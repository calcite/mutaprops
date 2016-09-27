#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import Enum
import logging
import types
from collections import OrderedDict

logger = logging.getLogger(__name__)


class MutaPropError(Exception):
    pass


class MutaTypes(Enum):

    STRING = 0
    INT = 1
    REAL = 2
    BOOL = 3


class MutaProp(object):
    """Generic MutaProp object"""

    __definition_counter = 0

    def __init__(self, pid, display_name, display_priority=None, hierarchy=None,
                 definition_order=None, doc=None, view=None):
        self._id = pid
        self._display_name = display_name
        self._display_priority = display_priority
        self._hierarchy = hierarchy
        self._view = view
        self.__doc__ = doc
        self._definition_order = definition_order

        if definition_order is None:
            self._definition_order = MutaProp.__definition_counter
            MutaProp.__definition_counter += 1

    @property
    def prop_id(self):
        return self._id

    @property
    def display_name(self):
        return self._display_name

    @property
    def display_priority(self):
        return self._display_priority

    @property
    def hierarchy(self):
        return self._hierarchy

    @property
    def view(self):
        return self._view

    @property
    def definition_order(self):
        return self._definition_order

    def __str__(self):
        temp = (
            "ID: {pid}: {name}\n" +
            "order: {deford}, priority: {priority}, hierarchy: {hierarchy}\n" +
            "Description: {doc}").format(pid=self._id, name=self._display_name,
                                         deford=self._definition_order,
                                         priority=self._display_priority,
                                         hierarchy=self._hierarchy,
                                         doc=self.__doc__)
        return temp


class MutaProperty(MutaProp):
    "Emulate PyProperty_Type() in Objects/descrobject.c"

    def __init__(self, pid, display_name, value_type, min_value=None,
                 max_value=None, step=None, display_priority=None,
                 hierarchy=None, view=None, fget=None, fset=None, fdel=None,
                 doc=None, definition_order=None, change_callback=None):

        if doc is None and fget is not None:
            doc = fget.__doc__

        super().__init__(pid, display_name, display_priority=display_priority,
                         hierarchy=hierarchy, view=view,
                         definition_order=definition_order, doc=doc)

        self._value_type = value_type
        self._min_value = min_value
        self._max_value = max_value
        self._step = step
        self._fget = fget
        self._fset = fset
        self._fdel = fdel
        self._change_callback = change_callback

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self._fget is None:
            raise MutaPropError("No getter defined.")
        logger.debug("Getting value for %s", self._display_name)
        return self._fget(obj)

    def __set__(self, obj, value):
        if self._fset is None:
            raise MutaPropError("No setter defined.")

        different = (self._fget(obj) != value)
        self._fset(obj, value)

        # Notify of property change
        if hasattr(obj, '_muta_obj_id'):
            logger.debug("Called setter for %s on %s", self._display_name,
                         obj._muta_obj_id)
            if different and (self._change_callback):
                self._change_callback(self, obj)

    def __delete__(self, obj):
        if self._fdel is None:
            raise MutaPropError("No deleter defined.")
        self._fdel(obj)

    def __str__(self):
        temp = (
            super().__str__() +
            "\nProperty [{valtyp}] ({minval}, {maxval}, {step})".format(
                valtyp=self._value_type,
                minval=self._min_value,
                maxval=self._max_value,
                step=self._step))
        return temp

    def getter(self, fget):
        logger.debug("{0}: Getter set".format(self._id))
        return type(self)(self._id, self._display_name, self._value_type,
                          min_value=self._min_value, max_value=self._max_value,
                          step=self._step,
                          display_priority=self._display_priority,
                          hierarchy=self._hierarchy, view=self._view,
                          fget=fget, fset=self._fset, fdel=self._fdel,
                          doc=self.__doc__,
                          definition_order=self._definition_order,
                          change_callback=self._change_callback)

    def setter(self, func=None, min_value=None, max_value=None, step=None):
        """Decorator function usable in two ways:
            * decorator without arguments::

                @some_metaprop.setter
                def some_metaprop(self, value):
                    pass


            * decorator with arguments::

                @some_metaprop.setter(min_value=1.0, max_value=2.0)
                def some_metaprop(self, value):
                    pass

        :param func: Is only for internal decorator use, don't use it
        :param min_value: Min. value for numeric types, min. lenght for Strings
        :param max_value: Max. value for numeric types, max. length for Strings
        :param step: Step increment for numeric types

        :returns: MetaProp object
        """

        if func:
            logger.debug("{0}: Setter set".format(self._id))
            return type(self)(
                self._id, self._display_name, self._value_type,
                min_value=self._min_value, max_value=self._max_value,
                step=self._step, display_priority=self._display_priority,
                hierarchy=self._hierarchy, view=self._view, fget=self._fget,
                fset=func, fdel=self._fdel, doc=self.__doc__,
                definition_order=self._definition_order,
                change_callback=self._change_callback)

        else:
            def decorator(fset):
                logger.debug("{0}: Setter set".format(self._id))
                return type(self)(
                    self._id, self._display_name, self._value_type,
                    min_value=min_value or self._min_value,
                    max_value=max_value or self._max_value,
                    step=step or self._step,
                    display_priority=self._display_priority,
                    hierarchy=self._hierarchy, view=self._view, fget=self._fget,
                    fset=fset, fdel=self._fdel, doc=self.__doc__,
                    definition_order=self._definition_order,
                    change_callback=self._change_callback)
            return decorator

    def deleter(self, fdel):
        logger.debug("{0}: Deleter set".format(self._id))
        return type(self)(self._id, self._display_name, self._value_type,
                          min_value=self._min_value, max_value=self._max_value,
                          step=self._step,
                          display_priority=self._display_priority,
                          hierarchy=self._hierarchy, view=self._view,
                          fget=self._fget, fset=self._fset, fdel=fdel,
                          doc=self.__doc__,
                          definition_order=self._definition_order,
                          change_callback=self._change_callback)

    def register_change_callback(self, callback):
        self._change_callback = callback


