#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  default.py
#
#  Copyright 2017 Jelle Smet <development@smetj.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

from gevent import monkey; monkey.patch_all()

from wishbone.actor import ActorConfig
from wishbone.utils.test import getter
from wishbone.event import Event

from wishbone_output_amqp import AMQPOut
from amqp.connection import Connection
from amqp.exceptions import NotFound
from gevent import sleep
import requests
from requests.auth import HTTPBasicAuth
from amqp import Connection, basic_message
from wishbone.componentmanager import ComponentManager


def test_module_amqp_create_exchange_default():

    actor_config = ActorConfig('amqp', 100, 1, {}, "", disable_exception_handling=True)
    amqp = AMQPOut(actor_config, exchange="new_exchange_direct")
    amqp.pool.queue.inbox.disableFallThrough()
    amqp.start()

    sleep(1)
    response = requests.get("http://localhost:15672/api/exchanges/%2f/new_exchange_direct", auth=HTTPBasicAuth("guest", "guest"))
    assert response.json()["name"] == "new_exchange_direct"

    amqp.stop()


def test_module_amqp_create_exchange_type():

    actor_config = ActorConfig('amqp', 100, 1, {}, "", disable_exception_handling=True)
    amqp = AMQPOut(actor_config, exchange="new_exchange_fanout", exchange_type="fanout")
    amqp.pool.queue.inbox.disableFallThrough()
    amqp.start()

    sleep(1)
    response = requests.get("http://localhost:15672/api/exchanges/%2f/new_exchange_fanout", auth=HTTPBasicAuth("guest", "guest"))
    assert response.json()["type"] == "fanout"

    amqp.stop()


def test_module_amqp_create_exchange_durable():

    actor_config = ActorConfig('amqp', 100, 1, {}, "", disable_exception_handling=True)
    amqp = AMQPOut(actor_config, exchange="new_exchange_direct_1", exchange_durable=True)
    amqp.pool.queue.inbox.disableFallThrough()
    amqp.start()

    sleep(1)
    response = requests.get("http://localhost:15672/api/exchanges/%2f/new_exchange_direct_1", auth=HTTPBasicAuth("guest", "guest"))
    assert response.json()["durable"] is True
    amqp.stop()


def test_module_amqp_create_exchange_auto_delete():

    actor_config = ActorConfig('amqp', 100, 1, {}, "", disable_exception_handling=True)
    amqp = AMQPOut(actor_config, exchange="new_exchange_direct_2", exchange_auto_delete=False)
    amqp.pool.queue.inbox.disableFallThrough()
    amqp.start()

    sleep(1)
    response = requests.get("http://localhost:15672/api/exchanges/%2f/new_exchange_direct_2", auth=HTTPBasicAuth("guest", "guest"))
    assert response.json()["auto_delete"] is False
    amqp.stop()


def test_module_amqp_default_queue():

    actor_config = ActorConfig('amqp', 100, 1, {}, "", disable_exception_handling=True)
    amqp = AMQPOut(actor_config)

    amqp.pool.queue.inbox.disableFallThrough()
    amqp.start()

    sleep(1)
    response = requests.get("http://localhost:15672/api/queues/%2f/wishbone", auth=HTTPBasicAuth("guest", "guest"))
    assert response.json()["name"] == "wishbone"

    amqp.stop()


def test_module_amqp_default_queue_binding():

    actor_config = ActorConfig('amqp', 100, 1, {}, "", disable_exception_handling=True)
    amqp = AMQPOut(actor_config, exchange="wishbone")

    amqp.pool.queue.inbox.disableFallThrough()
    amqp.start()

    sleep(1)
    response = requests.get("http://localhost:15672/api/bindings/%2f/", auth=HTTPBasicAuth("guest", "guest"))

    ok = False
    for binding in response.json():
        if binding["source"] == "wishbone" and binding["destination"] == "wishbone":
            ok = True

    assert ok is True
    amqp.stop()


def test_module_amqp_default_queue_durable():

    actor_config = ActorConfig('amqp', 100, 1, {}, "", disable_exception_handling=True)
    amqp = AMQPOut(actor_config, queue="wishbone_durable", queue_durable=True)

    amqp.pool.queue.inbox.disableFallThrough()
    amqp.start()

    sleep(1)
    response = requests.get("http://localhost:15672/api/queues/%2f/wishbone_durable", auth=HTTPBasicAuth("guest", "guest"))
    assert response.json()["durable"] is True
    amqp.stop()


def test_module_amqp_default_queue_exclusive():

    actor_config = ActorConfig('amqp', 100, 1, {}, "", disable_exception_handling=True)
    amqp = AMQPOut(actor_config, queue="wishbone_exclusive", queue_exclusive=True)

    amqp.pool.queue.inbox.disableFallThrough()
    amqp.start()

    sleep(1)
    response = requests.get("http://localhost:15672/api/queues/%2f/wishbone_exclusive", auth=HTTPBasicAuth("guest", "guest"))
    assert response.json()["exclusive"] is True
    amqp.stop()


def test_module_amqp_default_queue_auto_delete():

    actor_config = ActorConfig('amqp', 100, 1, {}, "", disable_exception_handling=True)
    amqp = AMQPOut(actor_config, queue_auto_delete=True)

    amqp.pool.queue.inbox.disableFallThrough()
    amqp.start()

    sleep(1)
    response = requests.get("http://localhost:15672/api/queues/%2f/wishbone", auth=HTTPBasicAuth("guest", "guest"))
    assert response.json()["auto_delete"] is True
    amqp.stop()


def test_module_amqp_submit_message():

    actor_config = ActorConfig('amqp', 100, 1, {}, "", disable_exception_handling=True)
    amqp = AMQPOut(actor_config, exchange="wishbone_submit_message", queue="wishbone_submit_message", exchange_durable=False, queue_durable=False)

    amqp.pool.queue.inbox.disableFallThrough()
    amqp.start()

    event = Event("test")
    amqp.submit(event, "inbox")

    sleep(1)
    conn = Connection()
    conn.connect()
    channel = conn.channel()
    message = channel.basic_get("wishbone_submit_message")
    channel.close()
    conn.close()
    sleep(1)
    amqp.stop()
    assert message.body == "test"


def test_module_amqp_submit_message_encode():

    c = ComponentManager()
    protocol = c.getComponentByName("wishbone.protocol.encode.json")()

    actor_config = ActorConfig('amqp', 100, 1, {}, "", protocol=protocol, disable_exception_handling=True)
    amqp = AMQPOut(actor_config, exchange="wishbone_submit_encode", queue="wishbone_submit_encode", exchange_durable=False, queue_durable=False)

    amqp.pool.queue.inbox.disableFallThrough()
    amqp.start()

    event = Event({"one": 1})
    amqp.submit(event, "inbox")

    sleep(1)
    conn = Connection()
    conn.connect()
    channel = conn.channel()
    message = channel.basic_get("wishbone_submit_encode")
    channel.close()
    conn.close()
    sleep(1)
    amqp.stop()
    assert message.body == '{"one": 1}'
