#! /usr/bin/env python3

import asyncio
import aiosc

loop = asyncio.get_event_loop()
loop.run_until_complete(
    aiosc.send(('127.0.0.1', 9000), '/hello', 'world')
)
