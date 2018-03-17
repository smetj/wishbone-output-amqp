#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  amqpout.py
#
#  Copyright 2016 Jelle Smet <development@smetj.net>
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
from wishbone.module import OutputModule
from amqp.connection import Connection
from amqp import basic_message
from gevent import sleep
from gevent.event import Event


class AMQPOut(OutputModule):
    '''
    Submits messages to AMQP.

    Submits messages to an AMQP message broker.

    If <exchange> is not provided, no exchange will be created during initialisation.
    If <queue> is not provided, queue will be created during initialisation

    If <exchange> and <queue> are provided, they will both be created and
    bound during initialisation.

    Parameters::

        - delivery_mode(int)(1)
           |  Sets the delivery mode of the messages.

        - exchange(str)("")
           |  The exchange to declare.

        - exchange_type(str)("direct")
           |  The exchange type to create. (direct, topic, fanout)

        - exchange_durable(bool)(false)
           |  Declare a durable exchange.

        - exchange_auto_delete(bool)(true)
           |  If set, the exchange is deleted when all queues have finished using it.

        - exchange_passive(bool)(false)
           |  If set, the server will not create the exchange. The client can use
           |  this to check whether an exchange exists without modifying the server state.

        - exchange_arguments(dict)({})
           |  Additional arguments for exchange declaration.

        - heartbeat(int)(0)
            | Enable AMQP heartbeat. The value is the interval in seconds.
            | 0 disables heartbeat support.

        - host(str)("localhost:5672")
           |  The host broker to connect to.

        - native_events(bool)(False)
           |  Outgoing events should be native Wishbone events

        - parallel_streams(int)(1)
           |  The number of outgoing parallel data streams.

        - password(str)("guest")
           |  The password to authenticate.

        - payload(str)(None)
           |  The string to submit.
           |  If defined takes precedence over `selection`.

        - queue(str)("wishbone")
           |  The queue to declare and bind to <exchange>. This will also the
           |  the destination queue of the submitted messages unless
           |  <routing_key> is set to another value and <exchange_type> is
           |  "topic".

        - queue_arguments(dict)({})
           |  Additional arguments for queue declaration.

        - queue_auto_delete(bool)(true)
           |  Whether to autodelete the queue.

        - queue_declare(bool)(true)
           |  Whether to actually declare the queue.

        - queue_durable(bool)(false)
           |  Declare a durable queue.

        - queue_exclusive(bool)(false)
           |  Declare an exclusive queue.

        - routing_key(str)("")
           |  The routing key to use when submitting messages.

        - selection(str)("data")
           |  The part of the event to submit externally.

        - ssl(bool)(False)
           |  If True expects SSL

        - user(str)("guest")
           |  The username to authenticate.

        - vhost(str)("/")
           |  The virtual host to connect to.


    Queues::

        - inbox
           | Messages going to the defined broker.
    '''

    def __init__(self, actor_config, native_events=False, selection="data", payload=None, parallel_streams=1,
                 host="localhost:5672", vhost="/", user="guest", password="guest", ssl=False, heartbeat=0,
                 exchange="wishbone", exchange_type="direct", exchange_durable=False, exchange_auto_delete=True, exchange_passive=False,
                 exchange_arguments={},
                 queue="wishbone", queue_durable=False, queue_exclusive=False, queue_auto_delete=True, queue_declare=True,
                 queue_arguments={},
                 routing_key="", delivery_mode=1):

        OutputModule.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")

        self.connect = Event()
        self.connect.set()

        self.do_consume = Event()
        self.do_consume.clear()

        self.channel = None

        self.connected = False

    def heartbeat(self):

        while self.loop():
            sleep(self.kwargs.heartbeat)
            try:
                if self.connected:
                    self.connection.send_heartbeat()
            except Exception as err:
                self.logging.error("Failed to send heartbeat. Reason: %s" % (err))

    def preHook(self):
        self._queue_arguments = dict(self.kwargs.queue_arguments)
        self._exchange_arguments = dict(self.kwargs.exchange_arguments)
        self.sendToBackground(self.setupConnectivity)

    def consume(self, event):

        self.do_consume.wait()
        if self.channel is None:
            self.logging.error("Failed to submit message. Initial connection not established yet.")
        else:
            data = self.getDataToSubmit(event)
            data = self.encode(data)
            message = basic_message.Message(
                body=data,
                delivery_mode=self.kwargs.delivery_mode
            )

            try:
                self.channel.basic_publish(
                    message,
                    exchange=self.kwargs.exchange,
                    routing_key=self.kwargs.routing_key
                )
            except Exception as err:
                self.logging.error("Failed to submit event to broker. Reason: %s" % (err))
                self.connected = False
                self.connect.set()

    def setupConnectivity(self):

        if self.kwargs.heartbeat > 0:
            self.logging.info("Sending heartbeat every %s seconds." % (self.kwargs.heartbeat))
            self.sendToBackground(self.heartbeat)

        while self.loop():
            self.connect.wait()
            self.logging.debug("Connecting to %s" % (self.kwargs.host))
            try:
                self.connection = Connection(
                    host=self.kwargs.host,
                    heartbeat=self.kwargs.heartbeat,
                    virtual_host=self.kwargs.vhost,
                    userid=self.kwargs.user,
                    password=self.kwargs.password,
                    ssl=self.kwargs.ssl,
                    connect_timeout=5
                )
                self.connection.connect()
                self.channel = self.connection.channel()

                if self.kwargs.exchange != "":
                    self.channel.exchange_declare(
                        self.kwargs.exchange,
                        self.kwargs.exchange_type,
                        durable=self.kwargs.exchange_durable,
                        auto_delete=self.kwargs.exchange_auto_delete,
                        passive=self.kwargs.exchange_passive,
                        arguments=self._exchange_arguments
                    )
                    self.logging.debug("Declared exchange %s." % (self.kwargs.exchange))

                if self.kwargs.queue_declare:
                    self.channel.queue_declare(
                        self.kwargs.queue,
                        durable=self.kwargs.queue_durable,
                        exclusive=self.kwargs.queue_exclusive,
                        auto_delete=self.kwargs.queue_auto_delete,
                        arguments=self._queue_arguments
                    )
                    self.logging.debug("Declared queue %s." % (self.kwargs.queue))

                if self.kwargs.exchange != "":
                    self.channel.queue_bind(
                        self.kwargs.queue,
                        self.kwargs.exchange,
                        routing_key=self.kwargs.routing_key
                    )
                    self.logging.debug("Bound queue %s to exchange %s." % (self.kwargs.queue, self.kwargs.exchange))

                self.logging.info("Connected to broker %s." % (self.kwargs.host))
            except Exception as err:
                self.logging.error("Failed to connect to broker.  Reason %s " % (err))
                sleep(1)
            else:
                self.do_consume.set()
                self.connect.clear()
                self.connected = True

    def postHook(self):
        try:
            self.channel.close()
        except Exception as err:
            del(err)
        try:
            self.connection.close()
        except Exception as err:
            del(err)
