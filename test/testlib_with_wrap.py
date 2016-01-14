PASS,FAIL="PASS","FAIL"
import aspects
import os

test,verdict = "wrap a module function inside very simple g_adv",FAIL
try:
    g_adv_executed=0
    def _test_mod_function(x):
        return x+42
    def g_adv(x):
        global g_adv_executed
        g_adv_executed=1
        yield aspects.proceed
    rv=aspects.with_wrap(g_adv,_test_mod_function)
    r=_test_mod_function(42)
    if rv==0 and r==84 and g_adv_executed: verdict=PASS
finally: print verdict,test

test,verdict = "change the arguments",FAIL
try:
    def __test_mod_function(x):
        return x+42
    def g_adv(x):
        yield aspects.proceed(x+1)
    aspects.with_wrap(g_adv,__test_mod_function)
    if __test_mod_function(0)==43: verdict=PASS
finally: print verdict,test

test,verdict = "change the return value",FAIL
try:
    def __test_mod_function(x):
        return x+42
    def g_adv(x):
        retval=yield aspects.proceed(x+1)
        yield aspects.return_stop(retval+10)
    aspects.with_wrap(g_adv,__test_mod_function)
    if __test_mod_function(0)==53: verdict=PASS
finally: print verdict,test

test,verdict = "reinvoking wrapped method",FAIL
try:
    argsum=0
    def __test_mod_function(x):
        global argsum
        argsum+=x
        return argsum
    def g_adv(x):
        yield aspects.proceed(1)
        yield aspects.proceed(1)
        yield aspects.proceed(1)
    aspects.with_wrap(g_adv,__test_mod_function)
    if __test_mod_function(0)==3: verdict=PASS
finally: print verdict,test

test,verdict = "non-yielding advice blocks the method call and returns None",FAIL
try:
    def __test_mod_function(x):
        return x+42
    def g_adv(x):
        if 1==0: yield aspects.proceed(15)
    aspects.with_wrap(g_adv,__test_mod_function)
    if __test_mod_function(0)==None: verdict=PASS
finally: print verdict,test


test,verdict = "unhandled exception passes through advice",FAIL
try:
    # Wrapped function throws exception that is not handled in
    # the wrap. It should be caught by the caller.
    def __test_mod_function(x):
        raise Exception("test exception")
    def g_adv(x):
        retval=yield aspects.proceed(x+1)
        yield aspects.return_stop(retval+10)
    aspects.with_wrap(g_adv,__test_mod_function)
    try: __test_mod_function(0)
    except Exception,e:
        if str(e)=="test exception": verdict=PASS
finally: print verdict,test

test,verdict = "advice catches an exception",FAIL
try:
    # Wrapped function throws exception but the wrap catches it and
    # sets new return value
    def __test_mod_function(x):
        raise Exception("test exception2")
    def g_adv(x):
        retval=0
        try:
            retval=yield aspects.proceed(x+1)
        except Exception, e:
            if str(e)=="test exception2":
                yield aspects.return_stop(retval+10)
    aspects.with_wrap(g_adv,__test_mod_function)
    if __test_mod_function(0)==10: verdict=PASS
finally: print verdict,test

test,verdict = "two advices on a method, new-style class",FAIL
try:
    class c(object):
        def sq(self,x=1):
            return x*x
    def g_adv1(self,x=3):
        retval=yield aspects.proceed
        yield aspects.return_stop(retval+1)
    def g_adv2(self,x=5):
        yield aspects.proceed(self,x=x)
    rv1=aspects.with_wrap(g_adv1,c.sq)
    rv2=aspects.with_wrap(g_adv2,c.sq)
    o=c()
    assert o.sq()==26, "o.sq()!=26"
    assert aspects.wrap_count(c.sq) == 2, "wrap_count fails!"
    
    verdict=PASS
finally: print verdict,test

test,verdict = "two advices on a function",FAIL
try:
    def sq(*args):
        return args
    def g_adv1(*args):
        yield aspects.proceed(*args+(1,))
    def g_adv2(*args):
        rv = yield aspects.proceed(*args+(2,))
        yield aspects.return_stop("-".join(str(s) for s in rv))
    rv1=aspects.with_wrap(g_adv1,sq)
    rv2=aspects.with_wrap(g_adv2,sq)
    if sq(0)=="0-2-1": verdict=PASS
    else: print sq(0)
finally: print verdict,test

test,verdict = "two advices and catching exceptions",FAIL
try:
    class c:
        def sq(self,x=2):
            return x*x
    def g_adv1(self,x=3):
        retval=yield aspects.proceed
        self.g_adv1_saw_rv=retval
    def g_adv2(self,x=5):
        try: yield aspects.proceed
        except Exception,e:
            self.g_adv2_saw_ex=e
            yield aspects.return_stop(11)
    aspects.with_wrap(g_adv1,c.sq)
    aspects.with_wrap(g_adv2,c.sq)
    o=c()
    if o.sq('a')!=11: raise Exception("o.sq('a')!=11")
    if not hasattr(o,'g_adv1_saw_rv') and type(o.g_adv2_saw_ex)==TypeError:
        verdict=PASS
