::
              __       __    __
    .--.--.--|__.-----|  |--|  |--.-----.-----.-----.
    |  |  |  |  |__ --|     |  _  |  _  |     |  -__|
    |________|__|_____|__|__|_____|_____|__|__|_____|
                                       version 3.0.0


    ===================================
    wishbone_contrib.module.output.amqp
    ===================================

    Version: 3.0.0

    Submits messages to an AMQP service.
    ------------------------------------

        Submits messages to an AMQP service.

        Submits messages to an AMQP message broker.

        If <exchange> is not provided, no exchange will be created during initialisation.
        If <queue> is not provided, queue will be created during initialisation

        If <exchange> and <queue> are provided, they will both be created and
        bound during initialisation.

        <exchange> and <queue> can be event lookup values.

        Parameters:

            - selection(str)("data")
               |  The part of the event to submit externally.
               |  Use an empty string to refer to the complete event.

            - payload(str)(None)
               |  The string to submit.
               |  If defined takes precedence over `selection`.

            - host(str)("localhost")
               |  The host broker to connect to.

            - port(int)(5672)
               |  The port to connect to.

            - vhost(str)("/")
               |  The virtual host to connect to.

            - user(str)("guest")
               |  The username to authenticate.

            - password(str)("guest")
               |  The password to authenticate.

            - ssl(bool)(False)
               |  If True expects SSL

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

            - queue(str)("wishbone")
               |  The queue to declare and bind to <exchange>. This will also the
               |  the destination queue of the submitted messages unless
               |  <routing_key> is set to another value and <exchange_type> is
               |  "topic".

            - queue_durable(bool)(false)
               |  Declare a durable queue.

            - queue_exclusive(bool)(false)
               |  Declare an exclusive queue.

            - queue_auto_delete(bool)(true)
               |  Whether to autodelete the queue.

            - queue_declare(bool)(true)
               |  Whether to actually declare the queue.

            - queue_arguments(dict)({})
               |  Additional arguments for queue declaration.

            - routing_key(str)("")
               |  The routing key to use when submitting messages.

            - delivery_mode(int)(1)
               |  Sets the delivery mode of the messages.


        Queues:

            - inbox
               | Messages going to the defined broker.

