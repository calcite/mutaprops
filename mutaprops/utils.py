#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import OrderedDict


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

    def to_json(self):
        return [(select, value) for select, value in self.items()]
