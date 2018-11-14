#!/usr/bin/env python3

# (c) copyright 2018 goapsych0@exitzero.de

from fontTools.ttLib import TTFont
import sys
import os
import pprint
import re
import requests
import base64



def glyphId2symbol(search):
    for glyphfile in os.listdir('glyphs_ref'):
        #print("reference file: " + glyphfile)
        cmd = "diff -q -I '<TTGlyph' -u " + search + " glyphs_ref/" + glyphfile + " > /dev/null"
        rc = os.system(cmd)
        #print("diff rc=" + str(rc))
        if 0 == rc:
            # get sym from ref file ...
            #print("the glyph " + search + " matches ref file: " + glyphfile)
            with open("glyphs_ref/" + glyphfile) as f:
                for line in f:
                    match = re.search('.* sym="(.)" .*', line)
                    if match:
                        #print(match.group(1))
                        return match.group(1)

            break

    return ""



c8_url = 'https://hidden-island-93990.squarectf.com/ea6c95c6d0ff24545cad'
ttffile = "captchattf"

s = requests.Session()
r = s.get(c8_url)
#print(r.text)

# get ttf file and eq string
ttfb64 = "n/a"
eqstr  = "n/a"
token  = "n/a"
match = re.search('.*;base64,(.+)\'.*<p>([\w\s]+)</p>.*name="token" value="(\d+).*"', r.text)
if match:
    #print(match.group(1))
    #print(match.group(2))
    ttfb64 = match.group(1)
    eqstr = match.group(2)
    token = match.group(3)

ttf = open(ttffile, "wb")
ttf.write(base64.b64decode(ttfb64))
ttf.close()

print("token:     " + str(token))
print("Eq string: " + eqstr)



glyph2code = {}
code2sym = {}
code2sym[32] = ' '


print("analyzing ttf file: " + ttffile)

cmd = 'rm -rf ttx_out && mkdir ttx_out && ttx -t glyf -g -d ttx_out ' + ttffile
print("running system command: " + cmd)
os.system(cmd)

    
font = TTFont(ttffile)
#print(font['cmap'].tables)

codeTable = None
# get mapping from cmap_format_0, but all of them should be fine I guess
for table in font['cmap'].tables:
    if (table.format == 0):
        codeTable = table
        print(table)

        for code in table.cmap:
            print("code: 0x{0:x} ({1}) - {2}".format(code, chr(code), table.cmap[code]))
            glyph2code[table.cmap[code]] = code

for glyph in font['glyf'].glyphs:
    #glyphObj = font['glyf'].glyphs[glyph]
    #print(glyph)
    ttxglyphfile = "ttx_out/" + ttffile + "._g_l_y_f." + glyph + ".ttx"
    if "glyph00000" != glyph:
        sym = glyphId2symbol(ttxglyphfile)
        code2sym[glyph2code[glyph]] = sym
        print("{} <--> {} <--> {}".format(glyph, sym, glyph2code[glyph]))


eqstr2 = ""
for x in eqstr:
    eqstr2 += code2sym[ord(x)]

print(eqstr2)
result = eval(eqstr2)
print(result)


# post result
r = s.post(c8_url, data = {'answer': str(result), 'token' : token})

print(r.text)
