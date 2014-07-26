#! /usr/bin/env python3

import asyncio
import aiosc

loop = asyncio.get_event_loop()
coro = loop.create_datagram_endpoint(aiosc.OSCProtocol, remote_addr=('127.0.0.1', 9000))
transport, client = loop.run_until_complete(coro)

# send a bunch of messages using the same client
tasks = [client.send('/hello', i) for i in range(10)]
asyncio.wait(tasks)
