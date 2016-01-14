def tracer_advice( self, *args, **keyw ):
    stack_entry = self.__proceed_stack()[-1]
    print "Call:", stack_entry.name,  \
          "by an instance of", stack_entry.method.im_class
    return self.__proceed( *args, **keyw )
