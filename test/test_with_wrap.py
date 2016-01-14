"""
This is a wrapper to the real generator advice unit test. The tests
cannot be run without Python 2.5 or later.
"""

import sys
_python_version=sys.version_info[:2]

if _python_version < (2,5):
    print "SKIP","Python 2.5 or later required, you have",_python_version
    sys.exit(127)

import testlib_with_wrap

