#! /usr/bin/env python3

import asyncio
import aiosc

def protocol_factory():
    osc = aiosc.OSCProtocol({
        '//*': lambda addr, path, *args: print(addr, path, args)
    })
    return osc

async def main():
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(protocol_factory,
        local_addr=('127.0.0.1', 9000))

    await loop.create_future()

asyncio.run(main())
