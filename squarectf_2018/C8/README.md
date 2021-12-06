# Square CTF 2018 - C8: CAPTCHA


## Description
Charvises (the native species which lived on Charvis 8HD before the first settlers arrived) were very good at math. In a surprising symbiosis relationship between humans and Charvises, it was agreed that the Charvises would be responsible for C8.

Can you pass their CAPTCHA (Completely Automated Public Turing Test to tell Charvises and Humans Apart)?

### Details
You get the url to a website showing some lenghty equation that needs to be solved (in time(!)) and the result needs to be submitted.

Looks like this:
![captcha.jpg](captcha.jpg?raw=true "captcha.jpg")

The problem here is that you cannot just copy and past the quation string from screen/source since the page provides a custom font the text to render.
So the real text would more look like this:
```
FFx G FFFi P BDz G BDz G FFBD P FY G Yzz G FFi G pz G fzzzz n FFFx P FM G Mzz P FFFx n FO n FB P pzzz P Ff G Fr n rzzz G FFFY n Mz n Mz G fzzz G FFFY P iz G Mz G FFFFf n Fr n izz P Mz P FM P FFB G Yz P Mzzz n FFFi n FFx P BDz P fzz G rz G FFB G FBD G pzz P FFFx n rz G Mz G FFBD G fz G FY G izzzzzzzzz
```

From here one would think you could just (note: you still would need those symbols) map the letters to the equation symbols. For example map letter **'F'** to symbol **'('**. But unfortunately the equation itself obviously has to change every time but so does the mapping itself.
And of course you do not have plenty of time to do so, so its necessary to script this whole process.



## Solution(s)

1. Be Charvises or a really fast at typing
2. Grab the screen and try extracting the equation via OCR, produce a string, calc & submit result
3. Grab the source and analyze the font mapping, grab the equation as letters, transform to equation string via the found mapping, calc & submit result

### 1. Be Charvises
Not for me

### 2. OCR
I came up with this [script](get-page-as-image.py) and did also manual tweaking but the results were rather dissapointing and not very reliable. For example looked like this:
```
«(1 x (10 + (9 + 4)))x<<<<<1o + e) + a) + (<3 x <6 — a» + (2 + (e x 4))» x (a + 3)) + (5 x ((4 x 7) x <2 x 4)))» x «(((e — ((6 +10)x
($16533) + 1) 7 (10 7 9)) x (a 7 (((«2 + 9) 7 «e 7 4) + (v 7 (s 7 10))» 7 9)71)+<a x 4))» + ((4 7 4) + «((5 7 <5 x 4)) 7 5) x v)
```
After more search on the internet I found one nice [tutorial](http://blog.ayoungprogrammer.com/2013/01/equation-ocr-part-1-using-contours-to.html/) that seemd like the right thing to do.
Somehow I got stuck with applying filters and blurs and the related functions. So I thought let's learn TrueType fonts.


### 3. Font analysis

There's lots of information you can find on the internet about TrueType fonts (.ttf) files. Basically they provide a table of glyphs and how they should be rendered on screen, means where are the pixels for each glyph. Lucky enough here the glyphs are always the same. Or you can say the contours will not change in the font file which does change everytime you reload the page.
So what does change is a) the mapping between the so called glyphID and the contour for this glyph and b) the mapping between glyphID and an ascii letter.

