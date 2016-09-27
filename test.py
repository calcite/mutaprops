#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mutaprops import *
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

@mutaprop_class("Test object")
class Test(object):

    def __init__(self, speed, tire_pressure, name):
        self._speed = speed
        # self._position = position
        self._name = name
        self._tire_pressure = tire_pressure

    @mutaproperty("Speed [km/h]", MutaTypes.INT)
    def speed(self):
        """Speed measured by the odometer."""
        return self._speed

    @speed.setter
    def speed(self, value):
        self._speed = value

    @mutaprop_action("Do something")
    def do_some_action(self):
        print("{0}: Doing some action!".format(self._name))

    @mutaproperty("Tire pressure [Bar]", MutaTypes.REAL)
    def tire_pressure(self):
        """Lowest measured tire pressure across all four wheels."""
        return self._tire_pressure

    @tire_pressure.setter(min_value=1.0, max_value=3.5, step=0.2)
    def tire_pressure(self, value):
        self._tire_pressure


def main():

    test = Test(3, 2.23, "Auto1")
    test2 = Test(3, 2.23, "Auto2")
    test.muta_init("Id instance")
    test2.muta_init("Id instance2")
    print("\n")

    for prop_id, prop in test.props.items():
        print("{0}\n------".format(prop))

    print(test.get_class_name())

    test.props['do_some_action'].call(test)

    test.speed = 100
    test2.speed = 30

    print(test.speed)
    print(test2.speed)

    test.do_some_action()
    test2.do_some_action()


if __name__ == "__main__":
    main()
