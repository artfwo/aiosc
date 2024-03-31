=====
aiosc
=====

aiosc is a minimalistic Open Sound Control (OSC) communication module
which uses asyncio for network operations and is compatible with the
asyncio event loop.

Installation
============

aiosc requires at least Python 3.7. It can be installed using pip::

    pip3 install aiosc

Alternatively, use ``--user`` option to install aiosc only for the current user::

    pip3 install --user aiosc

Usage
=====

To send OSC messages with ``aiosc``, create an asyncio datagram connection
endpoint of type ``aiosc.OSCProtocol``.

A datagram connection can be created with the ``aiosc.connect`` convenience
function or ``create_datagram_method`` of the asyncio event loop. Both have
the same set of arguments. Use the argument ``remote_addr`` to specify
the OSC server address and port as follows:

.. code-block:: python

    import asyncio
    import aiosc

    async def main():
        client = await aiosc.connect(remote_addr=('127.0.0.1', 8000))

        client.send('/hello/world')
        client.send('/a/b/cde', 1000, -1, 'hello', 1.234, 5.678)

    asyncio.run(main())

Subclassing ``aiosc.OSCProtocol`` is the recommended way of creating
OSC server implementations.

``aiosc.OSCProtocol`` provides a convenience async class method ``connect``
that can be used to bind the UDP socket and connect it to a remote endpoint
using ``local_addr`` and ``remote_addr`` arguments.

In a typical case, local address will look like ``('0.0.0.0', 9000)`` where
``9000`` is the port number and ``0.0.0.0`` address designates that the server
will be listening on all available network interfaces.

.. code-block:: python

    import asyncio
    import aiosc
    import sys

    class EchoServer(aiosc.OSCProtocol):
        def __init__(self):
            super().__init__(handlers={
                '/sys/exit': lambda addr, path, *args: sys.exit(0),
                '//*': self.echo,
            })

        def echo(self, addr, path, *args):
            print("incoming message from {}: {} {}".format(addr, path, args))

    async def main():
        server = await EchoServer.connect(local_addr=('0.0.0.0', 8000))
        await asyncio.get_running_loop().create_future()

    asyncio.run(main())

For more examples, see ``examples/``.

OSC address patterns
====================

``aiosc`` dispatches messages to handler methods using glob-style address
pattern matching as described in the OSC 1.0 specification. The ``//`` operator
from OSC 1.1 preliminary specification is also supported.

Examples:

* ``/hello/world`` matches ``/hello/world``.
* ``/hello/*`` matches ``/hello/world`` and ``/hello/sarah``.
* ``/{hello,goodbye}//world`` matches ``/hello/world`` and ``/goodbye/cruel/world``.
* ``//*`` matches any address.

Notes
=====

Bundles are not yet supported.

OSC data types are picked from the preliminary spec documented in Features
and Future of Open Sound Control version 1.1 for NIME paper. For example,
``I`` typetag is decoded to Impulse (aka "bang") which is passed around
as ``aiosc.Impulse`` singleton.

Suggestions, bug reports, issues and/or pull requests are, of course, welcome.

License
=======

Copyright (c) 2014 Artem Popov <artfwo@gmail.com>

aiosc is licensed under the MIT license, please see LICENSE file for details.
