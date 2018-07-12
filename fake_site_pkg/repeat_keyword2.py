''' repeat_keyword2 is almost identical to repeat_keyword except that
it converts the argument of range() into an int, thus making it compatible
with fractional_arithmetic.
'''

from io import StringIO
import tokenize


def transform_source(text):
    '''Replaces instances of

        repeat n:
    by

        for __VAR_i in range(int(n)):

    where __VAR_i is a string that does not appear elsewhere
    in the code sample.
    '''

    loop_keyword = 'repeat'

    nb = text.count(loop_keyword)
    if nb == 0:
        return text

    var_names = get_unique_variable_names(text, nb)

    toks = tokenize.generate_tokens(StringIO(text).readline)
    result = []
    replacing_keyword = False
    for toktype, tokvalue, _, _, _ in toks:
        if toktype == tokenize.NAME and tokvalue == loop_keyword:
            result.extend([
                (tokenize.NAME, 'for'),
                (tokenize.NAME, var_names.pop()),
                (tokenize.NAME, 'in'),
                (tokenize.NAME, 'range'),
                (tokenize.OP, '('),
                (tokenize.NAME, 'int'),
                (tokenize.OP, '(')
            ])
            replacing_keyword = True
        elif replacing_keyword and tokvalue == ':':
            result.extend([
                (tokenize.OP, ')'),
                (tokenize.OP, ')'),
                (tokenize.OP, ':')
            ])
            replacing_keyword = False
        else:
            result.append((toktype, tokvalue))
    return tokenize.untokenize(result)


ALL_NAMES = []

def get_unique_variable_names(text, nb):
    '''returns a list of possible variables names that
       are not found in the original text.'''
    base_name = '__VAR_'
    var_names = []
    i = 0
    j = 0
    while j < nb:
        tentative_name = base_name + str(i)
        if text.count(tentative_name) == 0 and tentative_name not in ALL_NAMES:
            var_names.append(tentative_name)
            ALL_NAMES.append(tentative_name)
            j += 1
        i += 1
    return var_names

if __name__ == '__main__':
    sample = '''# comment with repeat in it
repeat 3:  # first loop
    print('__VAR_1')
    repeat (2*2):
        pass'''

    comparison = '''# comment with repeat in it
for __VAR_3 in range (3 ):# first loop
    print ('__VAR_1')
    for __VAR_2 in range ((2 *2 )):
        pass '''

    transformed = transform_source(sample)
    if comparison == transformed:
        print("Transformation done correctly")
    else:
        print("Transformation done incorrectly")
        import difflib
        d = difflib.Differ()
        diff = d.compare(comparison.splitlines(), transformed.splitlines())
        print('\n'.join(diff))