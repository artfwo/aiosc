# aiosc - a minimalistic OSC communication module using asyncio
#
# Copyright (c) 2014 Artem Popov <artfwo@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import asyncio
import re
import struct


def singleton(cls):
    cls.__call__ = lambda self: self
    return cls()


@singleton
class Impulse:
    pass


OSC_ADDR_REGEXP = r'[^ #*,/?[\]{}]'
OSC_ADDR_SLASH_REGEXP = r'[^ #*,?[\]{}]'
NTP_EPOCH_OFFSET = 2208988800
NOW = struct.pack('>Q', 1)


# translate osc address pattern to regexp for use in message handlers
def translate_pattern(pattern):
    result = ''
    i = 0
    while i < len(pattern):
        c = pattern[i]
        if c == '/':
            j = i + 1
            if j < len(pattern) and pattern[j] == '/':
                result += OSC_ADDR_SLASH_REGEXP + r'*\/'
                i = j
            else:
                result += re.escape(c)
        elif c == '?':
            result += OSC_ADDR_REGEXP
        elif c == '*':
            result += OSC_ADDR_REGEXP + '*'
        elif c == '[':
            j = pattern.index(']', i)
            sub = pattern[i+1:j]
            result += '['
            if sub.startswith('!'):
                sub = sub[1:]
                result += '^'
            result += '-'.join([re.escape(s) for s in sub.split('-')])
            result += ']'
            i = j
        elif c == '{':
            j = pattern.index('}', i)
            sub = pattern[i+1:j]
            result += '('
            result += '|'.join([re.escape(s) for s in sub.split(',')])
            result += ')'
            i = j
        else:
            result += re.escape(c)
        i += 1
    return '^' + result + '$'


# read padded string from the beginning of a packet and return (value, tail)
def read_string(packet):
    actual_len = packet.index(b'\x00')
    padded_len = ((actual_len + 4) // 4) * 4
    return str(packet[:actual_len], 'ascii'), packet[padded_len:]


# read padded blob from the beginning of a packet and return (value, tail)
def read_blob(packet):
    actual_len, tail = struct.unpack('>I', packet[:4])[0], packet[4:]
    padded_len = ((actual_len + 3) // 4) * 4
    return tail[:actual_len], tail[padded_len:]


def parse_message(packet):
    tail = packet
    path, tail = read_string(tail)
    type_tag, tail = read_string(tail)
    args = []

    for t in type_tag[1:]:
        if t == 'i':
            len = 4
            value, tail = struct.unpack('>i', tail[:len])[0], tail[len:]
        elif t == 'f':
            len = 4
            value, tail = struct.unpack('>f', tail[:len])[0], tail[len:]
        elif t == 'd':
            len = 8
            value, tail = struct.unpack('>d', tail[:len])[0], tail[len:]
        elif t == 'h':
            len = 8
            value, tail = struct.unpack('>q', tail[:len])[0], tail[len:]
        elif t == 's':
            value, tail = read_string(tail)
        elif t == 'b':
            value, tail = read_blob(tail)
        elif t == 'T':
            value = True
        elif t == 'F':
            value = False
        elif t == 'N':
            value = None
        elif t == 'I':
            value = Impulse
        else:
            raise RuntimeError('Unable to parse type "{}"'.format(t))
        args.append(value)

    return (path, args)


# yield (path, args) for each message in bundle, ignoring timetags
def parse_bundle(packet):
    tail = packet[16:]

    while tail:
        size, tail = struct.unpack('>I', tail[:4])[0], tail[4:]
        element, tail = tail[:size], tail[size:]

        if element.startswith(b'#bundle'):
            yield from parse_bundle(element)
        else:
            yield parse_message(element)


# convert string to padded osc string
def pack_string(s):
    b = bytes(s + '\x00', 'ascii')
    width = ((len(b) + 3) // 4) * 4
    return b.ljust(width, b'\x00')


# convert bytes to padded osc blob
def pack_blob(b):
    b = bytes(struct.pack('>I', len(b)) + b)
    width = ((len(b) + 3) // 4) * 4
    return b.ljust(width, b'\x00')


def pack_message(path, *args):
    result = b''
    typetag = ','

    for arg in args:
        if type(arg) == int:
            result += struct.pack('>i', arg)
            typetag += 'i'
        elif type(arg) == float:
            result += struct.pack('>f', arg)
            typetag += 'f'
        elif type(arg) == str:
            result += pack_string(arg)
            typetag += 's'
        elif type(arg) == bytes:
            result += pack_blob(arg)
            typetag += 'b'
        elif type(arg) == bool:
            typetag += 'T' if arg else 'F'
        elif arg is Impulse:
            typetag += 'I'
        elif arg is None:
            typetag += 'N'
        else:
            raise NotImplementedError('Unable to pack {}'.format(type(arg)))

    result = pack_string(path) + pack_string(typetag) + result
    return result


# convert unix time to a 64-bit ntp timetag
def pack_timetag(t):
    seconds = int(t) + NTP_EPOCH_OFFSET
    fraction = int((t % 1.0) * (1 << 32))
    return struct.pack('>II', seconds, fraction)


# pack an iterable of (path, *args) tuples into bundle
def pack_bundle(messages, timetag=None):
    result = b'#bundle\x00'
    result += NOW if timetag is None else pack_timetag(timetag)

    for path, *args in messages:
        data = pack_message(path, *args)
        result += struct.pack('>I', len(data)) + data

    return result


class OSCProtocol(asyncio.DatagramProtocol):
    def __init__(self, handlers=None):
        super().__init__()
        self._handlers = []
        self.transport = None

        if handlers:
            for pattern, handler in handlers.items():
                self.add_handler(pattern, handler)

    @classmethod
    async def connect(cls, **kwargs):
        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(cls, **kwargs)
        return protocol

    def add_handler(self, pattern, handler):
        pattern_re = re.compile(translate_pattern(pattern))
        self._handlers.append((pattern_re, handler))

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        if data.startswith(b'#bundle'):
            messages = parse_bundle(data)
        else:
            messages = [parse_message(data)]

        # dispatch the messages
        for path, args in messages:
            for pattern_re, handler in self._handlers:
                if pattern_re.match(path):
                    handler(addr, path, *args)

    def send(self, path, *args, addr=None):
        return self.transport.sendto(pack_message(path, *args), addr=addr)

    def send_bundle(self, messages, timetag=None, addr=None):
        return self.transport.sendto(pack_bundle(messages, timetag=timetag), addr=addr)

    def close(self):
        if self.transport:
            self.transport.close()
            self.transport = None


async def connect(**kwargs):
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(OSCProtocol, **kwargs)
    return protocol
