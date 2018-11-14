# (c) copyright 2018 goapsych0@exitzero.de

# https://www.pyimagesearch.com/2017/07/10/using-tesseract-ocr-python/
# https://docs.opencv.org/trunk/d7/d4d/tutorial_py_thresholding.html
# http://blog.ayoungprogrammer.com/2013/01/equation-ocr-part-1-using-contours-to.html/

import pdfkit 
import pdf2image
from PIL import Image
import pytesseract
import argparse
import cv2
import os
import sys


# bg color: f3f3f3
# fg: < 6d6d6d

#cv::Size size(3,3)
#cv::GaussianBlur(img,img,size,0)


if len(sys.argv) > 1:
    imagefile = sys.argv[1]
    print("using already downloaded image: " + imagefile)

    image = cv2.imread(imagefile)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    rc, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    #rc, gray = cv2.threshold(gray, 0, 250, cv2.THRESH_BINARY)
    #rc, gray = cv2.threshold(gray, 0, 109, cv2.THRESH_BINARY)
    #gray = cv2.medianBlur(gray, 3)

    cv2.imwrite("gray.png", gray)

    
    text = pytesseract.image_to_string(Image.open("gray.png"))
    print(text)

    

else:
    url = 'https://hidden-island-93990.squarectf.com/ea6c95c6d0ff24545cad'

    pdfkit.from_url(url, 'captcha.pdf') 

    # convert pdf to image and/or do ocr on it
    pages = pdf2image.convert_from_path('captcha.pdf')
    print("pdf has {} pages".format(len(pages)))

    if 1 == len(pages):
        pages[0].save('captcha.jpg', 'JPEG')


