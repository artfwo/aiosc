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
        # echo the message
        self.send(path, *args, addr=addr)

loop = asyncio.get_event_loop()

coro = loop.create_datagram_endpoint(EchoServer, local_addr=('127.0.0.1', 9000))
transport, protocol = loop.run_until_complete(coro)

loop.run_forever()
