# Find FindBin

A script I wrote to track down a bug I believed was being caused by 
[FindBin](http://search.cpan.org/~nwclark/perl-5.8.7/lib/FindBin.pm). (It
turns out this was not the case, but it at least allowed me to eliminate it as
a possibility.) From the FindBin Known Issues:

> If there are two modules using FindBin from different directories under the
> same interpreter, this won't work. Since FindBin uses a BEGIN block, it'll
> be executed only once, and only the first caller will get it right.

This script allows you to provide a path to a script to check and a list of
library paths (for module look ups). It then iterates through all the modules
looking for uses of FindBin and reports them back to the user.

## Usage

    $ find_find_bins.py path/to/script.pl --libs /path/to/lib/1 --libs
        /path/to/lib/2

## Copyright

Released under the GPL 3.0. See LICENSE.
