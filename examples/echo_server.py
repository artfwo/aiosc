#! /usr/bin/env python3

import asyncio
import aiosc

class EchoServer(aiosc.OSCProtocol):
    def __init__(self):
        super().__init__(handlers={
            '/sys/exit': self.exit,
            '//*': self.echo,
        })

    def exit(self, *args):
        asyncio.get_event_loop().stop()

    def echo(self, addr, path, *args):
        print("incoming message from {}: {} {}".format(addr, path, args))
        # send the message back
        self.send(path, *args, addr=addr)

async def main():
    loop = asyncio.get_running_loop()
    echo = await EchoServer.connect(local_addr=('127.0.0.1', 9000))
    await loop.create_future()

asyncio.run(main())
