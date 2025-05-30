import cv2 as cv
import qrcode
import sys

im = cv.imread(sys.argv[1])
det = cv.QRCodeDetector()
retval, points, straight_qrcode = det.detectAndDecode(im)
print(f'QRCode contains : {retval}')

