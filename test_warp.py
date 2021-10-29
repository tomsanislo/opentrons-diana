import cv2
# import matplotlib.pyplot as plt
import numpy as np

im = cv2.imread("image.JPG")
src = np.float32([(120,  123), # ok, levy horni, x, y
                  (380, 150), # ok, pravy horni
                  (185, 485), # ok, levy dolni
                  (504, 403)]) # ok, pravy dolni

dst = np.float32([(604, 0), # pravy horni
                  (0, 0), # levy horni
                  (604, 480), # pravy dolni
                  (0, 480)]) # levy dolni

h, w = im.shape[:2]
M = cv2.getPerspectiveTransform(src, dst)
warped = cv2.warpPerspective(im, M, (w, h), flags=cv2.INTER_LINEAR)
flipped = cv2.flip(warped, 1)

cv2.imwrite("image2.JPG", flipped[230:350, 0:480]  )