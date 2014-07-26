#! /usr/bin/env python3

import asyncio
import aiosc

def protocol_factory():
    osc = aiosc.OSCProtocol({
        '//*': lambda addr, path, *args: print(addr, path, args)
    })
    return osc

loop = asyncio.get_event_loop()
coro = loop.create_datagram_endpoint(protocol_factory, local_addr=('127.0.0.1', 9000))
transport, protocol = loop.run_until_complete(coro)
loop.run_forever()
