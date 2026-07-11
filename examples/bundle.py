#! /usr/bin/env python3

import asyncio
import time
import aiosc

async def main():
    client = await aiosc.connect(remote_addr=('127.0.0.1', 9000))
    client.send_bundle([('/hello', 'world'), ('/answer', 42)], timetag=time.time() + 3.0)

asyncio.run(main())
