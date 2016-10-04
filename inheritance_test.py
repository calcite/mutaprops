#!/usr/bin/env python
# -*- coding: utf-8 -*-

class A(object):

    _some_attr = ('neco', 'neco_jine')

    @classmethod
    def _allowed_attrs(cls):
        return ('neco', 'neco_jine')

    def __init__(self):
        pass

    def list_attrs(self):
        for attr in self._some_attr:
            print(attr)


class B(A):

    _some_attr = ('Jeste neco jine',)


    def __init__(self):
        pass

    def list_attrs(self):
        super().list_attrs()

    @classmethod
    def _allowed_attrs(cls):
        return super()._allowed_attrs() + ('Jeste neco jine',)



test = B()
print(test._allowed_attrs())
