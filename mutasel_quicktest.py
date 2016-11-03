#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mutaprops import *
from mutaprops.utils import SelectSource
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

# @mutaprop_class("Test object")
# class Neco(object):
#
#     def __init__(self, cabin_type):
#         self._cabin_type = cabin_type
#
#     @
#     def cabin_types(self):
#         return {'Big': 4, 'Small': 2, 'Ugly': 0}
#
#     @mutaproperty("Cabin type", MutaTypes.INT)
#     def cabin_type(self):
#         """Speed measured by the odometer."""
#         return self._cabin_type
#
#     @cabin_type.setter(select=cabin_types)
#     def cabin_type(self, value):
#         self._cabin_type = value


class Neco:

    _availables = ['foo', 'bar']

    def __init__(self):
        self._neco = ['One', 'two']

    @mutaselect
    def some_select(cls):
        return cls._availables

    @some_select.setter
    def some_select(cls, items):
        cls._availables = items

    def pokus(self):
        pass


def ex_update_callback(obj_id, select_id, value):
    print("Select {0} on {1} updated to {2}".format(select_id, obj_id, value))

class funcpokus:

    def __call__(necojineho):
        print("Obviusly it's callable: {0}".format(necojineho))

    @staticmethod
    def innerfunc(neco):
        print(neco)

test0 = SelectSource({})
print(test0.items())
print(test0.to_dict())

test1 = SelectSource(['blbost', 'blbost2'])

print(test1.items())
print(test1.get_label('blbost'))
print(test1.get_value('blbost2'))

test2 = SelectSource({'jedna': 1, 'dva': 2, 'tri': 3})
print(test2.items())
print(test2.get_value('dva'))
print(test2.get_label(2))

test3 = SelectSource([('one', 1), ('two', 2), ('three', 3)])
print(test3.items())
print(test3.get_value('three'))
print(test3.get_label(1))
print(test3.to_dict())

neco = Neco()

print("And now, dynaMIC!!!")
test4 = SelectSource(Neco.__dict__['some_select'])
print(test4.items(Neco))
print(test4.to_dict(Neco))

test4.register_update_callback(ex_update_callback)
# neco.some_select = 'blbost'
print(test4.items(Neco))

print(neco.pokus.__self__.__class__)

funcpokus.innerfunc("Blbost jak cip")
