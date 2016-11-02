MutaProps - Mutated properties for dead simple UIs
==================================================

Introduction to mutaprops comes here...


Class MutaProps
---------------

Class-scoped mutaprops are currently not supported.

Class mutaselects
-----------------

Class-scoped mutaselects are there to allow selects updated for all objects
of given class. The implementation and syntax is sligtly different from normal
selects, due to the fact that it's impossible to override some default Python
behaviours to mimick class-based properties without changing Abstract Base Class
of the original decorated class.

The classes to which the class-scoped mutaselects are assigned to are identified
by it's python type object id (which is, in turn, derived from memory address).
That means that sharing of a class is limited within the Python interpreter
process.