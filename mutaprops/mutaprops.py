#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import Enum
import logging
import types
from collections import OrderedDict
from .utils import MutaPropError, SelectSource, MutaSelect

logger = logging.getLogger(__name__)


class MutaTypes(Enum):
    STRING = 0
    INT = 1
    REAL = 2
    BOOL = 3

    @classmethod
    def typecast(cls, muta_type, string_value):

        if muta_type == cls.STRING:
            return string_value
        elif muta_type == cls.INT:
            return int(string_value)
        elif muta_type == cls.REAL:
            return float(string_value)
        elif muta_type == cls.BOOL:
            return bool(string_value.lower() == 'true')
        else:
            raise MutaPropError("Unknown value type {0}".format(muta_type))


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
    MP_SELECT = 'select'
    MP_TOGGLE = 'toggle'

    @classmethod
    def _allowed_kwargs(cls):
        return super()._allowed_kwargs() + (cls.MP_MAXVAL, cls.MP_MINVAL,
                                            cls.MP_STEP, cls.MP_FGET,
                                            cls.MP_FSET, cls.MP_FDEL,
                                            cls.MP_CHANGE_CALLBACK,
                                            cls.MP_SELECT, cls.MP_TOGGLE)

    @classmethod
    def _exported_params(cls):
        return super()._exported_params() + (cls.MP_MINVAL, cls.MP_MAXVAL,
                                             cls.MP_STEP, cls.MP_READ_ONLY,
                                             cls.MP_VALUE_TYPE,
                                             cls.MP_SELECT, cls.MP_TOGGLE)

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
        temp_select = kwargs.get(self.MP_SELECT, {})
        logger.debug("Initializing mutaprop %s with selector %s" % (pid, temp_select))

        if isinstance(temp_select, SelectSource):
            self._muta_select = temp_select
        else:
            self._muta_select = SelectSource(temp_select)

        self._muta_toggle = kwargs.get(self.MP_TOGGLE, None)

    @property
    def value_type(self):
        return self._muta_value_type

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
        try:
            if different and self._muta_change_callback:
                logger.debug("Notification of set call for %s on %s",
                             self._muta_name, obj.muta_id)
                self._muta_change_callback(obj.muta_id, self._muta_id,
                                           value)
        except AttributeError:
            raise Warning("Property change called on unitialized object.")

    def __delete__(self, obj):
        if self._muta_fdel is None:
            raise MutaPropError("No deleter defined.")
        self._muta_fdel(obj)

    def __str__(self):
        temp = (
            super().__str__() +
            "\nProperty {ro} [{valtyp}] ({minval}, {maxval}, {step}, {select})"
            .format(
                valtyp=self._muta_value_type,
                minval=self._muta_min_val,
                maxval=self._muta_max_val,
                step=self._muta_step,
                select=self._muta_select,
                ro='[Read Only]' if self.is_read_only() else ''))
        return temp

    def getter(self, fget):
        logger.debug("{0}: Getter set".format(self._muta_id))
        temp_kwargs = self._get_kwargs()
        temp_kwargs[self.MP_FGET] = fget
        return type(self)(self._muta_id, self._muta_name, self._muta_value_type,
                          **temp_kwargs)

    def setter(self, func=None, min_val=None, max_val=None, step=None,
               select={}):
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
        :param select: Selector object to provide user select. A selector can be
                        either a dict, or list of (label, value) tuples, or
                        a MutaSelect which provides dict or list of tuples.
                        If selector is a MutaSelect, the selector list will be
                        updated during runtime.

        :returns: MutaProp object
        """
        temp_kwargs = self._get_kwargs()
        temp_kwargs[self.MP_MINVAL] = min_val or self._muta_min_val
        temp_kwargs[self.MP_MAXVAL] = max_val or self._muta_max_val
        temp_kwargs[self.MP_STEP] = step or self._muta_min_val
        temp_kwargs[self.MP_SELECT] = SelectSource(select) or self._muta_select

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

        # update the select (this would deserve some major rewrite btw)
        # because now the select serialization is duplicated
        temp[self.MP_SELECT] = self._muta_select.to_dict(obj)

        # Remove toggle parameter for non-bool items
        if self._muta_value_type != MutaTypes.BOOL:
            temp.pop(self.MP_TOGGLE)

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

    def update_props(self, change_callback=None, select_update_callback=None):
        """Because this is potentially heavy operation and property definitions
        are not likely to be changed during objects lifetime, it's easier to
        cache it.
        """
        temp = []

        for basecls in type(self).mro():
            for prop, value in basecls.__dict__.items():
                if isinstance(value, MutaProp):
                    temp.append(value)
                if isinstance(value, MutaProperty):
                    value.register_change_callback(change_callback)
                if isinstance(value, MutaSelect):
                    value.register_update_callback(select_update_callback)
                    if value.class_scoped:
                        value.set_owner_class(self.__class__)

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

    def muta_init(self, object_id, change_callback=None,
                  select_update_callback=None):
        self.update_props(change_callback, select_update_callback)
        setattr(self, self.muta_attr(self.MP_OBJ_ID), object_id)

    def muta_unregister(self):
        self.update_props(change_callback=None, select_update_callback=None)

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

