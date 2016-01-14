from thread import start_new_thread, allocate_lock
import time

class _Thread_return_stop_holder: pass

def timeout_2s_catch(self, *args, **keyw):
    """
    This function implements 2 second timeout advice
    that catches exceptions raised by the thread.
    The advice equals to the one you get by
    a = create_timeout_advice( 2.0, 1 )
    """

    # Initialise tflock that is locked until thread
    # finishes execution
    tflock = allocate_lock()
    tflock.acquire()
    
    ret = _Thread_return_stop_holder()
    ret.value = None
    
    def save_retval( ret ):
        try: ret.value = self.__proceed(*args, **keyw)
        except: pass
        tflock.release()

    start_new_thread( save_retval, (ret,) )
    
    if _wait_timeout( 2.0, tflock ):
        return None

    return ret.value


_num_of_advices = 0

def create_timeout_advice( timeout = 1.0, catch_exceptions = 1 ):
    global _num_of_advices
    _num_of_advices = _num_of_advices + 1
    py = "def timeout_advice" + str( _num_of_advices ) + \
         "(self, *args, **keyw):\n" + \
         "    tflock = allocate_lock()\n" + \
         "    tflock.acquire()\n" + \
         "    ret = _Thread_return_stop_holder()\n" + \
         "    ret.value = None\n" + \
         "    def save_retval( ret ):\n"
    if catch_exceptions:
        py = py + "        try: ret.value = self.__proceed(*args,**keyw)\n" + \
                  "        except: pass\n"
    else:
        py = py + "        ret.value = self.__proceed(*args,**keyw)\n"
    py = py + "        tflock.release()\n" + \
         "    start_new_thread( save_retval, (ret,) )\n" + \
         "    if _wait_timeout( "+str(timeout)+", tflock):\n" + \
         "        return None\n" + \
         "    return ret.value\n"
    return _create_function( py, "timeout_advice"+str(_num_of_advices) )


def _create_function( function_code, function_name ):
    # compile code
    codeobj = compile( function_code, "", "exec" )
    # execute code, new function is added to local name space
    exec( codeobj )
    return eval( function_name )

def _wait_timeout( max_time, lock ):
    """
    Return 1 if lock is not released before max_time
    seconds have elapsed.
    """
    start_time = time.time()
    while time.time() - start_time < max_time:
        time.sleep( 0.01 )
        if lock.acquire(0):
            return 0
    return 1
