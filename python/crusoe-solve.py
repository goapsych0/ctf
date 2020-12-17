#!/usr/bin/python3

# 
# (c) 2020 team exitzero (goapsych0@exitzero.de)
# 
# asis-ctf-2020 crusoe
#

# In [1]: for i in chars:
#    ...:     x=subprocess.check_output(['echo '+ i +'|./crusoe'],shell=True)
#    ...:     y[i]=x
# 1:06
# In [1]: chars='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
# 1:07
# y={}
# fehlt noch vor der schleife
# dann kann man mit y['a'] de darstellung fuer a kriegen
# ￼

#import pandas
from pwn import *
import string
import subprocess


# FLAG:
#
#         :    <>  :        :  []    :  [] <> :        :        : <> []
#   _()   :   /)   :   ()   :  |()_  :  |()/  :  _()   :  _()   :  \()|
#  []/^   :   ^\   :   /\   :   ^^[] :   ^^   : []^\   : []/^   :   ^^
#   <>[   :   ][ <>:<> ][ <>:   ][   :   ][   :   ][ <>:  <>[   :   ][
# -----------------------------------------------------------------------
#   []    :  [] <> :        :    <>  : <> []  :        : <>     :
#   |()_  :  |()/  :   ()   :   /)   :  \()|  :   ()_  :  \()   :   ()
#    ^^[] :   ^^   :   /\   :   ^\   :   ^^   :   /^[] :   ^\   :   /\
#    ][   :   ][   :<> ][ <>:   ][ <>:   ][   :<> ][   :   ][ <>:<> ][ <>
# -----------------------------------------------------------------------
#   <>    :        : <> []  :        :    <>  :        :        :    []
#    (\   :   ()_  :  \()|  :  _()   :   /)_  :   ()_  :  _()   :   ()|
#    /^   :   /^[] :   ^^   : []^\   :   ^^[] :   /^[] : []^\   :   /^
# <> ][   :<> ][   :   ][   :   ][ <>:   ][   :<> ][   :   ][ <>:<> ][
# -----------------------------------------------------------------------
#         :  <>    :  <>    :        :  <>    :  []    :  <>    : <>
#   _()   :   (\   :   (\   :   ()_  :   (\   :  |()_  :   (\   :  \()
#  []^\   :   ^\   :   /^   :   /^[] :   ^\   :   ^^[] :   ^\   :   ^\
#    ][ <>:   ]<>  :<> ][   :<> ][   :   ]<>  :   ][   :   ]<>  :   ][ <>
# -----------------------------------------------------------------------
#  <> []  :    <>  :  []    :        :  <>    :        :        :
#   \()|  :   /)   :  |()_  :   ()   :   (\   :  _()   :   ()_  :   ()_
#    ^^   :   ^\   :   ^^[] :   /\   :   /^   : []/^   : | ^^[] : | ^^[]
#    ][   :   ][ <>:   ][   :<> ][ <>:<> ][   :  <>[   :  [][   :  [][
# -----------------------------------------------------------------------
#   <>    :        :  <>    :  <>    : <>     :        :        : <>
#    (\   :  _()   :   (\   :   (\   :  \()_  :   ()_  :  _()   :  \()
#    /^   : []^\   :   ^\   :   /^   :   ^^[] : | ^^[] : []^\   :   ^\
# <> ][   :   ][ <>:   ]<>  :<> ][   :   ][   :  [][   :   ][ <>:   ][ <>
# -----------------------------------------------------------------------
#  <> []  :        :        :        :    <>  :        :    []  :
#   \()|  :  _()   :  _()   :  _()   :   /)   :  _()   :   ()|  :   ()
#    ^^   : []^\   : []^\   : []^\   :   /^   : []^\   :   /^   :   /\
#    ][   :   ][ <>:   ][ <>:   ][ <>:  <>[   :   ][ <>:<> ][   :<> ][ <>
# -----------------------------------------------------------------------
#         :  [] <> :  <>    :  <>    :    <>  :        :    []  :
#    ()_  :  |()/  :   (\   :   (\   :   /)   :  _()   :   ()|  :   ()
#  | ^^[] :   ^^   :   /^   :   ^\   :   ^\   : []^\   :   /^   : | /^
#   [][   :   ][   :<> ][   :   ]<>  :   ][ <>:   ][ <>:<> ][   :  <>[

# basically 8x8 matrix
# flag[row][col] = signN with row[0..7], and col[0..7]


flagfile = 'flag.crusoe'
printable_chars = string.digits + string.ascii_lowercase  #string.printable

lookup = {}
l2 = {}
for c in printable_chars:
    x = subprocess.check_output(['echo '+ c +'|./crusoe'], shell=True)
    #print(c + ":")
    #print(x.decode('ascii'))
    lines = x.decode('ascii').split('\n')
    #print("num lines: {}".format(len(lines)))
    for l in lines[:-2]:
        if c in lookup:
            lookup[c]
        else:
            lookup[c] = ""
        s = len(l)
        #print(":{}:{}".format(l, s))
        #print("len: ", s)
        if s == 9:
            #print(":"+l)
            lookup[c] += l
            l2[c]=l
        if s == 18:
            #print(":"+l[:-8])
            lookup[c] += l[:-8]
            l2[c]=l[:-8]
        if s == 27:
            lookup[c] += l[:-16]
            l2[c]=l[:-16]


        #print(lookup[c])


subrow = 0
row = 0
flag_0_0 = ""
flag = {}

with open(flagfile) as f:
    flaglines = f.readlines()

print("read in the flag file:")
for line in flaglines:
    if line == '\n':
        print('skipping empty line')
        continue

    #for c in line:
    #print(line[0:8], line[9:17], line[18:26], line[27:35], line[36:44], line[45:53], line[54:62], line[63:71])
    #          0       1*8+1      2*8+2 ...
    a = {}

    if row == len(flag):
        flag[row] = {}
    
    for col in range(8): # per each column (we have eight cols in the flag)
        if col == len(flag[row]):
            flag[row][col] = ""

        i = col * 8 + col
        a[col] = line[i:i+8]

        #print("flag[row="+str(row)+"],a[col="+str(col)+"], subrow="+str(subrow))
        # signs are in 0,0,0-3
        # we need to store flag[row][col] += a[col]
        flag[row][col] += a[col]

    subrow += 1
    subrow %= 4

    if 0 == subrow:
        row += 1

sendme = ""
for row in range(len(flag)):
    for col in range(len(flag[row])):
        #print(flag[row][col])
        for c, s in lookup.items():
            #print("lookup["+c+"] s:", s)
            #print("flag:   :", flag[row][col])
            # s.replace(" ", "")
            if s.replace(" ", "") in flag[row][col].replace(" ", ""):
                sendme += c
                break # v,x c,q 0,5,7,9,b,s f,h g,i these are duplicates

print(sendme)

conn = remote('66.172.10.203', 9999)
conn.sendline(sendme)
conn.interactive()
