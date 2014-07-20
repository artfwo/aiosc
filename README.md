aiosc
=====

This is an experimental minimalistic OSC communication module which uses
asyncio instead of sockets and is compatible with the asyncio event loop.

Installation
------------

aiosc requires at least Python 3.4. It can be installed using pip:

    pip3 install https://github.com/artfwo/aiosc/tarball/master
    pip3 install --user https://github.com/artfwo/aiosc/tarball/master

Usage
-----

    import asyncio
    import aiosc

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        aiosc.send(('127.0.0.1', 9000), '/hello', 'world')
    )

For more examples, see `examples/`

Notes
-----

Bundles are not yet supported.

Message handlers can be added using glob-style address pattern matching.

Contrary to most OSC implementations, OSC data types are picked from the
preliminary spec documented in Features and Future of Open Sound Control
version 1.1 for NIME paper.

For example, 'I' typetag is decoded to Impulse (aka "bang") which is
implemented using singleton.

Suggestions, bug reports, issues and/or pull requests are, of course, welcome.

License
-------

Copyright (c) 2014 Artem Popov <artfwo@gmail.com>

aiosc is licensed under the MIT license, please see LICENSE file for details.
