=====
aiosc
=====

This is an experimental minimalistic Open Sound Control (OSC) communication
module which uses asyncio for network operations and is compatible with the
asyncio event loop.

Installation
============

aiosc requires at least Python 3.5. It can be installed using pip::

    pip3 install aiosc

Or use `--user` option to install aiosc locally::

    pip3 install --user aiosc

Usage
=====

To send an OSC message just use ``aiosc.send``:

.. code-block:: python

    import asyncio
    import aiosc

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        aiosc.send(('127.0.0.1', 9000), '/hello', 'world')
    )

To implement an OSC server with ``aiosc`` you should create an UDP endpoint
using ``aiosc.OSCProtocol`` as the protocol. ``OSCProtocol`` can be subclassed
or directly constructed with a dictionary mapping OSC address patterns to
handler methods for incoming messages:

.. code-block:: python

    class EchoServer(aiosc.OSCProtocol):
        def __init__(self):
            super().__init__(handlers={
                '/sys/exit': lambda addr, path, *args: sys.exit(0),
                '//*': self.echo,
            })

        def echo(self, addr, path, *args):
            print("incoming message from {}: {} {}".format(addr, path, args))

    loop = asyncio.get_event_loop()
    coro = loop.create_datagram_endpoint(EchoServer, local_addr=('127.0.0.1', 9000))
    transport, protocol = loop.run_until_complete(coro)

    loop.run_forever()

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

Contrary to most OSC implementations, OSC data types are picked from the
preliminary spec documented in Features and Future of Open Sound Control
version 1.1 for NIME paper. For example, 'I' typetag is decoded to Impulse
(aka "bang") which is passed around as ``aiosc.Impulse`` singleton.

Suggestions, bug reports, issues and/or pull requests are, of course, welcome.

License
=======

Copyright (c) 2014 Artem Popov <artfwo@gmail.com>

aiosc is licensed under the MIT license, please see LICENSE file for details.
