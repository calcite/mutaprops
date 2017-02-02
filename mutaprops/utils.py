#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import OrderedDict
import logging
import inspect
from docutils.core import publish_parts

logger = logging.getLogger(__name__)


class MutaPropError(Exception):
    pass


class BiDict(OrderedDict):
    """
    Bidirectional dictionary for handling both getters and setters of
    MutaProperties with selects.
    Copied from http://stackoverflow.com/a/21894086 and adopted for Python3.
    """
    def __init__(self, *args, **kwargs):
        self.inverse = OrderedDict({})
        super().__init__(*args, **kwargs)
        # for key, value in self.items():
        #     self.inverse.setdefault(value,[]).append(key)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.inverse.setdefault(value,[]).append(key)

    def __delitem__(self, key):
        self.inverse.setdefault(self[key],[]).remove(key)
        if self[key] in self.inverse and not self.inverse[self[key]]:
            del self.inverse[self[key]]
        super().__delitem__(key)

    def get_map_list(self):
        return [(select, value) for select, value in self.items()]


class SelectSource:
    """
    Provider for the mutaprop select list.
    """
    TYPE_MAP = 'map'
    TYPE_LIST = 'list'
    PROVIDER_STATIC = 'static'
    PROVIDER_DYNAMIC = 'dynamic'

    def __init__(self, select):
        if select:
            (data_type, data) = self._preprocess_data(select)

            if data_type == self.PROVIDER_DYNAMIC:
                self._type = None
                self._provider = self.PROVIDER_DYNAMIC
                self._source = select
                logger.debug("Initialized SelectSource with %s" %
                             self._source.select_id)
            else:
                self._provider = self.PROVIDER_STATIC
                self._type = data_type
                self._source = data
        else:
            self._provider = None
            self._type = self.TYPE_LIST
            self._source = []

    def __str__(self):
        if self._provider == self.PROVIDER_STATIC:
            (dtype, d) = self.items()
            return "Select=<Static, type {0}, items: {1}>".format(dtype, d)
        if self._provider == self.PROVIDER_DYNAMIC:
            return "Select=<Dynamic select from {0}>".format(
                                                        self._source.select_id)
        if self._provider is None:
            return "Select=<None>"

    def __bool__(self):
        return (self._provider is not None)

    @classmethod
    def _infer_type(cls, data):
        if isinstance(data, list):
            # First check if it's not list of key-value tuples
            # TODO: This check should be rather checking the whole set...
            if isinstance(data[0], tuple) and (len(data[0]) == 2):
                return cls.TYPE_MAP
            else:
                return cls.TYPE_LIST

        elif isinstance(data, dict):
            return cls.TYPE_MAP
        elif isinstance(data, MutaSelect):
            return cls.PROVIDER_DYNAMIC
        else:
            raise MutaPropError("Unsupported data type for select.")

    @classmethod
    def _preprocess_data(cls, data):
        data_type = cls._infer_type(data)

        if data_type == cls.TYPE_MAP:
            processed_data = BiDict(data)
        else:
            processed_data = data

        return (data_type, processed_data)

    @classmethod
    def _items(cls, data_type, data):

        if data_type == cls.TYPE_MAP:
            data = data.get_map_list()

        return (data_type, data)

    @classmethod
    def _items_to_dict(cls, data_type, data):
        return {'type': data_type, 'items': data}

    @classmethod
    def items_dict(cls, data):
        (dt, d) = cls._preprocess_data(data)
        (dt, d) = cls._items(dt, d)
        return cls._items_to_dict(dt, d)

    def _get_data(self, obj=None):
        data_type = self._type
        data = self._source

        if self._provider == self.PROVIDER_DYNAMIC:
            temp = self._source.__get__(obj)
            (data_type, data) = self._preprocess_data(temp)

        return (data_type, data)

    def items(self, obj=None):
        data_type, data = self._get_data(obj)
        return self._items(data_type, data)

    def get_value(self, key, obj=None):
        (data_type, data) = self._get_data(obj)

        if key not in data:
            raise MutaPropError("Unknown key %s" % key)

        if data_type == self.TYPE_MAP:
            return data[key]
        else:
            return key

    def get_label(self, value, obj=None):
        (data_type, data) = self._get_data(obj)

        if data_type == self.TYPE_MAP:
            data = data.inverse

        if value not in data:
            raise MutaPropError("Unknown value %s" % value)

        if data_type == self.TYPE_MAP:
            return data[value]
        else:
            return value

    def to_dict(self, obj=None):

        if self._provider is None:
            return {}

        (data_type, data) = self.items(obj)
        contents = self._items_to_dict(data_type, data)
        dct = {'source': self._provider, 'data': contents}
        if self._provider == self.PROVIDER_STATIC:
            return dct

        if self._provider == self.PROVIDER_DYNAMIC:
            dct['id'] = self._source.select_id
            if self._source.class_scoped:
                dct['classId'] = id(self._source.owner_class)
            return dct


