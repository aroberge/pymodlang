"""A custom importer making use of the import hook capability
"""

import os.path
import sys

import importlib
from importlib.abc import Loader, MetaPathFinder
from importlib.util import spec_from_file_location

from . import transforms


MAIN_MODULE_NAME = None
FILE_EXT = "notpy"


def import_main(name):
    """Imports the module that is to be interpreted as the main module.

       pyextensions is often invoked with a script meant to be run as the
       main module its source is transformed.  The invocation will be

       python -m pyextensions [trans1 trans2 ...] main_script

       Python identifies pyextensions as the main script; we artificially
       change this so that "main_script" is properly identified as such.
    """
    global MAIN_MODULE_NAME
    MAIN_MODULE_NAME = name
    return importlib.import_module(name)


class ExtensionMetaFinder(MetaPathFinder):
    """A custom finder to locate modules.  The main reason for this code
       is to ensure that our custom loader, which does the code transformations,
       is used."""

    def find_spec(self, fullname, path, target=None):
        """finds the appropriate properties (spec) of a module, and sets
           its loader."""
        if not path:
            path = [os.getcwd()]
        if "." in fullname:
            name = fullname.split(".")[-1]
        else:
            name = fullname
        for entry in path:
            if os.path.isdir(os.path.join(entry, name)):
                # this module has child modules
                filename = os.path.join(entry, name, "__init__.py")
                submodule_locations = [os.path.join(entry, name)]
            else:
                filename = os.path.join(entry, name + "." + FILE_EXT)
                submodule_locations = None
            if not os.path.exists(filename):
                continue

            return spec_from_file_location(
                fullname,
                filename,
                loader=ExtensionLoader(filename),
                submodule_search_locations=submodule_locations,
            )
        return None  # we don't know how to import this


sys.meta_path.insert(0, ExtensionMetaFinder())


class ExtensionLoader(Loader):
    """A custom loader which will transform the source prior to its execution"""

    def __init__(self, filename):
        self.filename = filename

    def create_module(self, spec):
        return None  # use default module creation semantics

    def exec_module(self, module):
        """import the source code, transforma it before executing it so that
           it is known to Python."""
        global MAIN_MODULE_NAME
        if module.__name__ == MAIN_MODULE_NAME:
            module.__name__ = "__main__"
            MAIN_MODULE_NAME = None

        with open(self.filename) as f:
            source = f.read()

        if transforms.transformers:
            source = transforms.transform(source)
        else:
            for line in source.split("\n"):
                if line.startswith("#ext "):
                    ## transforms.transform will extract all such relevant
                    ## lines and add them all relevant transformers
                    source = transforms.transform(source)
                    break
        exec(source, vars(module))

    def get_code(self, _):
        """Hack to silence an error when running pyextensions as main script."""
        return compile("None", "<string>", "eval")
