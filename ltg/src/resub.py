#!/usr/bin/env python2.7
'''resub.py: an interface to re.sub() function, for when you need to substitute
some text somewhere but don't want to use sed.

Usage: resub.py <flags> <pattern> <replacement> [files] Use `resub.py -h` For
detailed help.  '''
import argparse
import re
import operator
from contextlib import contextmanager, closing
import os
import os.path as os_path
import sys
import tempfile
import glob
#from pipes import quote

def map_many(f, lst):
    """A monadic bind :)"""
    return [r for i in lst for r in f(i)]

def parse_args(args=None):
    re_double_break = re.compile('\s*\n\s*\n\s*')
    class CustomHelpFormatter(argparse.HelpFormatter):
        '''Supports multiline descriptions'''
        def add_text(self, text):
            if text is None: return
            paragraphs = (s.strip() for s in re_double_break.split(text))
            super = argparse.HelpFormatter.add_text
            for s in paragraphs:
                if s:
                    super(self, s)

    parser = argparse.ArgumentParser(description='Apply re.sub() to input stream or files.',
                                     formatter_class=CustomHelpFormatter)
    parser.epilog = r'''
Notes:

When invoking from sh-like shells you would want to enclose pattern and
replacement in single quotes to preserve escapes, then you can embed single
quotes as `'\''` (end quotation, escaped quote, begin quotation).

re.MULTILINE flag is implied, i.e. ^ and $ match the beginning and end of each
line, use --multiline and \A and \Z to match the beginning and end of the
entire input.

On line processing in general: unless --multiline is used,  all input lines are
stripped of trailing \n, all output lines have \n appended. As a result it is
not possible to delete or concatenate lines, but it is possible to add lines.
Also, the proper terminating EOL is added to output if not present.  '''

    parser.add_argument('pattern',
                       help='search pattern')
    parser.add_argument('replacement',
                       help='replacement template (use \\g<0>, \\g<1>, etc to refer to capture groups)')
    parser.add_argument('files', metavar='file', type=str, nargs='*',
                       help='input files (use stdin if none specified)')

    # re flags (re.M is implied)
    parser.add_argument('-I', '--ignorecase', dest='re_flags', action='append_const',
                        const=re.I,
                        help='add re.I to flags: perform case-insensitive matching.')

    parser.add_argument('-L', '--locale', dest='re_flags', action='append_const',
                        const=re.L,
                        help=r'''add re.L to flags: make \w, \W, \b, \B, \s and \S 
                        dependent on the current locale.''')

    parser.add_argument('-S', '--dotall', dest='re_flags', action='append_const',
                        const=re.S,
                        help='''add re.S to flags: make the \'.\' special character 
                        match any character at all, including a newline. *Does not* imply --multiline.''')

    parser.add_argument('-U', '--unicode', dest='re_flags', action='append_const',
                        const=re.U,
                        help=r'''add re.U to flags: make \w, \W, \b, \B, \d, \D, \s and \S dependent 
                        on the Unicode character properties database.''')

    parser.add_argument('-X', '--verbose', dest='re_flags', action='append_const',
                        const=re.X,
                        help='''add re.X to flags: ignore unescaped whitespace within a pattern, 
                        allow '#' comments.''')

    # sed-like arguments
    
    # OK, so I have four distinct scenarious in mind:
    #
    # 1) stdin > stdout, files > stdout: print results, report progress on stderr.
    # 2) --preview: print a diff of changes to stdout. Compatible with stdin > stdout.
    #        report progress on stdout in-stream.
    # 3) --inplace: apply changes inplace, report progress on stdout. 

    parser.add_argument('-p', '--preview', dest='preview', action='store_true',
                        help='''print diff of changes.''')
    
    parser.add_argument('-i', '--in-place', dest='in_place', action='store_true',
                        help='''apply changes in-place.''')

    # I don't use -i with optional extension because it then greedily consumes
    # the next argument, `-i pattern replacement *.txt` gets interpreted wrong,
    # `-i= pattern ...` has to be used. Sed doesn't have this problem as it
    # accepts only `-iext` or '--in-place=ext'.
    parser.add_argument('-b', '--backup-extension', dest='backup_extension',
                        metavar='EXT',
                        help='''Create backups with specified extension, implies --in-place''')

    parser.add_argument('-m', '--multiline', dest='multiline', action='store_true',
                        help='''Load the entire file so that multiline matching could be performed.''')
    # at some point I might make it use mmap instead of loading the entire file, when beneficial.

    parser.add_argument('-u', '--unbuffered', dest='unbuffered', action='store_true',
                        help='''output results as soon as possible.''')

    parser.add_argument('-n', '--no-matches', dest='no_matches', action='store_true',
                        help='''report files with no matches.''')

    parser.set_defaults(re_flags=[re.M])

    args = parser.parse_args(args)

    args.re_flags = reduce(operator.__or__, args.re_flags)
    args.in_place |= bool(args.backup_extension)
    args.rx = re.compile(args.pattern, args.re_flags)
    if os.name == 'nt':
        def expander(s):
            lst = glob.glob(s)
            assert len(lst), 'Pattern or file name {0!r} didn\'t match any files'.format(s)
            lst = filter(os_path.isfile, lst)
            assert len(lst), 'Pattern or file name {0!r} match only directories'.format(s)
            return lst
        args.files = map_many(expander, args.files)
    else:
        def expander(s):
            assert os_path.exists(s), 'File {0!r} doesn\'t exist'.format(s)
            if not os_path.isfile(s): return []
            return [s]
        if len(args.files):
            args.files = map_many(expander, args.files)
            assert len(args.files), 'Pattern or file names match only directories'
    
    args.read_stdin = not len(args.files)

    if args.preview and args.in_place:
        parser.error('--preview is incompatible with --in-place.')
    if args.preview and args.multiline:
        # for now...
        parser.error('--preview is incompatible with --multiline.')
    if args.in_place and args.read_stdin:
        parser.error('--in-place is incompatible with reading from stdin.')
    return args

