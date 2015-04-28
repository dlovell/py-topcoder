"""Functions to parse problem statement content from problem statement etrees
"""


def extract_problem_statement(etree):
    xpath_string0 = '//h3[text()="Problem Statement"]'
    xpath_string1 = '../../following-sibling::tr'
    h3 = etree.xpath(xpath_string0)[0]
    tr = h3.xpath(xpath_string1)[0]
    text = tr.text_content()
    return text


def extract_problem_definition(etree):

    FORMATTER = '//td[text()="{0}:"]'.format
    sibling_xpath_string = 'following-sibling::td'
    def get_text_for_field(field):
        td = etree.xpath(FORMATTER(field))[0]
        following_td = td.xpath(sibling_xpath_string)[0]
        text = following_td.text_content()
        return text

    FIELDS = ['Class', 'Method', 'Parameters', 'Method signature']
    def make_raw_dictionary():
        lookup = {
            field.lower(): get_text_for_field(field)
            for field in FIELDS
        }
        return lookup

    BLANK = ' '
    def clean_signature(parameters, signature):
        """Clean the function signature of types for use with python"""
        split = signature.split(BLANK)
        return_type, signature = split[0], BLANK.join(split[1:])
        parameters = parameters.split(', ')
        for parameter in parameters:
            signature = signature.replace(parameter + ' ', '')
        return return_type, signature

    def reprocess_lookup(lookup):
        """Operates in place"""
        signature = lookup.pop('method signature')
        parameters = lookup['parameters']
        return_type, signature = clean_signature(parameters, signature)
        lookup['signature'] = signature
        lookup['return_type'] = return_type
        return lookup

    lookup = make_raw_dictionary()
    lookup = reprocess_lookup(lookup)
    return lookup


def extract_problem_constraints(etree):
    pass


def extract_problem_examples(etree):

    REPLACEMENTS = [
        ('{', '['),
        ('}', ']'),
        ('Returns: ', '')
    ]
    xpath_formatter = '//tr//td[text()="{0})"]'.format
    xpath_string = '../following-sibling::tr[position()=1]'
    RETURNS = 'Returns'
    
    def extract_problem_example_pieces(etree, which_example):
        td = etree.xpath(xpath_formatter(which_example))[0]
        tr = td.xpath(xpath_string)[0]
        pieces = list(tr.itertext())[1:]
        return pieces

    def get_returns_index(pieces):
        has_returns = [i
                       for (i, piece) in enumerate(pieces)
                       if piece.find(RETURNS) != -1]
        assert len(has_returns) == 1
        return has_returns[0]

    def do_replace(string):
        for replacement in REPLACEMENTS:
            string = string.replace(*replacement)
        return string

    def extract_problem_example(etree, which_example):
        pieces = extract_problem_example_pieces(etree, which_example)
        returns_index = get_returns_index(pieces)
        pieces = pieces[:returns_index + 1]
        pieces = map(do_replace, pieces)
        pieces = map(eval, pieces)
        pieces = (pieces[:-1], pieces[-1])
        return pieces

    examples = []
    try:
        while True:
            which_example = len(examples)
            example = extract_problem_example(etree, which_example)
            examples.append(example)
    except Exception:
        pass
    return examples


PYTHON_TEXT_FORMATTER = \
"""
\"\"\"
{0}
\"\"\"


def {2}:
    pass


class {1}(object):
    @staticmethod
    def {2}:
        \"\"\"
        parameters: ({3})
        returns: ({4})
        \"\"\"
        return {2}


if __name__ == '__main__':
    input_outputs = [
        {6}
    ]
    for (input, expected_output) in input_outputs:
        output = {1}.{5}(*input)
        # FIXME: add check on correctness, only print expected if incorrect
        print '{1}.{5}({{0}}) = {{1}} (expected {{2}})'.format(input, output, expected_output)
        print
""".format
def get_python_text(etree):
    problem_statement = extract_problem_statement(etree).encode('utf-8')
    problem_statement = ''.join([x for x in problem_statement if ord(x) < 128])
    problem_definition = extract_problem_definition(etree)
    examples = extract_problem_examples(etree)
    text = PYTHON_TEXT_FORMATTER(problem_statement, problem_definition['class'],
        problem_definition['signature'], problem_definition['parameters'],
        problem_definition['return_type'], problem_definition['method'],
        ',\n        '.join(map(str, examples)),
        )
    return text
