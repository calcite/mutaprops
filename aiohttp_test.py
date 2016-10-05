#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aiohttp import web
import asyncio
from mutaprops import *


@mutaprop_class("Test object")
class Dummy(object):

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

    @tire_pressure.setter(min_val=1.0, max_val=3.5, step=0.2)
    def tire_pressure(self, value):
        self._tire_pressure

@asyncio.coroutine
def hello(request):
    temp = Dummy(96.5, 2.28, "Car of the year")
    temp.muta_init("Test object")
    return web.json_response(temp.to_dict())
    # return web.Response(text="Hello world")

def main():
    app = web.Application()
    app.router.add_get('/', hello)
    web.run_app(app)

if __name__ == "__main__":
    main()
