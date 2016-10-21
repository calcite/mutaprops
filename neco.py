#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mutaprops import *
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

@mutaprop_class("Test object")
class Neco(object):

    def __init__(self, speed, tire_pressure, name, trunk_capacity):
        self._speed = speed
        # self._position = position
        self._name = name
        self._tire_pressure = tire_pressure
        self._trunk_capacity = trunk_capacity
        self._turbo_enabled = False

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

    @tire_pressure.setter(min_val=1.0, max_val=3.5, step=0.2)
    def tire_pressure(self, value):
        self._tire_pressure

    @mutaproperty("Trunk capacity [liter]", MutaTypes.INT,
                  select={'Small': 500, 'Big': 600})
    def trunk_capacity(self):
        return self._trunk_capacity

    @trunk_capacity.setter
    def trunk_capacity(self, value):
        self._trunk_capacity = value

    @mutaproperty("Turbo enabled", MutaTypes.BOOL)
    def turbo_enabled(self):
        return self._turbo_enabled

    @turbo_enabled.setter()
    def turbo_enabled(self, enabled):
        self._turbo_enabled = enabled
def main():

    test = Neco(3, 2.23, "Auto1", 500)
    test2 = Neco(3, 2.23, "Auto2", 600)
    test.muta_init("instance1")
    test2.muta_init("Id instance2")
    print("\n")

    for prop_id, prop in test.props.items():
        print("{0}\n------".format(prop))
        print(prop.to_dict(obj=test))
        print("\n---------")

    print(test.get_class_name())

    test.props['do_some_action'].muta_call(test)

    test.speed = 100
    test2.speed = 30

    print(test.speed)
    print(test2.speed)

    test.do_some_action()
    test2.do_some_action()

    man = HttpMutaManager()
    man.add_object(test)
    man.add_object(test2, "instance2")
    man.run(port=9000)

if __name__ == "__main__":
    main()
