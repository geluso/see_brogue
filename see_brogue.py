import numpy as np
import cv2
import shelve
import time

from skimage.util import compare_images
from skimage.metrics import mean_squared_error

import pytesseract
pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'

LAST_TEXT = None
LAST_TEXT_IMG = None

def read(frame, xx, yy, width, height):
  global LAST_TEXT_IMG

  # does this make a whole copy of the image?
  # cropped = frame[yy:yy + height, xx:xx + width]
  xxc = xx + width / 2
  yyc = yy + height / 2
  image = cv2.getRectSubPix(frame, (width, height), (xxc, yyc))
  cv2.imshow('Frame2', image)  

  if LAST_TEXT_IMG is None:
    LAST_TEXT_IMG = image
    return

  diff = mean_squared_error(image, LAST_TEXT_IMG)
  if diff > 900 or LAST_TEXT is None:
    LAST_TEXT_IMG = image
    text = pytesseract.image_to_string(image, lang='eng')
    text = text.strip()
    return text
  else:
    return LAST_TEXT

def draw_fps(frame, start):
  end = time.time()
  seconds = end - start
  fps = int(1 / seconds)
  fps_text = "FPS: " + str(fps)

  font = cv2.FONT_HERSHEY_SIMPLEX
  org = (1100, 30)
  font_scale = 1
  color = (255, 0, 0)
  thickness = 2
  frame = cv2.putText(frame, fps_text, org, font, font_scale, color, thickness, cv2.LINE_AA)

with shelve.open('config') as config:
  default_config = {
    'rect_xx': 50,
    'rect_yy': 50,
    'rect_width': 400,
    'rect_height': 100,
    'start_frame': 21906,
  }

  for (key, value) in default_config.items():
    if key not in config:
      config[key] = value

  rect_xx = config['rect_xx']
  rect_yy = config['rect_yy']
  rect_width = config['rect_width']
  rect_height = config['rect_height']
  start_frame = config['start_frame']

  cap = cv2.VideoCapture('brogue.mp4')
  if cap.isOpened() == False:
    print("error opening video file")

  total_frames = cap.get(cv2.cv2.CAP_PROP_FRAME_COUNT)
  cap.set(cv2.cv2.CAP_PROP_POS_FRAMES, start_frame)

  while cap.isOpened():
    start = time.time()
    ret, frame = cap.read()
    if ret:
      current_frame = cap.get(cv2.cv2.CAP_PROP_POS_FRAMES)

      wait_key = cv2.waitKey(25)
      # Time controls
      if wait_key & 0xFF == ord('l'):
        forward_frame = min(current_frame + 5 * 30, total_frames)
        cap.set(cv2.cv2.CAP_PROP_POS_FRAMES, forward_frame)
      elif wait_key & 0xFF == ord('L'):
        forward_frame = min(current_frame + 60 * 30, total_frames)
        cap.set(cv2.cv2.CAP_PROP_POS_FRAMES, forward_frame)
      elif wait_key & 0xFF == ord('h'):
        backward_frame = max(current_frame - 5 * 30, 1)
        cap.set(cv2.cv2.CAP_PROP_POS_FRAMES, backward_frame)
      elif wait_key & 0xFF == ord('H'):
        backward_frame = max(current_frame - 60 * 30, 1)
        cap.set(cv2.cv2.CAP_PROP_POS_FRAMES, backward_frame)
      # Rect move commands
      elif wait_key & 0xFF == ord('w'):
        rect_yy -= 1
      elif wait_key & 0xFF == ord('s'):
        rect_yy += 1
      elif wait_key & 0xFF == ord('a'):
        rect_xx -= 1
      elif wait_key & 0xFF == ord('d'):
        rect_xx += 1
      # Rect size commands
      elif wait_key & 0xFF == ord('W'):
        rect_height += 1
      elif wait_key & 0xFF == ord('S'):
        rect_height -= 1
      elif wait_key & 0xFF == ord('A'):
        rect_width -= 1
      elif wait_key & 0xFF == ord('D'):
        rect_width += 1
      # Info
      elif wait_key & 0xFF == ord(' '):
        print("rect_xx, rect_yy, rect_width, rect_height")
        print(rect_xx, rect_yy, rect_width, rect_height)
        print()

        print("current_frame, total_frames")
        print(current_frame, total_frames)
        print()
      # Save
      elif wait_key & 0xFF == ord('Z'):
        config['rect_xx'] = rect_xx
        config['rect_yy'] = rect_yy
        config['rect_width'] = rect_width
        config['rect_height'] = rect_height

        start_frame = current_frame
        config['start_frame'] = start_frame
      # Read
      elif wait_key & 0xFF == ord('r'):
        text = read(frame, rect_xx, rect_yy, rect_width, rect_height)
        print(text)
      # Quit
      elif wait_key & 0xFF == ord('q'):
        config['rect_xx'] = rect_xx
        config['rect_yy'] = rect_yy
        config['rect_width'] = rect_width
        config['rect_height'] = rect_height
        config['start_frame'] = start_frame
        break

      text = read(frame, rect_xx, rect_yy, rect_width, rect_height)
      if not text == LAST_TEXT:
        LAST_TEXT = text
        print(text)

      rect_width = max(0, rect_width)
      rect_height = max(0, rect_height)

      top_left = (rect_xx, rect_yy)
      bot_right = (rect_xx + rect_width, rect_yy + rect_height)

      color = (255, 0, 0) # BGR format. wtf?
      thickness = 2
      cv2.rectangle(frame, top_left, bot_right, color, thickness)

      draw_fps(frame, start)

      cv2.imshow('Frame', frame)  
    else:
      break

  cap.release()
  cv2.destroyAllWindows()
