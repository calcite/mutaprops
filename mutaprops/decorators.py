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
                    {"_mutaprop_display_name": display_name,
                     "_mutaprop_gui_id": gui_id,
                     "_mutaprop_gui_major_version": gui_major_version,
                     "_mutaprop_gui_minor_version": gui_minor_version,
                     "__doc__": cls.__doc__})

    return decorator


def mutaproperty(display_name, value_type, min_value=None, max_value=None,
                 step=None, display_priority=None, hierarchy=None, view=None):

    def decorator(func):
        logger.debug("Registered mutaproperty: %s", func.__name__)
        prop = MutaProperty(func.__name__, display_name, value_type,
                            min_value=min_value, max_value=max_value, step=step,
                            display_priority=display_priority,
                            hierarchy=hierarchy, view=view, fget=func)
        return prop
    return decorator


def mutaprop_action(display_name, display_priority=None, hierarchy=None,
                    view=None):

    def decorator(func):
        logger.debug("Registered mutaprop action: %s", func.__name__)
        action = MutaAction(func.__name__, display_name, func,
                            display_priority=display_priority,
                            hierarchy=hierarchy, view=view)
        return action
    return decorator
