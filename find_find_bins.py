#!/usr/bin/env python

from __future__ import print_function

import re
import os
import sys
import argparse

# This is not perfect. It does not recognise whether inside POD or a
# multi-line string.
INCLUDE_RE = re.compile(r"""
    ^\s*use\s*          # Look behind for 'use' at the start of a line
    ([a-zA-Z0-9:]+)     # Name of module - letters, numbers, colons
""", re.VERBOSE | re.MULTILINE)

def some(f, seq):
    """Returns the first result of apply f to an element of seq for which the
    result is not false (in the loose Python sense).

    >>> some(lambda x: x % 2, [2, 4, 6, 3, 8, 9])
    1
    """
    for x in seq:
        fx = f(x)
        if fx:
            return fx
    return None

def flatten(l, ltypes=(list, tuple)):
    """Flattens a multi-dimensional sequence.

    Taken from http://rightfootin.blogspot.co.uk/2006/09/more-on-python-flatten.html.

    >>> flatten([1, 2, 3, 4])
    [1, 2, 3, 4]
    >>> flatten([1, [2, 3], 4, [5, [6], 7]])
    [1, 2, 3, 4, 5, 6, 7]
    """
    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i + 1] = l[i]
        i += 1
    return ltype(l)

def extract_includes(script):
    """Given a string representing Perl code, returns a set of module names
    for all included modules.

    >>> extract_includes("use Acme::Bleach")
    ['Acme::Bleach']
    """
    return [match.group(1) for match in INCLUDE_RE.finditer(script)]
    
def module_path(module_name, paths):
    """Given a Perl module name, returns the full path to the module (using
    the paths for parent directories) if it is available. Returns None
    otherwise.
    """
    components = module_name.split("::")
    components[-1] += ".pm"
    
    def find_module_in_path(path):
        full_path = os.path.join(path, *components)
        if os.path.isfile(full_path):
            return full_path
        return None

    return some(find_module_in_path, paths)

def find_bins(path, paths, on_broken_include=lambda x: x, processed=set(), broken_seen=set()):
    """Given the path to a Perl script and a list of paths in which to search
    for lbiraries, returns a list of all files used by the script that use
    FindBin.

    To intelligently deal with broken module includes, pass to
    on_broken_include a function that takes one parameter (the name of the
    broken module). You can then use this to throw an error or report the
    problem.
    """
#    print("Reading {}".format(path))
    processed.add(path)
    
    script = open(path, "r").read()
    includes = extract_includes(script)

    has_find_bin = any(include == "FindBin" for include in includes)

    includes = [(include, module_path(include, paths)) for include in includes]
    broken_includes = set(include[0] for include in includes if include[1] is \
                           None) - broken_seen
    map(on_broken_include, broken_includes)
    broken_seen.update(broken_includes)
    
    include_paths = set(include[1] for include in includes if include[1] is not \
                         None) - processed

    return ([path] if has_find_bin else []) + \
        flatten([find_bins(p, paths, on_broken_include, processed, broken_seen) for \
                    p in include_paths])

def main():
    parser = argparse.ArgumentParser(description="Finds instances of FindBin")
    parser.add_argument("--run_tests", action="store_true", help="Run the " + \
                            "module's tests.")
    parser.add_argument("--libs", action="append", help="Add a " + \
                            "module library path.")
    parser.add_argument("path", help="Path to script")
    args = parser.parse_args()

    if args.run_tests:
        import doctest
        doctest.testmod()
    else:
        def report_broken_module(module_name):
            print("Unable to locate {}".format(module_name), file=sys.stderr)
        files = set(find_bins(args.path, args.libs, report_broken_module))
        if not files:
            print("No script uses FindBin")
        else:
            files.remove(args.path)
            if not files:
                print("Only parent script contains FindBin")
            else:
                print("Following files contain FindBin:")
                for f in files:
                    print("\t{}".format(f))

if __name__ == '__main__':
    main()
