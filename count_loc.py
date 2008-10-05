"""simple script that counts the lines of code
in the Globby package"""

import os
from os.path import abspath, join, dirname, pardir

def main(root, search):
    LOC = 0

    root = abspath(root)
    offset = len(root) + 1

    print '+%s+' % ('=' * 78)
    print '| Lines of Code %s |' % (' ' * 62)
    print '+%s+' % ('=' * 78)

    for folder in search:
        folder = join(root, folder)
        for root, dirs, files in os.walk(folder):
            for fn in files:
                fn = join(root, fn)
                if fn.endswith('.py'):
                    fp = open(fn)
                    try:
                        lines = sum(1 for l in fp.read().splitlines() if l.strip())
                    except:
                        print '%-70sskipped' % fn
                    else:
                        LOC += lines
                        print '| %-68s %7d |' % (fn[offset:], lines)
                    fp.close()

    print '+%s+' % ('-' * 78)
    print '| Total Lines of Code: %55d |' % LOC
    print '+%s+' % ('-' * 78)

if __name__ == '__main__':
    main(abspath(dirname(__file__)), ['nms'])