finally: print verdict,test

test,verdict = "recursive function wrapped",FAIL
try:
    def fib(x):
        if x<2: return 1
        else: return fib(x-1)+fib(x-2)
    def g_adv(x):
        r = yield aspects.proceed(x)
        yield aspects.return_stop(r+1)
    aspects.with_wrap(g_adv,fib)
    if fib(4)==14: verdict=PASS
    else: print fib(4)
finally: print verdict,test

test,verdict = "wrap calls another wrapped method",FAIL
try:
    class c:
        def sq(self,x):
            return self.mul(x,x+1)
        def mul(self,x,y):
            # this multiplier has an off-by-one bug
            if y>=1: return x+self.mul(x,y-1)
            else: return x
    def g_adv_fixsq(self,x):
        yield aspects.return_stop(self.mul(x,x))
    def g_adv_fixmul(self,x,y):
        if y<1: yield aspects.return_stop(0)
        else: yield aspects.proceed
    rv1=aspects.with_wrap(g_adv_fixsq,c.sq)
    rv2=aspects.with_wrap(g_adv_fixmul,c.mul)
    o=c()
    if o.sq(5)==25: verdict=PASS
finally: print verdict,test

test,verdict = "advices with state",FAIL
try:
    def fun42(x): return x+42
    def fun32(x): return x+32
    def adv(x):
        args, kwargs = yield aspects.return_cont(22)
        x=args[0]
        yield aspects.proceed(x)
    # Note that calling different methods calls different instances of
    # the advice. Therefore, initially, fun42(1)==22 and fun32(1)==22
    # and not fun42(1)==22 and fun32(1)==33.
    aspects.with_wrap(adv,fun42,fun32)
    if fun42(1)==22 and fun42(1)==43 and fun42(1)==22 \
           and fun32(1)==22 and fun32(1)==33:
        verdict=PASS
    else: print fun42(1),fun32(1),fun32(1)
finally: print verdict,test

test,verdict = "enable_wrap, disable_wrap, wrap_is_enabled",FAIL
try:
    def succ(x):
        return x+1
    def add2(*a,**kw):
        rv = yield aspects.proceed
        yield aspects.return_stop(rv+2)
    def add4(*a,**kw):
        rv = yield aspects.proceed
        yield aspects.return_stop(rv+4)
    a2=aspects.with_wrap(add2,succ)
    a4=aspects.with_wrap(add4,succ)
    wis=aspects.wrap_is_enabled
    if wis(succ,a2)!=1 or wis(succ,a4)!=1: raise Exception("wis1")
    aspects.disable_wrap(succ,a4)
    if wis(succ,a2)!=1 or wis(succ,a4)!=0: raise Exception("wis2")
    if succ(0)!=3: raise Exception("succ(0)==%s!=3" % succ(0))
    aspects.disable_wrap(succ,a2)
    if wis(succ,a2)!=0 or wis(succ,a4)!=0: raise Exception("wis3")
    if succ(0)!=1: raise Exception("succ(0)==%s!=1" % succ(0))
    aspects.enable_wrap(succ,a4)
    if wis(succ,a2)!=0 or wis(succ,a4)!=1: raise Exception("wis4")
    if succ(0)!=5: raise Exception("succ(0)==%s!=5" % succ(0))
    aspects.enable_wrap(succ,a2)
    if wis(succ,a2)!=1 or wis(succ,a4)!=1: raise Exception("wis5")
    if succ(0)!=7: raise Exception("succ(0)==%s!=7" % succ(0))
    verdict=PASS
finally: print verdict,test

test,verdict = "instance-specific aspects",FAIL
try:
    class c:
        def foo(self): return 'foo'
        def bar(self): return 'bar'
    def adv1(self):
        yield aspects.return_stop('adv1')
    def adv2(self):
        yield aspects.return_stop('adv2')
    o1=c()
    o2=c()
    o3=c()
    aspects.with_wrap(adv1,c.foo,c.bar,instances=[o1])
    aspects.with_wrap(adv2,c.foo,instances=[o1,o2])
    if o3.foo()!='foo' or o3.bar()!='bar': raise Exception("o3")
    if o2.foo()!='adv2' or o2.bar()!='bar': raise Exception("o2")
    if o1.foo()!='adv2' or o1.bar()!='adv1': raise Exception("o1")
    verdict=PASS
finally: print verdict,test

