'''
In the following explanation, when we mention "the console" we refer to
a session using the pyextensions interactive console included in this package.

Possible invocations of this module:

1. python -m pyextensions: we want to start the console
2. python -m pyextensions script: we want to run "script" as the main program
                                but do not want to start the console
3. python -i -m pyextensions script: we want to run "script" as the main program
                                and we do want to start the console after
                                script has ended
4. python -m pyextensions trans1 trans2 script: we want to run "script" as the
                                main program, after registering the
                                tansformers "trans1" and "trans2";
                                we do not want to start the console
5. python -i -m pyextensions trans1 trans2 script: same as 4 except that we
                                want to start the console when script ends

Note that a console is started in all cases except 4 above.
'''
import sys
import os.path

# It is assumed that code transformers are third-party modules
# to be installed in a location from where they can be imported.
# For this proof of concept, we add a fake site-packages directory
# where the sample transformers will be located

top_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
fake_site_pkg = os.path.join(top_dir, "fake_site_pkg")

if not os.path.exists(fake_site_pkg):
    raise NotImplementedError(
        "A fake_site_pkg directory must exist for this demo to work correctly."
    )
sys.path.insert(0, fake_site_pkg)


from . import console, import_hook, transforms
start_console = console.start_console


if "-m" in sys.argv:
    if len(sys.argv) > 1:
        for i in range(1, len(sys.argv)-1):
            transforms.import_transformer(sys.argv[i])

        main_module = import_hook.import_main(sys.argv[-1])

        if sys.flags.interactive:
            main_dict = {}
            for var in dir(main_module):
                if var in ["__cached__", "__loader__",
                           "__package__", "__spec__"]:
                    continue
                main_dict[var] = getattr(main_module, var)
            start_console(main_dict)
    else:
        start_console()