::

              __       __    __
    .--.--.--|__.-----|  |--|  |--.-----.-----.-----.
    |  |  |  |  |__ --|     |  _  |  _  |     |  -__|
    |________|__|_____|__|__|_____|_____|__|__|_____|


    ===================================
    wishbone_contrib.module.output.amqp
    ===================================

    Version: 3.1.0

    Submits messages to AMQP.
    -------------------------

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