test,verdict = "peel_around a function and a method",FAIL
try:
    def foo(x): return x+1
    class c:
        def foo(self,x): return x+2
    class newc(object):
        def foo(self,x): return x+3
    def adv(*a):
        yield aspects.return_stop(42)
    def adv2(*a):
        yield aspects.return_stop(52)
    aspects.with_wrap(adv,foo,c.foo,newc.foo)
    o=c()
    newo=newc()
    if not (foo(0)==o.foo(1)==newo.foo(2)==42):
        raise Exception("first wrapping failed already")
    aspects.with_wrap(adv2,foo,c.foo,newc.foo)
    if not (foo(0)==o.foo(1)==newo.foo(2)==52):
        raise Exception("second wrapping failed already")
    w1=aspects.peel_around(foo)
    w2=aspects.peel_around(c.foo)
    w3=aspects.peel_around(newc.foo)
    if not (foo(0)==o.foo(1)==newo.foo(2)==42):
        raise Exception("first peeling failed")
    aspects.peel_around(foo)
    aspects.peel_around(c.foo)
    aspects.peel_around(newc.foo)    
    if not (foo(0)==1 and o.foo(0)==2 and newo.foo(0)==3):
        raise Exception("second peeling failed")
    aspects.with_wrap(w1,foo)
    aspects.with_wrap(w2,c.foo)
    aspects.with_wrap(w3,newc.foo)
    if not (foo(0)==o.foo(1)==newo.foo(2)==52):
        raise Exception("peels could not be put back")
    verdict=PASS
finally: print verdict,test

test,verdict = "asking for a wrapped function",FAIL
try:
    def wf():
        pass
    def wrap(*a):
        wrapped_func = yield aspects.get_wrapped
        if wrapped_func.__name__=="wf":
            yield aspects.return_stop(PASS)
        else:
            yield aspects.return_stop(FAIL)
    aspects.with_wrap(wrap,wf)
    verdict=wf()
finally: print verdict,test


test,verdict = "wrapping a built-in operator",FAIL
try:
    import operator
    def offbyone(*a):
        real_output = yield aspects.proceed
        if type(real_output)==int:
            yield aspects.return_stop(real_output+1)
    aspects.with_wrap(offbyone, operator.add)
    if operator.add(1, 1) == 3:
        verdict = PASS
finally: print verdict,test

test,verdict = "wrapping a built-in function from the os library",FAIL
try:
    def w(*a):
        yield aspects.return_stop("WRAPPED %s" % (yield aspects.proceed))
    aspects.with_wrap(w, os.getcwd)
    if os.getcwd()[:8] == "WRAPPED ": 
        verdict = PASS
finally: print verdict,test

test,verdict = "without wrap: removing arbitrary wraps",FAIL
try:
    def wrapme(x): return "wrapme" + x
    def w1(x): yield aspects.proceed("w1" + x)
    def w2(x): yield aspects.proceed("w2" + x)
    def w3(x): yield aspects.proceed("w3" + x)
    def w4(x): yield aspects.proceed("w4" + x)

    for w in (w1, w2, w4, w3, w4): aspects.with_wrap(w, wrapme)
    # check that everything is fine
    assert wrapme("") == "wrapmew1w2w4w3w4", "preparation failed"
    
    # remove the topmost wrap
    aspects.without_wrap(w4, wrapme)
    assert wrapme("") == "wrapmew1w2w4w3", "topmost"

    # remove the wrap in the middle
    aspects.without_wrap(w4, wrapme)
    assert wrapme("") == "wrapmew1w2w3", "middle"
    
    # remove the wrap on the bottom
    aspects.without_wrap(w1, wrapme)
    assert wrapme("") == "wrapmew2w3", "bottom"

    # remove the rest wraps
    aspects.without_wrap(w2, wrapme)
    aspects.without_wrap(w3, wrapme)
    assert wrapme("") == "wrapme", "rest"

    # test removing by wrap id
    wid1 = aspects.with_wrap(w1, wrapme)
    wid2 = aspects.with_wrap(w2, wrapme)
    wid3 = aspects.with_wrap(w1, wrapme)
    wid4 = aspects.with_wrap(w3, wrapme)
    wid5 = aspects.with_wrap(w1, wrapme)
    wid6 = aspects.with_wrap(w4, wrapme)
    wid7 = aspects.with_wrap(w1, wrapme)
    assert wrapme("") == "wrapmew1w2w1w3w1w4w1", "preparation 2 failed"

    aspects.without_wrap(wid1, wrapme)
    aspects.without_wrap(wid7, wrapme)
    assert wrapme("") == "wrapmew2w1w3w1w4", "first and last removed"

    aspects.without_wrap(wid4, wrapme)
    assert wrapme("") == "wrapmew2w1w1w4", "middle removed"

    aspects.without_wrap(wid3, wrapme)
    aspects.without_wrap(wid2, wrapme)
    aspects.without_wrap(wid5, wrapme)
    assert wrapme("") == "wrapmew4", "one left"
    
    aspects.without_wrap(wid6, wrapme)
    assert wrapme("") == "wrapme", "all gone"
    
    verdict = PASS