class MutaSelect(object):

    def __init__(self, select_id, getter=None, setter=None,
                 update_callback=None, class_scope=False):
        self._id = select_id
        self._getter = getter
        self._setter = setter
        self._update_callback = update_callback
        self._class_scope = class_scope
        self._owner_class = None
        logger.debug("Initialized mutaselect %s" % self._id)

    def getter(self, func):
        return type(self)(func.__name__, getter=func, setter=self._setter,
                          update_callback=self._update_callback)

    def setter(self, func):
        return type(self)(self._id, getter=self._getter, setter=func,
                          update_callback=self._update_callback,
                          class_scope=self._class_scope)

    def setter_classproperty(self, func):

        if not self._class_scope:
            raise MutaPropError("Initializing class property setter" +
                                " for property without class scope.")

        def class_scoped_setter(cls, value):

            different = self._getter(cls) != value
            func(cls, value)

            # Notify of property change
            if different and self._update_callback:
                logger.debug("Notification of set on mutaselect on %s", id(cls))
                self._update_callback(id(cls), self._id, value)

        return classmethod(class_scoped_setter)

    def register_update_callback(self, callback):
        logger.debug("Select update callback registered for %s" %
                     self.select_id)
        self._update_callback = callback

    def set_owner_class(self, defining_class):
        self._owner_class = defining_class

    @property
    def owner_class(self):
        return self._owner_class

    @property
    def select_id(self):
        return self._id

    @property
    def class_scoped(self):
        return self._class_scope

    def _get_obj(self, obj):

        if self._owner_class:
            return self._owner_class

        if obj:
            return obj

        raise MutaPropError("Object not specified.")

    def __call__(self, value):
        if self._class_scope:
            self.__set__(None, value)

    def __get__(self, obj, objtype=None):
        if obj is None:
            if self._class_scope:
                obj = objtype
            else:
                raise MutaPropError("Object not specified.")

        if self._getter is None:
            raise MutaPropError("No select getter defined.")
        # logger.debug("Getting value for %s", self._muta_name)
        return self._getter(obj)

    def __set__(self, obj, value):
        if self._setter is None:
            raise MutaPropError("No select setter defined.")

        different = (self._getter(obj) != value)
        self._setter(obj, value)

        # Notify of property change
        try:
            if different and self._update_callback:
                self._update_callback(obj.muta_id, self._id, value)
        except AttributeError:
            raise Warning("Mutaselect change on unitialized object.")

def rest_to_html(docstring):
    """ Converts reSTructured text from docstrings to HTML.

    As it uses quite strange docutils implementations, it adds some unnecessary
    clutter to the HTML <div class="document"> etc.

    """
    if docstring:
        return publish_parts(inspect.cleandoc(docstring),
                             writer_name='html')['html_body']
    else:
        return None
