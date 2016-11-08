#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mutaprops import *
import logging
import sys
import time
import asyncio

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

@mutaprop_class("Test object")
class Neco(object):

    _roof_types = {'Convertible': 5, 'PapaMobil': 20, 'Normal': 45}

    def __init__(self, speed, tire_pressure, name, trunk_capacity):
        self._speed = speed
        # self._position = position
        self._name = name
        self._tire_pressure = tire_pressure
        self._trunk_capacity = trunk_capacity
        self._turbo_enabled = False
        self._body_type = 'Sedan'
        self._engine_type = 20
        self._engine_types = [('Diesel', 20), ('Gasoline', 30), ('Hybrid', 10)]
        self._roof_type = 45

    @mutaproperty("Speed [km/h]", MutaTypes.INT)
    def speed(self):
        """Speed measured by the odometer."""
        return self._speed

    @speed.setter
    def speed(self, value):
        self._speed = value

    @mutaproperty("Vehicle name", MutaTypes.STRING)
    def name(self):
        return self._name

    @name.setter(max_val=10)
    def name(self, value):
        self._name = value

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

    @mutaproperty("Body type", MutaTypes.STRING)
    def body_type(self):
        return self._body_type

    @body_type.setter(select=['Minivan', 'Combi', 'Sedan'])
    def body_type(self, value):
        self._body_type = value

    @mutaselect
    def engine_types(self):
        return self._engine_types

    @engine_types.setter
    def engine_types(self, values):
        self._engine_types = values

    @mutaproperty("Engine type", MutaTypes.INT, select=engine_types)
    def engine_type(self):
        return self._engine_type

    @engine_type.setter
    def engine_type(self, value):
        self._engine_type = value

    @mutaselect_classproperty
    def roof_types(cls):
        return cls._roof_types

    @roof_types.setter_classproperty
    def set_roof_types(cls, values):
        cls._roof_types = values

    @mutaproperty("Roof type", MutaTypes.INT)
    def roof_type(self):
        return self._roof_type

    @roof_type.setter(select=roof_types)
    def roof_type(self, value):
        self._roof_type = value


@asyncio.coroutine
def speed_updater(obj):
    while True:
        obj.speed += 1
        yield from asyncio.sleep(1)

@asyncio.coroutine
def trunk_updater(obj):
    while True:
        obj.trunk_capacity = 500
        yield from asyncio.sleep(2)
        obj.trunk_capacity = 600
        yield from asyncio.sleep(2)

@asyncio.coroutine
def device_updater(manager):
    test3 = Neco(50, 2.8, "TempAuto", 550)
    while True:
        manager.add_object(test3, "Instance3")
        yield from asyncio.sleep(5)
        manager.remove_object(test3)
        yield from asyncio.sleep(5)


@asyncio.coroutine
def select_updater(obj):
    while True:
        obj.engine_types = [('Diesel', 20), ('Gasoline', 30), ('Hybrid', 10),
                            ('Uhlak', 0)]
        yield from asyncio.sleep(2)
        Neco.set_roof_types({'Convertible': 5, 'PapaMobil': 20, 'Normal': 45,
                             'Idiotic': 25})
        yield from asyncio.sleep(2)
        obj.engine_types = [('Diesel', 20), ('Gasoline', 30), ('Hybrid', 10)]
        yield from asyncio.sleep(2)
        Neco.set_roof_types({'Convertible': 5, 'PapaMobil': 20, 'Normal': 45})
        yield from asyncio.sleep(2)


def main():

    test = Neco(3, 2.23, "Auto1", 500)
    test2 = Neco(3, 2.23, "Auto2", 600)
    test.muta_init("instance 1")
    test2.muta_init("Id instance2")
    print("\n")

    # for prop_id, prop in test.props.items():
    #     print("{0}\n------".format(prop))
    #     print(prop.to_dict(obj=test))
    #     print("\n---------")
    #
    # print(test.get_class_name())
    #
    # test.props['do_some_action'].muta_call(test)
    #
    # test.speed = 100
    # test2.speed = 30
    #
    # print(test.speed)
    # print(test2.speed)
    #
    # test.do_some_action()
    # test2.do_some_action()


    loop = asyncio.get_event_loop()
    man = HttpMutaManager("ConCon2", loop=loop)
    man.add_object(test)
    man.add_object(test2, "instance #2")

    # print(Neco.roof_types)
    #
    # Neco.set_roof_types(['Kolotoc', 'RedBullCan', 'RadarTower'])
    # test.set_roof_types(['Blbost', "jeste vetsi blbost"])
    # print(Neco._roof_types)
    # print(Neco.roof_types)
    # print(test.roof_types)
    # print(Neco.roof_types)
    # test.engine_types = [, ('Nuclear', 30), ('Unicorn', 10)]

    # asyncio.ensure_future(speed_updater(test))
    # asyncio.ensure_future(trunk_updater(test))
    # asyncio.ensure_future(device_updater(man))
    # asyncio.ensure_future(select_updater(test))
    man.run(port=9000)
    # man.run_in_thread(port=9000)

    #Now the fun begins
    while True:
        test.speed += 1
        time.sleep(5)


if __name__ == "__main__":
    main()
