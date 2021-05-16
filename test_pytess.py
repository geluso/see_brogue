import cv2
import pytesseract
  
# Mention the installed location of Tesseract-OCR in your system
pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'

img = cv2.imread("complicated_scroll.png")
im2 = img.copy()

xx = 303
yy = 41
width = 891
height = 24
cropped = im2[yy:yy + height, xx:xx + width]
text = pytesseract.image_to_string(cropped)
print(text)

cv2.imshow('frame', im2)
cv2.imshow('frame2', cropped)
while True:
  wait_key = cv2.waitKey(25)
  if wait_key & 0xFF == ord('q'):
    break
