#
# Copyright (C) 2004  Antti Kervinen
#
#
# Changes:
# 2006-05-05 Pedro Emanuel de Castro Faria Salgado
#    - added a new method (x)
#    - added examples
#
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#

from aspects import wrap_around
from typecheck_advice import argtypecheck

class b:
    pass
class d(b):
    pass

class c:
    def m(self,integer,string):
        print "c.m called with",integer,string
    def n(self,object):
        print "c.n called with object",object
    def x(self, arg1, opt1=None, opt2=None):
        print "c.x called with ", arg1, opt1, opt2

c.__argtypes={
    'm':[[int,long],[str]],
    'n':[[b]],
    'x':[[int], [int, type(None)], [int, type(None)]]
}

wrap_around(c.m,argtypecheck)
wrap_around(c.n,argtypecheck)
wrap_around(c.x,argtypecheck)

o=c()
o.m(2L,"a")
o.n( d() )
o.x(1)
o.x(1, 2)
o.x(1, 2, 3)
o.x(1, opt2=3)
