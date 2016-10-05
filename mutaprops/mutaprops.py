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
    MP_ID = 'id'
    MP_NAME = 'name'
    MP_PRIORITY = 'priority'
    MP_HIERARCHY = 'hierarchy'
    MP_DEFINITION_ORDER = 'deford'
    MP_DOC = 'doc'
    MP_VIEW = 'view'
    MP_TYPE = 'type'
    MP_CLASS_TYPE = 'abstract'

    # I'm using classmethods instead of class constants because of easier
    # inheritance
    @classmethod
    def _allowed_kwargs(cls):
        return cls.MP_PRIORITY, cls.MP_HIERARCHY, cls.MP_DEFINITION_ORDER, \
               cls.MP_DOC, cls.MP_VIEW

    @classmethod
    def _exported_params(cls):
        return (cls.MP_ID, cls.MP_NAME, cls.MP_PRIORITY, cls.MP_HIERARCHY,
                cls.MP_DEFINITION_ORDER,  cls.MP_DOC, cls.MP_VIEW, cls.MP_TYPE)

    def __init__(self, pid, display_name, **kwargs):
        """
        :param pid:  Mutaprop identifier
        :param display_name:  Mutaprop name to be displayed in GUI
        :param kwargs:  Optional attibutes
            *  `priority` : int
                            Display priority, higher numbers are displayed first
            * `hierarchy` : string
                            Hierarchy path in the GUI
            * `deford` :    int
                            Modifies definition order. This is normally defined
                            automatically based on the decorator calls
            * `view` :      string
                            identifier of recommended GUI view type
        """
        self._muta_id = pid
        self._muta_name = display_name

        # Check for invalid kwargs
        for key in kwargs.keys():
            if key not in self._allowed_kwargs():
                raise MutaPropError("Invalid argument {0}".format(key))

        # Assign with defaults
        self._muta_priority = kwargs.get(self.MP_PRIORITY, None)

        self._muta_hierarchy = kwargs.get(self.MP_HIERARCHY, None)
        self._muta_view = kwargs.get(self.MP_VIEW, None)
        self._muta_deford = kwargs.get(self.MP_DEFINITION_ORDER, None)

        if self._muta_deford is None:
            self._muta_deford = MutaProp.__definition_counter
            MutaProp.__definition_counter += 1

        self.__doc__ = kwargs.get(self.MP_DOC, None)

    def _assign_kwarg(self, kwarg_key, kwarg_value):
        if kwarg_key in self._allowed_kwargs():
            if kwarg_key == 'doc':
                self.__doc__ = kwarg_value
            else:
                setattr(self, "_muta_{0}".format(kwarg_key), kwarg_value)
        else:
            raise MutaPropError("Invalid keyword {0}".format(kwarg_key))

    @property
    def prop_id(self):
        return self._muta_id

    @property
    def display_name(self):
        return self._muta_name

    @property
    def display_priority(self):
        return self._muta_priority

    @property
    def hierarchy(self):
        return self._muta_hierarchy

    @property
    def view(self):
        return self._muta_view

    @property
    def definition_order(self):
        return self._muta_deford

    def __str__(self):
        temp = (
            "ID: {pid}: {name}\n" +
            "order: {deford}, priority: {priority}, hierarchy: {hierarchy}\n" +
            "Description: {doc}").format(pid=self._muta_id,
                                         name=self._muta_name,
                                         deford=self._muta_deford,
                                         priority=self._muta_priority,
                                         hierarchy=self._muta_hierarchy,
                                         doc=self.__doc__)
        return temp

    def to_dict(self, obj=None):
        temp = {}
        for attr in self._exported_params():
            if attr == self.MP_DOC:
                temp[self.MP_DOC] = self.__doc__
            elif attr == self.MP_TYPE:
                temp[self.MP_TYPE] = self.MP_CLASS_TYPE
            else:
                temp[attr] = getattr(self, '_muta_{0}'.format(attr))

        return temp


