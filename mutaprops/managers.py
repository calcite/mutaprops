#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import urllib.parse
from aiohttp import web
from .mutaprops import MutaPropError, MutaPropClass, MutaAction, MutaTypes
from collections import OrderedDict
import threading
import sockjs
import json
import logging


class MutaManagerError(MutaPropError):
    pass


class HttpMutaManager(object):

    INDEX_FILE = open('web_ui/index.html', 'rb').read()
    NOTIFICATION_PROPERTY_CHANGE = 'property_change'
    NOTIFICATION_EXTERNAL_CHANGE = 'external_change'
    NOTIFICATION_LOG_MESSAGE = 'log'
    NOTIFICATION_OBJECTS_CHANGE = 'objects_change'

    def __init__(self, name, loop=None):
        """
        :param loop: Asyncio execution loop,
        see `aiohttp.web.Application <http://aiohttp.readthedocs.io/en/stable/web_reference.html#aiohttp.web.run_app>`_
        for details.
        """
        self._name = name
        self._app = web.Application(loop=loop)
        self._muta_objects = OrderedDict()
        self._init_router()
        self._sockjs_manager = None
        self._logger = logging.getLogger(HttpMutaManager.__class__.__name__)

    @asyncio.coroutine
    def _get_app_name(self, request):
        return web.Response(text=self._name)

    @asyncio.coroutine
    def _get_object_list(self, request):

        # Don't know if it's better to return empty list or 204...
        # if not self._muta_objects:
        #     return web.HTTPNoContent() # No objects defined

        # temp = {'objects': [obj.muta_id for obj in self._muta_objects]}
        # temp = [obj.muta_id for obj in self._muta_objects]
        temp = list(self._muta_objects.keys())
        return web.json_response(temp)

    def _find_object(self, request):
        return self._muta_objects[request.match_info['obj_id']]

    @asyncio.coroutine
    def _get_object(self, request):
        try:
            return web.json_response(self._find_object(request).to_dict())
        except KeyError:
            return web.HTTPNotFound()

    @asyncio.coroutine
    def _get_props(self, request):
        try:
            temp_obj = self._find_object(request)
            temp_props = [prop.to_dict(obj=temp_obj)
                          for prop in temp_obj.props.values()]

            return web.json_response(temp_props)
        except KeyError:
            return web.HTTPNotFound()

    def _find_prop(self, obj, request):
        return obj.props[request.match_info['prop_id']]

    @asyncio.coroutine
    def _get_prop(self, request):
        try:
            temp_obj = self._find_object(request)
            return web.json_response(
                self._find_prop(temp_obj, request).to_dict(obj=temp_obj))
        except KeyError:
            return web.HTTPNotFound()


    @asyncio.coroutine
    def _get_prop_value(self, request):
        try:
            temp_obj = self._find_object(request)
            return web.json_response(
                self._find_prop(temp_obj, request).__get__(temp_obj))
        except KeyError:
            return web.HTTPNotFound()

    @asyncio.coroutine
    def _set_prop_value(self, request):
        try:
            temp_obj = self._find_object(request)
            temp_prop = self._find_prop(temp_obj, request)
        except KeyError:
            return web.HTTPNotFound()

        if temp_prop.is_read_only():
            return web.HTTPMethodNotAllowed('value', [],
                                            text="Property is read only.")

        value = urllib.parse.parse_qs(request.query_string)['value'][0]
        value = MutaTypes.typecast(temp_prop.value_type, value)
        return web.json_response(
            self._find_prop(temp_obj, request).muta_set(temp_obj, value))

    @asyncio.coroutine
    def _set_prop_action(self, request):
        try:
            temp_obj = self._find_object(request)
            temp_prop = self._find_prop(temp_obj, request)
        except KeyError:
            return web.HTTPNotFound()

        if isinstance(temp_prop, MutaAction):
            temp_prop.muta_call(temp_obj)
            return web.HTTPOk()
        else:
            return web.HTTPMethodNotAllowed("action", ['value',],
                                            text="Resource is not MutaAction.")

    def _sockjs_handler(self, msg, session):
        """ SockJS handler is now not doing anything because we onlu use
        SockJS for downstream.
        :param session:
        :return:
        """
        if msg.tp == sockjs.MSG_OPEN:
            self._sockjs_manager = session.manager
            # session.manager.broadcast("Someone joined.")
        elif msg.tp == sockjs.MSG_CLOSED:
            self._sockjs_manager = None
            # session.manager.broadcast("Someone left.")

    def _property_change(self, obj_id, prop_id, value):
        self._send_notification(self.NOTIFICATION_PROPERTY_CHANGE,
                                objId=obj_id, propId=prop_id, value=value)
        self._logger.debug("Property {0} changed value to {1} on {2}".format(
                                                        obj_id, prop_id, value))

    def _send_notification(self, msg_type, **kwargs):
        if self._sockjs_manager:
            temp = {'type': msg_type, 'params': kwargs}
            self._sockjs_manager.broadcast(json.dumps(temp))

    def _index(self, request):
        return web.Response(body=self.INDEX_FILE, content_type='text/html')

    def _init_router(self):
        self._app.router.add_get('/', self._index)
        self._app.router.add_static('/dist', r'web_ui/dist/', show_index=True)

        self._app.router.add_get('/api/appname', self._get_app_name)
        self._app.router.add_get('/api/objects', self._get_object_list)
        self._app.router.add_get('/api/objects/{obj_id}', self._get_object)
        self._app.router.add_get('/api/objects/{obj_id}/props', self._get_props)
        self._app.router.add_get('/api/objects/{obj_id}/props/{prop_id}',
                                 self._get_prop)
        self._app.router.add_get('/api/objects/{obj_id}/props/{prop_id}/value',
                                 self._get_prop_value)
        self._app.router.add_put('/api/objects/{obj_id}/props/{prop_id}',
                                 self._set_prop_value)

        # http://programmers.stackexchange.com/questions/141410/restful-state-changing-actions
        self._app.router.add_put('/api/objects/{obj_id}/props/{prop_id}/action',
                                 self._set_prop_action)
        sockjs.add_endpoint(self._app, self._sockjs_handler, name='notifier',
                            prefix='/api/notifications/')

    def add_object(self, muta_object, obj_id=None):

        # Somewhat unnecessarily complicated checking
        if not isinstance(muta_object, MutaPropClass):
            raise MutaPropError("Object is not MutaClass instance.")

        if not muta_object.is_muta_ready() and obj_id is None:
            raise MutaPropError("MutaObject is not initialized. " +
                                "Provide obj_id or initialize externally.")

        if muta_object.is_muta_ready():
            if obj_id:
                muta_object.muta_init(obj_id, self._property_change)
        else:
            if not obj_id:
                raise MutaPropError("MutaObject is not initialized. " +
                                    "Provide obj_id or initialize externally.")

            muta_object.muta_init(obj_id, self._property_change)

        # Check that we won't have two objects with the same id
        if muta_object.muta_id in self._muta_objects:
            raise MutaPropError(
                "MutaObject with id {0} is already registered.".format(
                    muta_object.muta_id))

        self._muta_objects[muta_object.muta_id] = muta_object
        self._send_notification(self.NOTIFICATION_OBJECTS_CHANGE,
                                objId=muta_object.muta_id, action='added')
        self._logger.debug("Added object %s" % muta_object.muta_id)

    def remove_object(self, muta_object):
        try:
            temp = self._muta_objects.pop(muta_object.muta_id)
            temp.muta_unregister()
            self._send_notification(self.NOTIFICATION_OBJECTS_CHANGE,
                                    objId=temp.muta_id, action='removed')
            self._logger.debug("Removed object %s" % temp.muta_id)
        except KeyError:
            raise MutaManagerError("Object is not managed.")

    def _run(self, host='0.0.0.0', port='8080'):

        handler = self._app.make_handler()
        self._app.loop.run_until_complete(
            self._app.loop.create_server(handler, host, port))
        print("Server started at http://{0}:{1}".format(host, port))
        self._app.loop.run_forever()

    def run(self, **aiohttp_kwargs):
        """ Run the manager
        :param aiohttp_kwargs: HTTP server parameters as defined for aiohttp
         `web.run_app <http://aiohttp.readthedocs.io/en/stable/web_reference.html#aiohttp.web.run_app>`_
        """
        # loop.run_forever()
        # web.run_app(self._app, **aiohttp_kwargs)
        self._run(**aiohttp_kwargs)

    def run_in_thread(self, **aiohttp_kwargs):
        t = threading.Thread(target=self._run, kwargs=aiohttp_kwargs)
        t.start()

