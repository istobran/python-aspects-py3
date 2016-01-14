# Copyright (C) 2004-2007  Antti Kervinen
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301 USA

# Changes:
#
# -> aspects-0.3, added support for type checking keyword arguments

def argtypecheck(self,*args,**kwargs):
    """Check that the types of the arguments satisfy the specification
    given in class variable __argtypes. __argtype is a dictionary
    where method's name is a key to the list of allowed types of
    arguments of the method. This function should be wrapped around
    the methods whose argument types are checked."""

    method=self.__proceed_stack()[-1].method

    type_list=self.__argtypes[ method.__name__ ]

    # Check normal arguments. If the type of an argument is not
    # spesified in the type_list (there are more arguments than types
    # for them), any type is allowed.

    try:
        for i,arg in enumerate(args):
            if not True in [isinstance(arg,argt) for argt in type_list[i] ]:
                raise TypeError("The type of the "+str(i+1)+". argument of "+
                                self.__proceed_stack[-1].name+
                                " was "+str(type(arg))+
                                ". Allowed types are: "+
                                ", ".join([str(t) for t in type_list[i]])+
                                ".")
    except IndexError:
        pass # there were more arguments than specified types


    # Check keyword arguments. If the keyword is not mentioned in the
    # parameter list, or , allow any type.
    
    argnames=list(method.func_code.co_varnames[:method.func_code.co_argcount])
    for kwarg in kwargs:
        try:
            # -1 is because type of the first argument (self) is not
            # spesified in type_list'
            kwargnum=argnames.index(kwarg)-1
        except ValueError:
            continue # keyword kwarg does not appear in the argument list

        # skip type check if there is no type spec for this argument
        if kwargnum>=len(type_list): continue 

        if not True in [isinstance(kwargs[kwarg],kwargt) for kwargt in type_list[kwargnum]]:
            raise TypeError(
                "The type of the keyword argument '"+kwarg+"' was "+
                str(type(kwargs[kwarg]))+" when calling "+
                self.__proceed_stack[-1].name+
                ". Allowed types are: "+
                ", ".join([str(t) for t in type_list[kwargnum]])+
                ".")
            
    return self.__proceed(*args,**kwargs)