class MutaAction(MutaProp):

    def __init__(self, pid, display_name, callback, display_priority=None,
                 hierarchy=None, view=None, doc=None, definition_order=None):

        if doc is None and callback is not None:
            doc = callback.__doc__

        super().__init__(pid, display_name, display_priority=display_priority,
                         hierarchy=hierarchy, view=view,
                         definition_order=definition_order, doc=doc)

        self._callback = callback

    def call(self, obj):
        if not hasattr(obj, '_muta_obj_id'):
            raise MutaPropError("Executing action on uninitialized MutaObject.")

        logger.debug("%s: External execution call on %s", self._id,
                     obj._muta_obj_id)
        self.__call__(obj)

    def __call__(self, obj):
        if self._callback is None:
            raise MutaPropError("No callback is defined.")
        self._callback(obj)

    def __get__(self, obj, objtype=None):
        return types.MethodType(self, obj)


class MutaPropClass(object):

    def update_props(self):
        """Because this is potentially heavy operation and property definitions
        are not likely to be changed during objects lifetime, it's easier to
        cache it.
        """
        temp = []

        for basecls in type(self).mro():
            for prop, value in basecls.__dict__.items():
                if isinstance(value, MutaProp):
                    temp.append(value)

        temp.sort(key=lambda x: x.definition_order)
        self._muta_props = OrderedDict([(prop.prop_id, prop) for prop in temp])

    @property
    def props(self):
        return self._muta_props

    # Normal properties cannot be used on class variables, so going with get_*
    @classmethod
    def get_class_name(cls):
        return cls._mutaprop_display_name

    @classmethod
    def get_gui_version(cls):
        return (cls._mutaprop_major_version, cls._mutaprop_minor_version)

    @classmethod
    def get_gui_id(cls):
        return cls._mutaprop_gui_id

    def muta_init(self, object_id):
        self.update_props()
        self._muta_obj_id = object_id
