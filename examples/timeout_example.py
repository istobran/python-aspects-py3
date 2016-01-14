import aspects
import timeout_advice
import time

class Example:
    def __init__( self ):
        self.all_waits = 0

    def wait( self, time_to_wait, throw_exception = 0 ):
        myname = "Example.wait("+str(time_to_wait)+","+str(throw_exception)+")"
        print myname, "falls sleep."

        time.sleep( time_to_wait )
        self.all_waits = self.all_waits + time_to_wait 

        if throw_exception:
            print "Suddenly", myname, "raises exception"
            raise myname
        else:
            print myname, "wakes up. Total sleep:",self.all_waits
            return self.all_waits


e = Example()
adv = timeout_advice.create_timeout_advice( timeout=1.0, catch_exceptions=1 )
aspects.wrap_around( Example.wait, adv )

t = time.time()
print e.wait( time_to_wait=1.6, throw_exception=1 )
print e.wait(0.2)
print e.wait(0.3)
print e.wait(0.4)
print time.time()-t
