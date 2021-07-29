#! /usr/bin/env python3

import asyncio
import aiosc

async def main():
    await aiosc.send(('127.0.0.1', 9000), '/hello', 'world')

asyncio.run(main())
