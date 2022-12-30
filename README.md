# Face Aimer #

## Overview ##
A Python program (Windows only, Python 3.8+) for controlling your mouse using your face.
Uses your webcam and tracks your face's orientation using a trained model from dlib.
There are two modes of control, absolute mouse position, and joystick.

## Installation ##
1. Download and extract, or clone this repo to a location of your choice.
2. Install Prerequisites (recommend using virtualenv):
   1. `pip install opencv-python`
   2. `pip install dlib `
   3. `pip install imutils`
   4. `pip install pynput`
   5. `pip install pywin32`
3. Download this [trained model](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2) from dlib and place it into the ***resources*** folder.

## Execution ##
1. Run the program: `python <install_path>\face_aimer.py`
2. Calibrate the camera by following the prompts in the Face Aimer window that appears.
3. The program will now begin controlling the mouse. While the Face Aimer window is in focus:
   - Press the ESC key to quit the program
   - Press the TAB key to switch between **mouse** and **stick** control modes
   - Press the SPACEBAR to pause and unpause the program's control of your mouse

## To-Do ##
- [x] Add text to indicate the currently selected control mode
- [x] Improve facial tracking by utilizing more tracked points from the model
- [ ] Add re-calibrate option
- [ ] Implement offsets based on head translation so you don't need to keep your head locked in place
- [ ] Create better installation process

## Acknowledgements ##
- Referenced Satya Mallick's tutorial: https://learnopencv.com/head-pose-estimation-using-opencv-and-dlib/
- Also referenced this project: https://github.com/lincolnhard/head-pose-estimation
