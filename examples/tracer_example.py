from aspects import wrap_around
from tracer_advice import tracer_advice

class B1:
    def foo(self):
        print "B1.foo"

class B2:
    def foo(self):
        print "B2.foo"
    def bar(self):
        print "B2.bar"

class B3:
    def bar(self):
        print "B3.bar"

class D1(B1,B2):
    pass

class DD1(D1,B3):
    pass

wrap_around( B1.foo, tracer_advice )
wrap_around( B2.foo, tracer_advice )

wrap_around( B2.bar, tracer_advice )
wrap_around( B3.bar, tracer_advice )
wrap_around( DD1.bar, tracer_advice )

o = DD1()
o.foo()
o.bar()