class MutaProperty(MutaProp):
    """Emulate PyProperty_Type() in Objects/descrobject.c"""

    MP_MAXVAL = 'max_val'
    MP_MINVAL = 'min_val'
    MP_STEP = 'step'
    MP_FGET = 'fget'
    MP_FSET = 'fset'
    MP_FDEL = 'fdel'
    MP_CHANGE_CALLBACK = 'change_callback'
    MP_VALUE = 'value'  # This is not used directly in this class
    MP_VALUE_TYPE = 'value_type'
    MP_CLASS_TYPE = 'property'
    MP_READ_ONLY = 'read_only'

    @classmethod
    def _allowed_kwargs(cls):
        return super()._allowed_kwargs() + (cls.MP_MAXVAL, cls.MP_MINVAL,
                                            cls.MP_STEP, cls.MP_FGET,
                                            cls.MP_FSET, cls.MP_FDEL,
                                            cls.MP_CHANGE_CALLBACK)

    @classmethod
    def _exported_params(cls):
        return super()._exported_params() + (cls.MP_MINVAL, cls.MP_MAXVAL,
                                             cls.MP_STEP, cls.MP_READ_ONLY,
                                             cls.MP_VALUE_TYPE)

    def __init__(self, pid, display_name, value_type, **kwargs):

        doc = kwargs.get(self.MP_DOC, None)
        fget = kwargs.get(self.MP_FGET, None)

        if doc is None and fget is not None:
            kwargs[self.MP_DOC] = fget.__doc__

        super().__init__(pid, display_name, **kwargs)

        self._muta_value_type = value_type
        self._muta_min_val = kwargs.get(self.MP_MINVAL, None)
        self._muta_max_val = kwargs.get(self.MP_MAXVAL, None)
        self._muta_step = kwargs.get(self.MP_STEP, None)
        self._muta_fget = kwargs.get(self.MP_FGET, None)
        self._muta_fset = kwargs.get(self.MP_FSET, None)
        self._muta_fdel = kwargs.get(self.MP_FDEL, None)
        self._muta_change_callback = kwargs.get(self.MP_CHANGE_CALLBACK, None)

    def _get_kwargs(self):
        temp = {}
        for kwarg in self._allowed_kwargs():
            if kwarg == self.MP_DOC:
                temp[kwarg] = self.__doc__
            else:
                temp[kwarg] = getattr(self, '_muta_{0}'.format(kwarg))

        return temp

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self._muta_fget is None:
            raise MutaPropError("No getter defined.")
        logger.debug("Getting value for %s", self._muta_name)
        return self._muta_fget(obj)

    def __set__(self, obj, value):
        if self._muta_fset is None:
            raise MutaPropError("No setter defined.")

        different = (self._muta_fget(obj) != value)
        self._muta_fset(obj, value)

        # Notify of property change
        if isinstance(obj, MutaProperty) and obj._is_muta_ready():

            if different and self._muta_change_callback:
                logger.debug("Notification of set call for %s on %s",
                             self._muta_name, obj.muta_id)
                self._muta_change_callback(self, obj)

    def __delete__(self, obj):
        if self._muta_fdel is None:
            raise MutaPropError("No deleter defined.")
        self._muta_fdel(obj)

    def __str__(self):
        temp = (
            super().__str__() +
            "\nProperty {ro} [{valtyp}] ({minval}, {maxval}, {step})".format(
                valtyp=self._muta_value_type,
                minval=self._muta_min_val,
                maxval=self._muta_max_val,
                step=self._muta_step,
                ro='[Read Only]' if self.is_read_only() else ''))
        return temp

    def getter(self, fget):
        logger.debug("{0}: Getter set".format(self._muta_id))
        temp_kwargs = self._get_kwargs()
        temp_kwargs[self.MP_FGET] = fget
        return type(self)(self._muta_id, self._muta_name, self._muta_value_type,
                          **temp_kwargs)

    def setter(self, func=None, min_val=None, max_val=None, step=None):
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
        temp_kwargs = self._get_kwargs()
        temp_kwargs[self.MP_MINVAL] = min_val or self._muta_min_val
        temp_kwargs[self.MP_MAXVAL] = max_val or self._muta_max_val
        temp_kwargs[self.MP_STEP] = step or self._muta_min_val

        if func:
            logger.debug("{0}: Setter set".format(self._muta_id))
            temp_kwargs[self.MP_FSET] = func
            return type(self)(self._muta_id, self._muta_name,
                              self._muta_value_type, **temp_kwargs)

        else:
            def decorator(fset):
                logger.debug("{0}: Setter set".format(self._muta_id))
                temp_kwargs[self.MP_FSET] = fset
                return type(self)(self._muta_id, self._muta_name,
                                  self._muta_value_type, **temp_kwargs)
            return decorator

    def deleter(self, fdel):
        logger.debug("{0}: Deleter set".format(self._muta_id))
        temp_kwargs = self._get_kwargs()
        temp_kwargs[self.MP_FDEL] = fdel
        return type(self)(self._muta_id, self._muta_name, self._muta_value_type,
                          **temp_kwargs)

    def register_change_callback(self, callback):
        self._muta_change_callback = callback

    def to_dict(self, obj=None):
        setattr(self, '_muta_{0}'.format(self.MP_READ_ONLY),
                self.is_read_only())
        temp = super().to_dict()
        if obj:
            temp[self.MP_VALUE] = self.__get__(obj)
        temp[self.MP_VALUE_TYPE] = self._muta_value_type.name
        return temp

    def muta_set(self, obj, value):
        # TODO: Validation!
        if self._muta_fget(obj) != value:
            logger.debug("Set remotely to %s", str(value))
            self._muta_fset(obj, value)

    def is_read_only(self):
        return self._muta_fset is None


