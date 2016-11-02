"""Functions to request content from topcoder and extract match overview etrees
"""


import os
import re
import time
import random
import argparse
import datetime
import requests
import itertools
import lxml.html
#
import problem_statement as ps


LAST_REQUEST_TIME = time.time()
BASE_URL = 'http://community.topcoder.com'
def request_topcoder_relpath(relpath):
    """Perform an http 'GET' with a minimum wait since the last request """

    def ensure_interval(interval=.5):
        global LAST_REQUEST_TIME
        if time.time() - LAST_REQUEST_TIME < interval:
            mean=2.; N=10; max_duration=5
            duration = random.gammavariate(N, mean/N)
            duration = min(duration, max_duration)
            duration = max(duration, interval)
            time.sleep(duration)
        LAST_REQUEST_TIME = time.time()
        return

    ensure_interval()
    url = BASE_URL + relpath
    print('requesting {0} at {1}'.format(url, datetime.datetime.now()))
    response = requests.get(url)
    assert response.status_code == 200
    return response.text


def ensure_filepath(filepath):
    dirname, filename = os.path.split(filepath)
    if dirname:
        try:
            os.makedirs(dirname)
        except Exception:
            pass


def read_topcoder_relpath(relpath, dirname='./html'):
    """Return an lxml.html.HtmlElement given topcoder relpath

    Read from disk if present, else do http GET request and write to disk"""

    ensure_joinable = lambda path: path[1:] if path[0] == '/' else path
    filepath = os.path.join(dirname, ensure_joinable(relpath))
    if not os.path.isfile(filepath):
        ensure_filepath(filepath)
        text = request_topcoder_relpath(relpath)
        with open(filepath, 'w') as fh:
            fh.write(text)
    else:
        with open(filepath) as fh:
            text = fh.read()

    etree = lxml.html.fromstring(text)
    return etree


PROBLEM_STATEMENT = 'problem_statement'
ROUND_OVERVIEW = 'round_overview'
def get_relpaths(etree, _type):
    """Extract all relpaths (href strings) of a particular type """

    xpath_string = './/a[starts-with(@href, "/stat?c={0}")]'.format(_type)
    hrefs = etree.xpath(xpath_string)
    hrefs = [href.get('href') for href in hrefs]
    return hrefs


def read_problem_statement_lookup(overview_etree):
    """read a lookup of (division, level) -> problem statement etree

    using read_topcoder_relpath may cause a GET request
    """

    FORMATTER = '//b[text()="Division {0} Problem Stats"]//ancestor::table'.format
    MAPPING = {1: 'I', 2: 'II'}
    def extract_etree_tuples(division):
        xpath_string = FORMATTER(MAPPING[division])
        sub_etree = overview_etree.xpath(xpath_string)[-1]
        relpaths = get_relpaths(sub_etree, PROBLEM_STATEMENT)
        assert len(relpaths) == 3
        etrees = map(read_topcoder_relpath, relpaths)
        return list(((division, _i), _etree)
                    for (_i, _etree) in enumerate(etrees, 1))

    divisions = MAPPING.keys()
    from_iterable = itertools.chain.from_iterable
    chained = from_iterable(map(extract_etree_tuples, divisions))
    lookup = dict(chained)
    return lookup


def get_first_overview_relpath():
    MATCHLIST_RELPATH = '/tc?module=MatchList'
    etree = read_topcoder_relpath(MATCHLIST_RELPATH)
    relpath = get_relpaths(etree, ROUND_OVERVIEW)[0]
    return relpath


def get_overview_relpath_lookup(overview_etree=None):
    """Extract all match overview relpaths from a particular match overview relpath etree

    Can't use the topcoder matchlist relpath: limited to 200 matches per page
    """

    compiled_re = re.compile('Single Round Match (\d+)')
    def get_match_number(option):
        """Not all options are SRMs, return None if this is the case"""
        match = compiled_re.match(option.text)
        match_number = int(match.groups()[0]) if match else None
        return match_number

    if overview_etree is None:
        overview_etree = read_topcoder_relpath(get_first_overview_relpath())

    xpath_string = '//select[@name="Contest"]//option'
    options = overview_etree.xpath(xpath_string)
    overview_relpath_lookup = dict((get_match_number(option), option.get('value'))
                                 for option in options
                                 if get_match_number(option))
    return overview_relpath_lookup


DIRNAME = './scripts'
def write_problem_statement(overview_relpath_lookup,
                            match_number, divisions, levels,
                            dirname=DIRNAME):
    overview_relpath = overview_relpath_lookup[match_number]
    overview_etree = read_topcoder_relpath(overview_relpath)
    problem_statement_lookup = read_problem_statement_lookup(overview_etree)
    for (division, level) in itertools.product(divisions, levels):
        problem_statement_etree = problem_statement_lookup[(division, level)]
        text = ps.get_python_text(problem_statement_etree)
        formatter = 'SRM{0}_division{1}_level{2}.py'.format
        filename = formatter(match_number, division, level)
        filepath = os.path.join(dirname, filename)
        ensure_filepath(filepath)
        with open(filepath, 'w') as fh:
            fh.write(text)


def parse_args(override=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('match_number', type=int)
    parser.add_argument('--divisions', nargs='+', type=int)
    parser.add_argument('--levels', nargs='+', type=int)
    parser.add_argument('--dirname', type=str, default=DIRNAME)
    args = parser.parse_args(override)
    #
    args.divisions = args.divisions or range(1, 3)
    args.levels = args.levels or range(1, 4)
    #
    return args


if __name__ == '__main__':
    args = parse_args()
    overview_relpath_lookup = get_overview_relpath_lookup()
    write_problem_statement(overview_relpath_lookup,
                            args.match_number, args.divisions, args.levels,
                            args.dirname)