So you might want to use [fonttools](https://github.com/fonttools/fonttools) and do this in python.

The steps here involve:
1. GET the webpage and extract font file, the equation string, and probably the token that's passed with the post request
2. analyze the font file and get mapping(s)
3. calculate result
4. submit result

You find this script [here](anal-ttf.py "anal-ttf.py")
Before this would work I prepared a refernce directory containing only the contours of the glyf table of that font.

#### GET stuff
This is the code piece to get the ttf file:
```
r = s.get(c8_url)
match = re.search('.*;base64,(.+)\'.*<p>([\w\s]+)</p>.*name="token" value="(\d+).*"', r.text)
if match:
    ttfb64 = match.group(1)
    eqstr = match.group(2)
    token = match.group(3)

ttf = open(ttffile, "wb")
ttf.write(base64.b64decode(ttfb64))
ttf.close()
```

#### Analyze font
You can then use fonttools ttLib to parse the file and access the tables. However I had trouble to get to the contours information via the lib so the (faster) workaround here was to use the **ttx** tool that comes with fonttools.

```
$ ttx -t glyf -g -d glyphs_ref/ captchattf
```
This generates one file for each glyph, we have basically 15 named like glyphs_ref/glyph000[01..15].ttx
There's a number zero as well, you can see in the image below how thos glyphs might really look like and that we have the same at position (aka ID) zero and one. Zero is kind of an default ID, for now we just need 1-15.
![glyphs](read_font_online_download_4_glyphs_Screenshot.png?raw=true)

Looking at this, and I mentioned it earlier, what changes in the file here is which glyph gets assigned to which ID. But the relation between the glyph symbol itself and its contour is exactly the same all the time. Therefore if you generate the files from the glyph table with ttx command shown above you will get (almost) the exact same files.
For the same glyph the will only differ in the name attribute.
Show below are lines from those files were I added a **sym** attribute that will map the glyph sym to this file. Then we can do a lookup glyph contour to symbol.


```
    <TTGlyph sym="9" name="glyph00001" xMin="0" yMin="0" xMax="561" yMax="689">
    <TTGlyph sym="7" name="glyph00002" xMin="0" yMin="0" xMax="510" yMax="696">
    <TTGlyph sym="4" name="glyph00003" xMin="0" yMin="-3" xMax="576" yMax="690">
    <TTGlyph sym="5" name="glyph00004" xMin="0" yMin="0" xMax="531" yMax="690">
    <TTGlyph sym="*" name="glyph00005" xMin="0" yMin="0" xMax="444" yMax="481">
    <TTGlyph sym="6" name="glyph00006" xMin="0" yMin="0" xMax="544" yMax="679">
    <TTGlyph sym="2" name="glyph00007" xMin="0" yMin="0" xMax="497" yMax="704">
    <TTGlyph sym=")" name="glyph00008" xMin="0" yMin="-128" xMax="290" yMax="747">
    <TTGlyph sym="3" name="glyph00009" xMin="0" yMin="0" xMax="548" yMax="684">
    <TTGlyph sym="-" name="glyph00010" xMin="0" yMin="0" xMax="465" yMax="347">
    <TTGlyph sym="8" name="glyph00011" xMin="0" yMin="0" xMax="569" yMax="689">
    <TTGlyph sym="+" name="glyph00012" xMin="0" yMin="0" xMax="495" yMax="519">
    <TTGlyph sym="(" name="glyph00013" xMin="0" yMin="-128" xMax="290" yMax="747">
    <TTGlyph sym="1" name="glyph00014" xMin="0" yMin="0" xMax="311" yMax="673">
    <TTGlyph sym="0" name="glyph00015" xMin="0" yMin="0" xMax="585" yMax="660">
```


So we still need another mapping of the actual ascii letter shown in the html source and the glyph symbol. The ttf file provides the cmap table which does a mapping between ascii letter and glyph name (aka the glyphID). Table looks like this for example, note this mapping changes as well in each new  ttf file:
```
  <cmap>
    <tableVersion version="0"/>
    <cmap_format_4 platformID="0" platEncID="3" language="0">
      <map code="0x42" name="glyph00005"/><!-- LATIN CAPITAL LETTER B -->
      <map code="0x4b" name="glyph00006"/><!-- LATIN CAPITAL LETTER K -->
      <map code="0x50" name="glyph00003"/><!-- LATIN CAPITAL LETTER P -->
      <map code="0x52" name="glyph00002"/><!-- LATIN CAPITAL LETTER R -->
      <map code="0x53" name="glyph00012"/><!-- LATIN CAPITAL LETTER S -->
      <map code="0x54" name="glyph00001"/><!-- LATIN CAPITAL LETTER T -->
      <map code="0x56" name="glyph00013"/><!-- LATIN CAPITAL LETTER V -->
      <map code="0x58" name="glyph00009"/><!-- LATIN CAPITAL LETTER X -->
      <map code="0x63" name="glyph00008"/><!-- LATIN SMALL LETTER C -->
      <map code="0x65" name="glyph00007"/><!-- LATIN SMALL LETTER E -->
      <map code="0x6a" name="glyph00015"/><!-- LATIN SMALL LETTER J -->
      <map code="0x6d" name="glyph00014"/><!-- LATIN SMALL LETTER M -->
      <map code="0x70" name="glyph00004"/><!-- LATIN SMALL LETTER P -->
      <map code="0x73" name="glyph00010"/><!-- LATIN SMALL LETTER S -->
      <map code="0x74" name="glyph00011"/><!-- LATIN SMALL LETTER T -->
    </cmap_format_4>
```

With that in place we are almost done.
As mentioned above however I had problems using python to extract the contour from glyf table, therefore ttx is executed via os.system().
This time the files are placed  in ttx_out directory.

```python
cmd = 'rm -rf ttx_out && mkdir ttx_out && ttx -t glyf -g -d ttx_out ' + ttffile
print("running system command: " + cmd)
os.system(cmd)
```

Now loop through each of the 15 glyphs (skipping glyph zero) from this file and figure out which sym matches its contours
```python
for glyph in font['glyf'].glyphs:
    #glyphObj = font['glyf'].glyphs[glyph]
    #print(glyph)
    ttxglyphfile = "ttx_out/" + ttffile + "._g_l_y_f." + glyph + ".ttx"
    if "glyph00000" != glyph:
        sym = glyphId2symbol(ttxglyphfile)
        code2sym[glyph2code[glyph]] = sym
```

this is the sym lookup function called as sym = glyphId2symbol(ttxglyphfile).
once again I was lazy and used just diff system command to figure out if only the name differs for a matching contour (reminder learn more python)

```python
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
```


... almost done.
We do have the equation string already in *eqstr* so just need to replace the letters. Note that **'x'** was already mapped to **'*'** and we have a mapping fpr spaces (*code2sym[32] = ' '*).

```python
for x in eqstr:
    eqstr2 += code2sym[ord(x)]
```

#### calc and submit
and simply calculate using evil eval
```python
result = eval(eqstr2)
```

post it
```python
r = s.post(c8_url, data = {'answer': str(result), 'token' : token})
```

et voila
```
$ ./anal-ttf.py
token:     1542154265
Eq string: aaaaaY d aI B VNN B amc d GNN v aaV B mcN d aI v aG d am d YNNNNN d aaaao d GN d mcN d aao B oN v INN d amc v aaD d DN d aY v aaaG v YN d mcN d aX B GNNNNNNN B aamc d aaaI d DN B am d mNN d aaaX d mN d IN d INNN B aaaD B XN d amc d mNN v aaao v XN B aaX v bN d aD d oNNN d aamc d aaI d oN B YNN v mNNNNN
analyzing ttf file: captchattf
running system command: rm -rf ttx_out && mkdir ttx_out && ttx -t glyf -g -d ttx_out captchattf
Dumping "captchattf" to "ttx_out/captchattf.ttx"...
Dumping 'glyf' table...
<fontTools.ttLib.tables._c_m_a_p.cmap_format_0 object at 0x7f6f0b39d668>
code: 0x61 (a) - glyph00008
code: 0x42 (B) - glyph00013
code: 0x63 (c) - glyph00005
code: 0x44 (D) - glyph00002
code: 0x76 (v) - glyph00009
code: 0x64 (d) - glyph00001
code: 0x47 (G) - glyph00004
code: 0x49 (I) - glyph00006
code: 0x62 (b) - glyph00014
code: 0x4e (N) - glyph00010
code: 0x6d (m) - glyph00003
code: 0x56 (V) - glyph00012
code: 0x58 (X) - glyph00011
code: 0x59 (Y) - glyph00015
code: 0x6f (o) - glyph00007
glyph00003 <--> 1 <--> 109
glyph00010 <--> ) <--> 78
glyph00004 <--> 4 <--> 71
glyph00015 <--> 5 <--> 89
glyph00008 <--> ( <--> 97
glyph00005 <--> 0 <--> 99
glyph00011 <--> 7 <--> 88
glyph00006 <--> 2 <--> 73
glyph00007 <--> 3 <--> 111
glyph00013 <--> - <--> 66
glyph00002 <--> 6 <--> 68
glyph00014 <--> 9 <--> 98
glyph00012 <--> 8 <--> 86
glyph00009 <--> + <--> 118
glyph00001 <--> * <--> 100
(((((5 * (2 - 8)) - (10 * 4)) + ((8 - 10) * (2 + (4 * (1 * 5))))) * ((((3 * 4) * 10) * ((3 - 3) + 2)) * (10 + ((6 * 6) * (5 + (((4 + 5) * 10) * (7 - 4))))))) - ((10 * (((2 * 6) - (1 * 1)) * (((7 * 1) * 2) * 2))) - (((6 - 7) * (10 * 1)) + (((3 + 7) - ((7 + 9) * (6 * 3))) * ((10 * ((2 * 3) - 5)) + 1)))))
-271143748
```

```
<html><body>
<p>If you can see this then you have solved the CAPTCHA.</p>
<p>If you have solved the CAPTCHA then you are a Charvise.</p>
<p>If you are a Charvise then you are welcome on Charvis.</p>
<p>If you are welcome on Charvis then:</p>
<ol>
<li>You can disable this system using flag-a76013167fd4c04e3134</li>
<li><p>You should be given useful information.</p>
<p>If you should be given useful information then this informs you that there are two layers of defense left, and the last one is trivial.</p></body></html>
```

nice challange, thx.
