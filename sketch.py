import cv2
import numpy as np
import time
import math
from picamera.array import PiRGBArray
from picamera import PiCamera
import RPi.GPIO as GPIO
from CameraLED import CameraLED
# https://github.com/ArduCAM/RPI_Motorized_IRCut_Control
# https://github.com/BigNerd95/CameraLED
led = CameraLED() # CameraLED(134)
led.off() # Night vision function

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
motorPins = [5,6,13,19] #will have to check the right GPIOs for the project

# Background for the displaying of hash and crypto stuff
background_tile = np.zeros((320,240,3), np.uint8)

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

with picamera.PiCamera() as camera:
    camera.resolution = (320, 240)
    camera.framerate = 24
    time.sleep(2) #Camera warmup
    camera.awb_mode = 'off'
    # camera.awb_gains = (0.5, 0.5)

    with picamera.array.PiRGBArray(camera) as stream:
        # Loop constantly
        while True:
            camera.capture(stream, format='bgr', use_video_port=True)
            image = stream.array
            b, g, r = cv2.split(image)

            # Also check https://stackoverflow.com/questions/64134608/calculating-ndvi-from-a-nir-image-of-a-plant
            # Calculate the NDVI
            bottom = (r.astype(float) + b.astype(float))
            bottom[bottom == 0] = 0.01  # Make sure we don't divide by zero!

            # This would be the image to call for displaying NDVI
            ndvi = (r.astype(float) - b) / bottom
            ndvi = contrast_stretch(ndvi)
            ndvi = ndvi.astype(np.uint8)
            image = image.astype(np.uint8)
            g = g.astype(np.uint8)

            #randomSpore() from image ?
            # https://numpy.org/doc/stable/reference/generated/numpy.mean.html
            mn = ndvi.mean()
            mx = nvdi.max()
            mi = nvdi.min()
            #random generator with seed
            # https://realpython.com/python-random/#pythons-best-kept-secrets

            # see "Using hash() on a Custom Object" section
            # https://www.askpython.com/python/built-in-methods/python-hash-function

            #encryption in openCV with cv2.bitwise_xor noise based on np.random(size of image)
            # https://www.programmersought.com/article/16714778804/

            # Call for concatenating the different images together
            im_tile = concat_tile([[image, g],[ndvi, background_tile]])
            
            cv2.imshow("cryptogam", im_tile)

            stream.truncate(0)

# check this link for blockchain configuration of data
# https://www.activestate.com/blog/how-to-build-a-blockchain-in-python/
# https://livecodestream.dev/post/from-zero-to-blockchain-in-python-part-1/

#Concatenate function for displaying four different images

def concat_tile(im_list_2d):
    return cv2.vconcat([cv2.hconcat(im_list_h) for im_list_h in im_list_2d])

#waits for user to press any key
#(this is necessary to avoid Python kernel form crashing)
cv2.waitKey(0)

#closing all open windows
cv2.destroyAllWindows()