def process_file_preview(input, fname, output, msg_output, args):
    rx, replacement, unbuffered = args.rx, args.replacement, args.unbuffered
    # Formats:
    # * no matches -- empty output
    # * no matches -- 'fname (0 substitutions)' (if args.no_matches and no substitutions) 
    # * 'fname\n', 'replacement\n'.., '(n substitutions)'
    fname_printed = False
    substitutions = 0
    line = 0
    while True:
        s = input.readline()
        if not s: break
        line += 1
        s = s.rstrip('\n')
        r, tmp = rx.subn(replacement, s)
        if s == r: continue # ignore ineffectual substitutions
        substitutions += tmp
        if tmp:
            if not fname_printed:
                if fname: output.write(fname + '\n')
                fname_printed = True
            # properly format result even if it has newlines
            rs = r.split('\n') 
            output.write('line {0}:\n- {1}\n'.format(line, s))
            for it in rs:
                output.write('+ {0}\n'.format(it))
            if unbuffered: output.flush()
    if substitutions:
        output.write('({0} substitutions)\n'.format(substitutions))
    elif args.no_matches:
        output.write('{0} ({1} substitutions)\n'.format(fname, substitutions))
    output.flush()
    return substitutions

def process_file_sequential(input, fname, output, msg_output, args):
    rx, replacement, unbuffered = args.rx, args.replacement, args.unbuffered
    substitutions = 0
    while True:
        s = input.readline()
        if not s: break
        s = s.rstrip('\n')
        r, tmp = rx.subn(replacement, s)
        if r != s:
            substitutions += tmp # ignore ineffectual substitutions 
        r += '\n'
        output.write(r)
        if unbuffered: output.flush()
    output.flush()
    if substitutions or args.no_matches:
        msg_output.flush()
        msg_output.write('{0} ({1} substitutions)\n'.format(fname, substitutions))
        msg_output.flush()
    return substitutions

def process_file_multiline(input, fname, output, msg_output, args):
    rx, replacement = args.rx, args.replacement
    s = input.read()
    r, n = rx.subn(replacement, s)
    # important: this requires the caller to not rename temporary file to
    # target file if no replacements were made. 
    if n or not args.in_place:
        output.write(r)
        if r and r[-1] != '\n': output.write('\n')
    if n or args.no_matches:
        msg_output.flush()
        msg_output.write('{0} ({1} substitutions)\n'.format(fname, n))
        msg_output.flush()
    return n

@contextmanager
def open_files(source_fname, args):
    modified_flag = [False]
    if source_fname is None:
        yield sys.stdin, sys.stdout, modified_flag
        return
    with open(source_fname, 'r') as input:
        if not args.in_place:
            yield input, sys.stdout, modified_flag
            return
        source_fname = os_path.abspath(source_fname)
        tmp_fd, tmp_name = tempfile.mkstemp(dir=os_path.dirname(source_fname), text=True)
        try:
            with closing(os.fdopen(tmp_fd, 'w')) as output:
                yield input, output, modified_flag
        except IOError:
            os.remove(tmp_name)
            raise
    if not modified_flag[0]:
        # just delete the temporary file -- important, because the caller
        # might have left it empty in this case.
        os.remove(tmp_name)
        return
    # rename source to backup or delete
    if args.backup_extension:
        backup = source_fname + '.' + args.backup_extension
        # remove before rename is necessary on Windows
        if os_path.exists(backup):
            os.remove(backup)
        os.rename(source_fname, backup)
    if os_path.exists(source_fname):
        os.remove(source_fname)
    os.rename(tmp_name, source_fname)

def main(args=None):
    '''Note that we follow the argparse convention that args _do not_ include
    program name, unlike sys.argv.'''
    args = parse_args(args)
    if args.multiline:
        process_file_method = process_file_multiline
    elif args.preview:
        process_file_method = process_file_preview
    else:
        process_file_method = process_file_sequential

    def process_file(fname):
        if fname:
            assert os_path.isfile(fname)
            display_fname = fname
        else:
            display_fname = '<stdin>'
            
        if args.preview:
            msg_output = None # no output allowed, fail fast!
        elif args.in_place:
            msg_output = sys.stdout
        else:
            msg_output = sys.stderr
            
        with open_files(fname, args) as (input, output, modified_flag):
            n = process_file_method(input, display_fname, output, msg_output, args)
            modified_flag[0] = n != 0

    if len(args.files):
        for fname in args.files: process_file(fname)
    else:
        process_file(None)


if __name__ == '__main__':
    main()
