#!/usr/bin/env python3

# 
# (c) 2020 team exitzero (goapsych0@exitzero.de)
# 

# asis-ctf-2020 baby-m5

# $ nc 66.172.10.203 2570

# Please submit a printable string X, such that sha384(X)[-6:] = 0d49ae and len(X) = 30
# Please submit a printable string X, such that sha1(X)[-6:] = c0ac03 and len(X) = 14
#
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# +  hi powerful coders! Your mission is to find weird hash collision,   +
# +  its baby level, so dont over-think please!!                         +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# | Options: 
# |    [B]aby hash function 
# |    [C]onditions 
# |    [R]eport collision! 
# |    [Q]uit


from pwn import *
import random
import string
import os
import hashlib
import re


min_lc = ord(b'!') # 33 # '!' ord(b'a')
len_lc = ord(b'~') - min_lc

def babymd5(m, n, x_head, y_head, x, y):
    if x.startswith(x_head) and y.startswith(y_head):
        for _ in range(m):
            xhash = hashlib.md5(x.encode('utf-8')).hexdigest()
            x = xhash
        for _ in range(n):
            yhash = hashlib.md5(y.encode('utf-8')).hexdigest()
            y = yhash
        if xhash == yhash:
            return True
    return False


# (m, n, x_head, y_head) = (195, 124, 'Mhy', 'dead')
# (m, n, x_head, y_head) = (142,   7, 'SB3', 'dead')

def gen_hash(len):
    while True:
        ba = bytearray(os.urandom(int(len)))
        for i, b in enumerate(ba):
            ba[i] = min_lc + b % len_lc # convert 0..255 to 97..122
        yield ba



conn = remote('66.172.10.203', 2570)
task = conn.recvline()

print("task: ", task)
result = re.match(r'.* ((md|sha)\d+)\(X\)\[-(\d):\] = (\w+) and len\(X\) = (\d+)', task.decode('ascii'))

if result:
    print("res: ", result.group(1), result.group(3), result.group(4), result.group(5))
else:
    exit(1)

hasher = result.group(1)
expect = result.group(4)
slen   = result.group(5)

for s in gen_hash(slen):
    if hasher == 'sha1':
        sh = hashlib.sha1(s).hexdigest()
    if hasher == 'sha224':
        sh = hashlib.sha224(s).hexdigest()
    if hasher == 'sha256':
        sh = hashlib.sha256(s).hexdigest()
    if hasher == 'sha384':
        sh = hashlib.sha384(s).hexdigest()
    if hasher == 'sha512':
        sh = hashlib.sha512(s).hexdigest()
    if hasher == 'md5':
        sh = hashlib.md5(s).hexdigest()

    sh6 = sh[-6:]
    if expect == sh6:
        print(s.decode('ascii'))
        conn.send(s)
        conn.send(b'\r\n')
        break
    
conn.recvlines(9)

conn.send('C')
conn.send(b'\r\n')
cond = conn.recvline()

conn.recvlines(5)

print("cond: ", cond)
# cond:  b"| (m, n, x_head, y_head) = (309, 274, 'skX', 'dead')\n"
result = re.match(r'.* = \((\d+), (\d+), \'(\w+)\', \'dead\'\)', cond.decode('ascii'))
print("m      = ", result.group(1))
print("n      = ", result.group(2))
print("x_head = ", result.group(3))
m = int(result.group(1))
n = int(result.group(2))

for s in gen_hash(29):
    x_start = result.group(3) + s.decode('ascii')
    x1 = x_start
    for _ in range(m - n):
        x_hash = hashlib.md5(x1.encode('utf-8')).hexdigest()
        x1 = x_hash
    
    if x_hash.startswith('dead'):
        y = x_hash
        x = x_start
        if babymd5(int(result.group(1)), int(result.group(2)), result.group(3), 'dead', x, y):
            print("MATCH!")
        break

print("x:", x)
print("y:", y)

conn.sendline('r')
conn.sendline(x)
conn.sendline(y)

conn.interactive()
        
conn.close()
