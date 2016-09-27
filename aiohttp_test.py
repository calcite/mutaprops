#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aiohttp import web
import asyncio


@asyncio.coroutine
def hello(request):
    return web.Response(text="Hello world")

def main():
    app = web.Application()
    app.router.add_get('/', hello)
    web.run_app(app)

if __name__ == "__main__":
    main()
