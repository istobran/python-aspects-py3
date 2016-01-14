#!/usr/bin/env python

PASS,FAIL="PASS","FAIL"

import thread
import time

test,verdict="importing aspects library",FAIL
try:
    import aspects
    verdict=PASS
finally: print verdict,test

test,verdict="checking version_info",FAIL
try:
    if aspects.version_info==(1,3):
        verdict=PASS
    test+=", returned: %s" % str(aspects.version_info)
finally: print verdict,test

# Some test data
class C:
    def __foo0(self,num): return num
    def foo1(self,num): return self.__foo0(num)+1        
    def foo2(self,num): return self.__foo0(num)+2
    def bar1(self,num): return self.__foo0(num)+4

def adv1(self,*args):
    return self.__proceed(args[0]+100)

def adv2(self,*args,**keyw):
    return self.__proceed(keyw['num']+400)

o=C()

test,verdict="using wrap_count when no wraps",FAIL
try:
    if aspects.wrap_count(C.foo1)==0: verdict=PASS
finally: print verdict,test


test,verdict="wrap_around a public method, keyword argument",FAIL
try:
    n=aspects.wrap_around(C.foo1,adv2)
    if o.foo1(num=0)==401 and n==0: verdict=PASS
finally: print verdict,test


test,verdict="using wrap_count when one wrap",FAIL
try:
    if aspects.wrap_count(C.foo1)==1: verdict=PASS
    else: print "wrap_count returned",aspects.wrap_count(C.foo1)
finally: print verdict,test


test,verdict="wrap_around a private method (called by a public method)",FAIL
try:
    aspects.wrap_around(C._C__foo0,adv1)
    if o.foo1(num=0)==501: verdict=PASS
finally: print verdict,test

test,verdict="using wrap_count on private method",FAIL
try:
    if aspects.wrap_count(C._C__foo0)==1: verdict=PASS
finally: print verdict,test

test,verdict="peel_around clear advices",FAIL
try:
    try:
        aspects.peel_around(C.foo1)
        aspects.peel_around(C._C__foo0)
        if o.foo1(num=0)==1: verdict=PASS
    except: pass
finally: print verdict,test

test,verdict="using wrap_count on peeled methods",FAIL
try:
    if aspects.wrap_count(C.foo1)==0 and \
       aspects.wrap_count(C._C__foo0)==0: verdict=PASS
finally: print verdict,test

test,verdict="wrap_around_re, wrap_around, normal arguments",FAIL
try:
    aspects.wrap_around_re(C,'foo[0-9]',adv1)
    if o.foo1(0)==101 and o.foo2(0)==102: verdict=PASS
finally: print verdict,test

test,verdict="peel_around 1/2: remove advice",FAIL
try:
    peel=aspects.peel_around(C.foo1) # peel=adv1
    if o.foo1(0)==1: verdict=PASS
finally: print verdict,test

test,verdict="peel_around 2/2: rewrap peeled method. One method wrapped twice.",FAIL
try:
    aspects.wrap_around_re(C,'.*',peel) # peel=adv1
    if o.foo1(0)==201 and o.foo2(0)==302 and o.bar1(0)==204: verdict=PASS
finally: print verdict,test

test,verdict="keyword arguments, two different wraps on one method",FAIL
try:
    surface_wrapnum=aspects.wrap_around(C.bar1,adv2)
    # bar1 is has now wraps adv2/adv1, it calls _foo0 which has wrap adv1
    if o.bar1(num=8)==612: verdict=PASS
finally: print verdict,test

test,verdict="using wrap_count when two wraps",FAIL
try:
    if aspects.wrap_count(C.bar1)==2: verdict=PASS
    else: print aspects.wrap_count(C.bar1)
finally: print verdict,test

test,verdict="disabling the deeper wrap",FAIL
try:
    aspects.disable_wrap(C.bar1,0) # adv1 disabled
    if o.bar1(num=8)==512: verdict=PASS
finally: print verdict,test

test,verdict="testing wrap_is_enabled",FAIL
try:
    if aspects.wrap_is_enabled(C.bar1,0)==0 and \
       aspects.wrap_is_enabled(C.bar1,surface_wrapnum)==1: verdict=PASS
finally: print verdict,test

test,verdict="disabling the shallower wrap",FAIL
try:
    aspects.disable_wrap(C.bar1,surface_wrapnum) # adv2 disabled
    if o.bar1(8)==112: verdict=PASS
finally: print verdict,test

test,verdict="enabling all wraps",FAIL
try:
    for i in range(aspects.wrap_count(C.bar1)):
        aspects.enable_wrap(C.bar1,i)
    if o.bar1(num=8)==612: verdict=PASS
finally: print verdict,test

test,verdict="enabling, disabling and testing non-existing wraps",FAIL
try:
    try: aspects.disable_wrap(C.bar1,42)
    except aspects.AspectsException:
        try: aspects.disable_wrap(C.bar1,-1)
        except aspects.AspectsException:
            try: aspects.wrap_is_enabled(C.bar1,55)
            except aspects.AspectsException:
                verdict=PASS
finally: print verdict,test

test,verdict="wrap methods of certain instances",FAIL
try:
    class D:
        def addone(self,x):
            self.y=x+1
            return self.y
        def const(self):
            return 42
    def extra(self,x):
        return self.__proceed(x+1)+1
    o1,o2,o3=D(),D(),D()
    aspects.wrap_around(D.addone,extra,instances=[o1,o2])
    retvals=[o1.addone(0), o2.addone(0), o3.addone(0)]
    if o1.const()==42 and o1.y==o2.y==2 and o3.y==1 and \
       retvals==[3,3,1]: verdict=PASS
finally: print verdict,test

test,verdict="wrapping bound methods of certain instances",FAIL
try:
    class D:
        def addone(self,x):
            self.y=x+1
            return self.y
        def const(self):
            return 42
    def extra_noarg(self):
        return self.__proceed()+1
    o1,o2,o3=D(),D(),D()
    aspects.wrap_around(o1.const,extra_noarg,instances=[o2,o3])
    retvals=[o1.const(), o2.const(), o3.const()]
    if o1.addone(0)==1 and o2.addone(0)==1 and \
       retvals==[42,43,43]: verdict=PASS
finally: print verdict,test

test,verdict="threads use separate proceed stacks",FAIL
try:
    # If all __proceed uses the same stack in all threads,
    # self.__proceed() in function aa calls method b, although it
    # should call method a, because aa is wrapped around it.
    class T:
        def a(self):
            self.last_called="a"
        def b(self):
            self.last_called="b"
    def aa(self):
        time.sleep(0.2)
        self.__proceed()
    def bb(self):
        time.sleep(0.2)
        self.__proceed()
    aspects.wrap_around(T.a,aa)
    aspects.wrap_around(T.b,bb)
    o=T()
    thread.start_new_thread(o.a,())
    time.sleep(0.1)
    thread.start_new_thread(o.b,())
    time.sleep(0.4)
    if o.last_called=="b": verdict=PASS    
finally: print verdict,test

