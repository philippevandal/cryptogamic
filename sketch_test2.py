import cv2
import numpy as np
import time
import math
from picamera.array import PiRGBArray
from picamera
import RPi.GPIO as GPIO
from CameraLED import CameraLED
# https://github.com/ArduCAM/RPI_Motorized_IRCut_Control
# https://github.com/BigNerd95/CameraLED
led = CameraLED() # CameraLED(134)
led.off() # Night vision function

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
motorPins = [5,6,13,19] #will have to check the right GPIOs for the project

cv2.namedWindow('cryptogam',cv2.WINDOW_KEEPRATIO)
cv2.setWindowProperty('cryptogam',cv2.WND_PROP_ASPECT_RATIO,cv2.WINDOW_KEEPRATIO)
cv2.setWindowProperty('cryptogam',cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

for pin in motorPins:
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

halfstep_seq = [
  [1,0,0,0],
  [1,1,0,0],
  [0,1,0,0],
  [0,1,1,0],
  [0,0,1,0],
  [0,0,1,1],
  [0,0,0,1],
  [1,0,0,1]
]

def motor(angle, motor):
    steps = angle * 4096 / 360
    counter = 0;
    for i in range(512):
        for halfstep in range(8):
            if counter > abs(steps):
                break
            for pin in range(4):
                if (angle < 0):
                    CCW = list(reversed(motor))
                    GPIO.output(CCW[pin], halfstep_seq[halfstep][pin])
                else:
                    GPIO.output(motor[pin], halfstep_seq[halfstep][pin])
            time.sleep(0.001)
            counter += 1
        else:
            continue
        break
    GPIO.cleanup()

def contrast_stretch(im):
    in_min = np.percentile(im, 5)
    in_max = np.percentile(im, 95)

    out_min = 0.0
    out_max = 255.0

    out = im - in_min
    out *= ((out_min - out_max) / (in_min - in_max))
    out += in_min

    return out

#Concatenate function for displaying four different images

def concat_tile(im_list_2d):
    return cv2.vconcat([cv2.hconcat(im_list_h) for im_list_h in im_list_2d])

def display_info(text):
    # Background for the displaying of hash and crypto stuff
    background_tile = np.zeros((640,480,3), np.uint8)
    font = cv2.FONT_HERSHEY_SIMPLEX
    # org
    org = (50, 50)
    # fontScale
    fontScale = 1
    # Blue color in BGR
    color = (255, 255, 255)

    # Line thickness of 2 px
    thickness = 2

    # Using cv2.putText() method
    image = cv2.putText(background_tile, text, org, font,
                       fontScale, color, thickness, cv2.LINE_AA)

while True:
    # Picamera directly to openCV numpy.array
    with picamera.PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.framerate = 24
        camera.awb_mode = 'off'
        time.sleep(2)
        image = np.empty((480, 640, 3), dtype=np.uint8)
        camera.capture(image, 'rgb')
    b, g, r = cv2.split(image)

    # Also check https://stackoverflow.com/questions/64134608/calculating-ndvi-from-a-nir-image-of-a-plant

    # Calculate the NDVI
    bottom = (r.astype(float) + b.astype(float))
    bottom[bottom == 0] = 0.01  # Make sure we don't divide by zero!

    # This would be the image to call for displaying NDVI
    ndvi = (r.astype(float) - b) / bottom
    ndvi = contrast_stretch(ndvi)
    ndvi = ndvi.astype(np.uint8)
    n = cv2.applyColorMap(ndvi, cv2.COLORMAP_SUMMER)

    #randomSpore() from image ?
    # https://numpy.org/doc/stable/reference/generated/numpy.mean.html
    mn = ndvi.mean()
    mx = ndvi.max()
    mi = ndvi.min()
    display_info("mean: " + mn + " max: " + mx)

    #random generator with seed
    # https://realpython.com/python-random/#pythons-best-kept-secrets

    # see "Using hash() on a Custom Object" section
    # https://www.askpython.com/python/built-in-methods/python-hash-function

    #encryption in openCV with cv2.bitwise_xor noise based on np.random(size of image)
    # https://www.programmersought.com/article/16714778804/

    # Call for concatenating the different images together
    # im_tile = concat_tile([[image, g],[ndvi, background_tile]])

    cv2.imshow("cryptogam", image)
    time.sleep(2)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        GPIO.cleanup()
        cv2.destroyAllWindows()
    	break

# check this link for blockchain configuration of data
# https://www.activestate.com/blog/how-to-build-a-blockchain-in-python/
# https://livecodestream.dev/post/from-zero-to-blockchain-in-python-part-1/
