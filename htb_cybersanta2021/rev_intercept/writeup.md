# HTB CyberSanta 2021 - Rev Intercept

## Description
We get two files, a data file that captured some (tcp) network traffic and an assembly code snippet of an encryption function.
The assumption is that the data that was transferred was encrypted in some way.

## Encryption - intercept.asm
The given asm looks like this:

```assembly
	.text
	.globl	state
	.bss
	.type	state, @object
	.size	state, 1
state:
	.zero	1
	.text
	.globl	do_encrypt
	.type	do_encrypt, @function
do_encrypt:
	push	rbp
	mov	rbp, rsp
	mov	eax, edi
	mov	BYTE PTR [rbp-4], al
	movzx	eax, BYTE PTR state[rip]
	add	eax, 19
	xor	BYTE PTR [rbp-4], al
	movzx	eax, BYTE PTR state[rip]
	add	eax, 55
	mov	BYTE PTR state[rip], al
	movzx	eax, BYTE PTR [rbp-4]
	pop	rbp
	ret
```

Here it is do_encrypt(), as the name suggests (but who knows) seems to "encrypt" one byte at a time.
On function entry, after preserving current frame pointer and pointing to the stack:
```
	push	rbp
	mov	rbp, rsp
```
the first (and only) arg (EDI) is written to the stack, that is ... into a local variable. Since AL is used that should be some 8 Bit value.
```
	mov	eax, edi
	mov	BYTE PTR [rbp-4], al
```
then I was struggling a bit about the [rip] syntax but you can read about it [here](https://cs61.seas.harvard.edu/site/2021/Asm/#rip-relative-addressing).
From the asm snippet we can see there is some global object with size 1 Byte put into .bss were we can expect it to be initialized to zero. Here we load the value of the global state variable into EAX and 19 to it.
```
	movzx	eax, BYTE PTR state[rip]
	add	eax, 19
```
Next xor the input (plain text) byte with this modified state value (initially 0 + 19).
```
	xor	BYTE PTR [rbp-4], al
```
Finally update the global state variable by adding 55 to it (note, before the state value was just fetched and 15 was added, it was not modified in memory)
```
	movzx	eax, BYTE PTR state[rip]
	add	eax, 55
	mov	BYTE PTR state[rip], al
```
So after the first byte state should be 55 and the next byte should be XOR'ed with a value of 55+19=74.
Last but not least return return the modified byte (and restore stack pointer).


### python function
I came up with basically this python code that should re-assmble the asm crypt code. This should be able to do the reversing as well right ...
```python
state = 0
def crypt(ct):
    global state
    x = (state + 19) % 256
    res = (ct ^ x)
    state = (state + 55)
    return res
```

So far so good but what to feed into this function? Let's look into the network data ...

## Network data - intercept.pcap

$ tcpdump -r intercept.pcap -X
```
reading from file intercept.pcap, link-type IPV4 (Raw IPv4)
21:04:29.309412 IP localhost.31337 > 46.16.18.255.1337: Flags [S.], seq 0:6, ack 0, win 8192, length 6
	0x0000:  4500 002e 0001 0000 4006 bab9 7f00 0001  E.......@.......
	0x0010:  2e10 12ff 7a69 0539 0000 0000 0000 0000  ....zi.9........
	0x0020:  5012 2000 86fc 0000 5b2f edd4 8019       P.......[/....
21:04:29.309688 IP localhost.31337 > 46.16.18.255.1337: Flags [S.], seq 0:16, ack 0, win 8192, length 16
	0x0000:  4500 0038 0001 0000 4006 baaf 7f00 0001  E..8....@.......
	0x0010:  2e10 12ff 7a69 0539 0000 0000 0000 0000  ....zi.9........
	0x0020:  5012 2000 04b5 0000 14e7 eb76 5119 d4fe  P..........vQ...
	0x0030:  6223 f1d1 9846 38a9                      b#...F8.
21:04:29.309872 IP localhost.31337 > 46.16.18.255.1337: Flags [S.], seq 0:40, ack 0, win 8192, length 40
	0x0000:  4500 0050 0001 0000 4006 ba97 7f00 0001  E..P....@.......
	0x0010:  2e10 12ff 7a69 0539 0000 0000 0000 0000  ....zi.9........
	0x0020:  5012 2000 343b 0000 816b 5419 dac0 7b27  P...4;...kT...{'
	0x0030:  eed9 d35e 09fd ef65 521a c587 7a24 eed1  ...^...eR...z$..
	0x0040:  9b0c 0ae9 f16d 4c02 cc86 773b faa8 924a  .....mL...w;...J
21:04:29.310054 IP localhost.31337 > 46.16.18.255.1337: Flags [S.], seq 0:48, ack 0, win 8192, length 48
	0x0000:  4500 0058 0001 0000 4006 ba8f 7f00 0001  E..X....@.......
	0x0010:  2e10 12ff 7a69 0539 0000 0000 0000 0000  ....zi.9........
	0x0020:  5012 2000 c926 0000 2ae9 a12a 2f1d d792  P....&..*..*/...
	0x0030:  3d39 eea7 8d59 09f9 f57b 2a16 ddc8 7d33  =9...Y...{*...}3
	0x0040:  ada5 8f12 08d4 f737 7552 83da 1168 a3e6  .......7uR...h..
	0x0050:  cc07 5e8c e920 774e                      ..^...wN
21:04:29.310241 IP localhost.31337 > 46.16.18.255.1337: Flags [S.], seq 0:39, ack 0, win 8192, length 39
	0x0000:  4500 004f 0001 0000 4006 ba98 7f00 0001  E..O....@.......
	0x0010:  2e10 12ff 7a69 0539 0000 0000 0000 0000  ....zi.9........
	0x0020:  5012 2000 d842 0000 f88d 483f b1bb 8a44  P....B....H?...D
	0x0030:  0884 af7d 69e2 c587 4b3b b3be 695d 4fd5  ...}i...K;..i]O.
	0x0040:  a97b 27e7 d7d0 572c f0bf 6654 05db fe    .{'...W,..fT...
21:04:29.310421 IP localhost.31337 > 46.16.18.255.1337: Flags [S.], seq 0:72, ack 0, win 8192, length 72
	0x0000:  4500 0070 0001 0000 4006 ba77 7f00 0001  E..p....@..w....
	0x0010:  2e10 12ff 7a69 0539 0000 0000 0000 0000  ....zi.9........
	0x0020:  5012 2000 164a 0000 4225 e19b 8248 13e4  P....J..B%...H..
	0x0030:  b96a 4e17 8a95 776f e1d8 800b 0bf7 f070  .jN...wo.......p
	0x0040:  5719 c0c3 7834 a8f7 a26f 1feb be3d 7119  W...x4...o...=q.
	0x0050:  dad6 6427 d5f5 8b42 59ea bc3f 3626 ded4  ..d'...BY..?6&..
	0x0060:  6621 d3b0 ca44 1afc e552 274b d6da 1f2a  f!...D...R'K...*
```

I used wireshark to capture the tcp-payload as raw bytes and put them into some python lists:
```python

p1_ = [ 0x5b, 0x2f, 0xed, 0xd4, 0x80, 0x19 ]

p2_ = [ 0x14, 0xe7, 0xeb, 0x76, 0x51, 0x19, 0xd4, 0xfe, 0x62, 0x23, 0xf1, 0xd1, 0x98, 0x46, 0x38, 0xa9 ]

p3_ = [ 0x81, 0x6b, 0x54, 0x19, 0xda, 0xc0, 0x7b, 0x27, 0xee, 0xd9, 0xd3, 0x5e, 0x09, 0xfd, 0xef, 0x65, 0x52, 0x1a, 0xc5, 0x87, 0x7a, 0x24, 0xee, 0xd1, 0x9b, 0x0c, 0x0a, 0xe9, 0xf1, 0x6d, 0x4c, 0x02, 0xcc, 0x86, 0x77, 0x3b, 0xfa, 0xa8, 0x92, 0x4a ]

p4_ = [ 0x2a, 0xe9, 0xa1, 0x2a, 0x2f, 0x1d, 0xd7, 0x92, 0x3d, 0x39, 0xee, 0xa7, 0x8d, 0x59, 0x09, 0xf9, 0xf5, 0x7b, 0x2a, 0x16, 0xdd, 0xc8, 0x7d, 0x33, 0xad, 0xa5, 0x8f, 0x12, 0x08, 0xd4, 0xf7, 0x37, 0x75, 0x52, 0x83, 0xda, 0x11, 0x68, 0xa3, 0xe6, 0xcc, 0x07, 0x5e, 0x8c, 0xe9, 0x20, 0x77, 0x4e ]

p5_ = [ 0xf8, 0x8d, 0x48, 0x3f, 0xb1, 0xbb, 0x8a, 0x44, 0x08, 0x84, 0xaf, 0x7d, 0x69, 0xe2, 0xc5, 0x87, 0x4b, 0x3b, 0xb3, 0xbe, 0x69, 0x5d, 0x4f, 0xd5, 0xa9, 0x7b, 0x27, 0xe7, 0xd7, 0xd0, 0x57, 0x2c, 0xf0, 0xbf, 0x66, 0x54, 0x05, 0xdb, 0xfe ]

p6_ = [ 0x42, 0x25, 0xe1, 0x9b, 0x82, 0x48, 0x13, 0xe4, 0xb9, 0x6a, 0x4e, 0x17, 0x8a, 0x95, 0x77, 0x6f, 0xe1, 0xd8, 0x80, 0x0b, 0x0b, 0xf7, 0xf0, 0x70, 0x57, 0x19, 0xc0, 0xc3, 0x78, 0x34, 0xa8, 0xf7, 0xa2, 0x6f, 0x1f, 0xeb, 0xbe, 0x3d, 0x71, 0x19, 0xda, 0xd6, 0x64, 0x27, 0xd5, 0xf5, 0x8b, 0x42, 0x59, 0xea, 0xbc, 0x3f, 0x36, 0x26, 0xde, 0xd4, 0x66, 0x21, 0xd3, 0xb0, 0xca, 0x44, 0x1a, 0xfc, 0xe5, 0x52, 0x27, 0x4b, 0xd6, 0xda, 0x1f, 0x2a ]
```

I was struggling a bit here since wireshark reported some warning (out-of-order) sequence. As well as when looking at the tcp traffic with the "Follow TCP Stream" option in wireshark and comparing to the payload data there is some mismatch. In the "follow-stream" view not all bytes are displayed and frame 5 is skipped. You can see that there is a mismatch in the reported "bytes-in-flight" vs. actual TCP payload byte count. I just copied all data after the first 40 bytes of the packet and that is what the six lists above show.



## final python script

[crypt.py](crypt.py)

```python
######### PAYLOAD 1 - LEN 6 bytes
p1_ = [ 0x5b, 0x2f, 0xed, 0xd4, 0x80, 0x19 ]

######### PAYLOAD 1 - LEN 16 bytes
p2_ = [ 0x14, 0xe7, 0xeb, 0x76, 0x51, 0x19, 0xd4, 0xfe, 0x62, 0x23, 0xf1, 0xd1, 0x98, 0x46, 0x38, 0xa9 ]

######### PAYLOAD 1 - LEN 40 bytes
p3_ = [ 0x81, 0x6b, 0x54, 0x19, 0xda, 0xc0, 0x7b, 0x27, 0xee, 0xd9, 0xd3, 0x5e, 0x09, 0xfd, 0xef, 0x65, 0x52, 0x1a, 0xc5, 0x87, 0x7a, 0x24, 0xee, 0xd1, 0x9b, 0x0c, 0x0a, 0xe9, 0xf1, 0x6d, 0x4c, 0x02, 0xcc, 0x86, 0x77, 0x3b, 0xfa, 0xa8, 0x92, 0x4a ]

######### PAYLOAD 1 - LEN 48 bytes
p4_ = [ 0x2a, 0xe9, 0xa1, 0x2a, 0x2f, 0x1d, 0xd7, 0x92, 0x3d, 0x39, 0xee, 0xa7, 0x8d, 0x59, 0x09, 0xf9, 0xf5, 0x7b, 0x2a, 0x16, 0xdd, 0xc8, 0x7d, 0x33, 0xad, 0xa5, 0x8f, 0x12, 0x08, 0xd4, 0xf7, 0x37, 0x75, 0x52, 0x83, 0xda, 0x11, 0x68, 0xa3, 0xe6, 0xcc, 0x07, 0x5e, 0x8c, 0xe9, 0x20, 0x77, 0x4e ]
######### PAYLOAD 1 - LEN 39 bytes
p5_ = [ 0xf8, 0x8d, 0x48, 0x3f, 0xb1, 0xbb, 0x8a, 0x44, 0x08, 0x84, 0xaf, 0x7d, 0x69, 0xe2, 0xc5, 0x87, 0x4b, 0x3b, 0xb3, 0xbe, 0x69, 0x5d, 0x4f, 0xd5, 0xa9, 0x7b, 0x27, 0xe7, 0xd7, 0xd0, 0x57, 0x2c, 0xf0, 0xbf, 0x66, 0x54, 0x05, 0xdb, 0xfe ]
######### PAYLOAD 1 - LEN 72 bytes
p6_ = [ 0x42, 0x25, 0xe1, 0x9b, 0x82, 0x48, 0x13, 0xe4, 0xb9, 0x6a, 0x4e, 0x17, 0x8a, 0x95, 0x77, 0x6f, 0xe1, 0xd8, 0x80, 0x0b, 0x0b, 0xf7, 0xf0, 0x70, 0x57, 0x19, 0xc0, 0xc3, 0x78, 0x34, 0xa8, 0xf7, 0xa2, 0x6f, 0x1f, 0xeb, 0xbe, 0x3d, 0x71, 0x19, 0xda, 0xd6, 0x64, 0x27, 0xd5, 0xf5, 0x8b, 0x42, 0x59, 0xea, 0xbc, 0x3f, 0x36, 0x26, 0xde, 0xd4, 0x66, 0x21, 0xd3, 0xb0, 0xca, 0x44, 0x1a, 0xfc, 0xe5, 0x52, 0x27, 0x4b, 0xd6, 0xda, 0x1f, 0x2a ]


payloads = (p1_, p2_, p3_, p4_, p5_, p6_)
state = 0
num = 1

def crypt(ct):
    global state
    x = (state + 19) % 256
    res = (ct ^ x)
    state = (state + 55)
    return res


for pl in payloads:
    print('\n######### PAYLOAD {} - LEN {} bytes'.format(num, int(len(pl))))
    pl_r = list(reversed(pl))
    for ct in pl:
        x = crypt(ct)
        print("{}".format(chr(x)), end='')
    num += 1

print("\n")
```

### getting the flag
$ python ./crypt.py
```
######### PAYLOAD 1 - LEN 6 bytes
Hello?
######### PAYLOAD 2 - LEN 16 bytes
Is this working?
######### PAYLOAD 3 - LEN 40 bytes
Looks like the connection is established
######### PAYLOAD 4 - LEN 48 bytes
Our next meeting will be at at 90.0000, 135.0000
######### PAYLOAD 5 - LEN 39 bytes
Make sure to bring the stolen presents!
######### PAYLOAD 6 - LEN 72 bytes
The password to get in will be HTB{pl41nt3xt_4sm?wh4t_n3xt_s0urc3_c0d3?}
```

