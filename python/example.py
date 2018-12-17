#!/usr/bin/env python

# 
# (c) 20018 team exitzero (goapsych0@exitzero.de)
# 

# links:
# https://github.com/Gallopsled/pwntools
# http://docs.pwntools.com/en/stable/
# https://medium.com/bugbountywriteup/learn-pwntools-step-by-step-8c96f2dba61a
# 


from __future__ import print_function
from pwn import *

# import other useful modules...
# import numpy
# 

# nc = remote("A domain or ip address", port)
#
# - send(payload) send payload
# - sendline(payload) send your payload ending with new line
# - sendafter(some_string, payload) after receiving some_string , send your payload
# - recvn(N) receive N(a number) characters
# - recvline() receive one line
# - recvlines(N) receive N(a number) lines
# - recvuntil(some_string) retrieve until some_string
# - nc.interactive() allow user input via terminal


# p32(0xcafebabe)
# convert 4 bit integer to little endian.
# -> be ba fe ca
# print("0xcafebabe: " + str(p32(0xcafebabe)))