class MutaAction(MutaProp):

    MP_CLASS_TYPE = 'action'

    def __init__(self, pid, display_name, callback, **kwargs):

        doc = kwargs.get(self.MP_DOC, None)

        if doc is None:
            kwargs[self.MP_DOC] = callback.__doc__

        super().__init__(pid, display_name, **kwargs)

        self._callback = callback

    def muta_call(self, obj):
        if not hasattr(obj, '_muta_obj_id'):
            raise MutaPropError("Executing action on uninitialized MutaObject.")

        logger.debug("%s: External execution call on %s", self._muta_id,
                     obj._muta_obj_id)
        self.__call__(obj)

    def __call__(self, obj):
        if self._callback is None:
            raise MutaPropError("No callback is defined.")
        self._callback(obj)

    # It's necessary to use non-data descriptor to make this callable class
    # capable of binding a method
    # https://docs.python.org/3.5/howto/descriptor.html#functions-and-methods
    # http://stackoverflow.com/questions/972/adding-a-method-to-an-existing-object-instance
    # http://stackoverflow.com/questions/26226604/decorating-a-class-function-with-a-callable-instance
    def __get__(self, obj, objtype=None):
        return types.MethodType(self, obj)


class MutaPropClass(object):

    MP_OBJ_ID = 'obj_id'
    MP_PROPS = 'props'
    MP_NAME = 'name'
    MP_GUI_ID = 'gui_id'
    MP_GUI_MAJOR_VERSION = 'gui_major_version'
    MP_GUI_MINOR_VERSION = 'gui_minor_version'
    MP_DOC = 'doc'

    @classmethod
    def _exported_params(cls):
        return (cls.MP_OBJ_ID, cls.MP_NAME, cls.MP_PROPS,
                cls.MP_GUI_MAJOR_VERSION, cls.MP_GUI_MINOR_VERSION,
                cls.MP_DOC)

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
        setattr(self, self.muta_attr(self.MP_PROPS),
                OrderedDict([(prop.prop_id, prop) for prop in temp]))

    @property
    def props(self):
        return getattr(self, self.muta_attr(self.MP_PROPS))

    @property
    def muta_id(self):
        return getattr(self, self.muta_attr(self.MP_OBJ_ID))

    # Normal properties cannot be used on class variables, so going with get_*
    @classmethod
    def get_class_name(cls):
        return getattr(cls, cls.muta_attr(cls.MP_NAME))

    @classmethod
    def get_gui_version(cls):
        return (getattr(cls, cls.muta_attr(cls.MP_GUI_MAJOR_VERSION)),
                getattr(cls, cls.muta_attr(cls.MP_GUI_MINOR_VERSION)))

    @classmethod
    def get_gui_id(cls):
        return getattr(cls, cls.muta_attr(cls.MP_GUI_ID))

    @classmethod
    def muta_attr(cls, attr):
        return '_muta_{0}'.format(attr)

    def muta_init(self, object_id):
        self.update_props()
        setattr(self, self.muta_attr(self.MP_OBJ_ID), object_id)

    def is_muta_ready(self):
        if (hasattr(self, self.muta_attr(self.MP_OBJ_ID)) and
                (self.muta_id is not None)):
            return True
        else:
            return False

    def to_dict(self):
        temp = {}
        for attr in self._exported_params():
            if attr == self.MP_DOC:
                temp[self.MP_DOC] = self.__doc__
            else:
                attr_value = getattr(self, self.muta_attr(attr))
                if attr == self.MP_PROPS:
                    print(attr_value)
                    attr_value = [prop.to_dict(obj=self) for prop in
                                  attr_value.values()]

                temp[attr] = attr_value

        return temp