finally: print verdict,test

test, verdict = "bound methods", FAIL
try:
    class co:
        def m_co(self):
            return self.x_co
    class do(co):
        def m_do(self):
            return self.m_co()
        def w_do(self_do, self_co, *args):
            rv = yield aspects.proceed
            yield aspects.return_stop(rv+1)
    o1 = do()
    o2 = do()
    o3 = co()
    aspects.with_wrap(o1.w_do, o1.m_co) # executes only when called through o1
    aspects.with_wrap(o1.w_do, do.m_co) # executes always
    o1.x_co = 1
    o2.x_co = 1
    o3.x_co = 1

    assert o1.m_do() == 3
    assert o2.m_do() == 2
    assert o3.m_co() == 1 # no wraps in the base class

    # Exactly the same, this time for new-style classes
    class co(object):
        def m_co(self):
            return self.x_co
    class do(co):
        def m_do(self):
            return self.m_co()
        def w_do(self_do, self_co, *args):
            rv = yield aspects.proceed
            yield aspects.return_stop(rv+1)
    o1 = do()
    o2 = do()
    o3 = co()
    aspects.with_wrap(o1.w_do, o1.m_co) # executes only when called through o1
    aspects.with_wrap(o1.w_do, do.m_co) # executes always
    o1.x_co = 5
    o2.x_co = 5
    o3.x_co = 5

    assert o1.m_do() == 7
    assert o2.m_do() == 6
    assert o3.m_co() == 5 # no wraps in the base class
    verdict = PASS
finally: print verdict, test

########################################################################
#
# TESTING ILLEGAL BEHAVIOUR
#
########################################################################

test,verdict = "without wrap: erroneous use",FAIL
try:
    def wrapme(x): return "wrapme" + x
    def wrapme2(x): return "wrapme2" + x
    def w1(x): yield aspects.proceed("w1" + x)
    def w2(x): yield aspects.proceed("w2" + x)
    def w3(): 
        rv = yield aspects.proceed
        yield aspects.return_stop("w3" + str(rv))
    w1id = aspects.with_wrap(w1, wrapme)
    w2id = aspects.with_wrap(w2, wrapme)

    # Try to remove a wrap from a non-wrapped function
    ok = 0
    try: aspects.without_wrap(w1, wrapme2)
    except aspects.AspectsException: ok = 1
    assert ok == 1, "unwrapping non-wrapped function"

    # Try to remove a wrap (wrap id) from a non-wrapped function
    ok = 0
    try: aspects.without_wrap(w1id, wrapme2)
    except aspects.AspectsException: ok = 1
    assert ok == 1, "unwrapping according to wrap_id non-wrapped function"

    w3id = aspects.with_wrap(w3, os.getpid)

    # Try to remove a wrap from a wrapped function
    ok = 0
    try: aspects.without_wrap(w3, wrapme)
    except aspects.AspectsException: ok = 1
    assert ok == 1, "unwrapping wrapped function"

    # Try to remove a wrap (wrap id) from a wrapped function
    ok = 0
    try: aspects.without_wrap(w1id, os.getpid)
    except aspects.AspectsException: ok = 1
    assert ok == 1, "unwrapping according to wrap_id a wrapped function"

    # Making sure that the wraps still work and clean them up
    assert os.getpid().startswith("w3"), "os.gitpid wrap does not work"
    assert wrapme("") == "wrapmew1w2", "wrapme wrap does not work"
    aspects.without_wrap(w2id, wrapme)
    aspects.without_wrap(w1, wrapme)
    aspects.without_wrap(w3id, os.getpid)
    assert int(os.getpid()) > 0, "os.gitpid could not be cleaned"
    assert wrapme("") == "wrapme", "wrapme could not be cleaned"
    
    verdict = PASS
finally: print verdict,test


test,verdict = "non-generator advice wrapped with with_wrap",FAIL
try:
    def __test_mod_function(x):
        return x+42
    def adv(x):
        return 144
    aspects.with_wrap(adv,__test_mod_function)
    try: __test_mod_function(0)
    except aspects.AspectsException:
        verdict=PASS
finally: print verdict,test

test,verdict = "returning and yielding without proceeding", FAIL
try:
    def fun1(x): return x
    def fun2(x): return x
    def return_early(x):
        aspects.return_stop
    def yield_early(x):
        aspects.return_cont
    aspects.with_wrap(return_early,fun1)
    aspects.with_wrap(yield_early,fun2)
    try: fun1(0)
    except aspects.AspectsException:
        try: fun2(0)
        except aspects.AspectsException:
            verdict=PASS
finally: print verdict,test
