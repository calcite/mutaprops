#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from .mutaprops import MutaProperty, MutaAction, MutaPropClass

logger = logging.getLogger(__name__)


def mutaprop_class(display_name, gui_id=None, gui_major_version=0,
                   gui_minor_version=0):

    def decorator(cls):
        logger.debug("Registered mutaprop class: %s", cls.__name__)
        return type("MutaProp{0}".format(cls.__name__), (cls, MutaPropClass),
                    {"_muta_name": display_name,
                     "_muta_gui_id": gui_id,
                     "_muta_gui_major_version": gui_major_version,
                     "_muta_gui_minor_version": gui_minor_version,
                     "__doc__": cls.__doc__})

    return decorator


def mutaproperty(display_name, value_type, **kwargs):

    def decorator(func):
        logger.debug("Registered mutaproperty: %s", func.__name__)
        kwargs[MutaProperty.MP_FGET] = func
        prop = MutaProperty(func.__name__, display_name, value_type, **kwargs )
        return prop
    return decorator


def mutaprop_action(display_name, **kwargs):

    def decorator(func):
        logger.debug("Registered mutaprop action: %s", func.__name__)
        action = MutaAction(func.__name__, display_name, func, **kwargs)
        return action
    return decorator
