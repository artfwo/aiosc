#! /usr/bin/env python3

import asyncio
import aiosc

async def main():
    client = await aiosc.connect(remote_addr=('127.0.0.1', 9000))
    client.send('/hello', 'world')

asyncio.run(main())
