import queue
import threading

import cv2 as cv
import dlib
import numpy as np
from imutils import face_utils

from input_controllers import mouseController, stickController
from settings import face_aimer_settings


class faceAimer():

    def __init__(self):
        # import settings
        self.control_mode = face_aimer_settings['default_control_mode']
        self.res_x = face_aimer_settings['res_x']
        self.res_y = face_aimer_settings['res_y']
        self.marker_color = face_aimer_settings['marker_color_bgr']
        self.gaze_line_color = face_aimer_settings['gaze_line_color_bgr']
        self.deadzone_color = face_aimer_settings['deadzone_color_bgr']
        self.landmarks_color = face_aimer_settings['facial_landmarks_color_bgr']

        # text settings
        self.show_text = True
        self.font_face = cv.FONT_HERSHEY_PLAIN
        self.font_scale = 0.85
        self.font_color = (0, 0, 0)
        self.font_thickness = 1
        self.font_linetype = cv.LINE_AA

        # text overlays
        self.primary_text_position = (10, 10)
        self.quit_text = "'ESC' to quit"
        self.switch_mode_text = f"'TAB' to switch control modes | {self.control_mode}"
        self.pause_text = "'SPACEBAR' to pause control input"
        self.unpause_text = "'SPACEBAR' to resume control input"
        self.hide_controls_text = "'H' to hide controls"
        # get size of quit text to calculate additional text positions
        (_, text_height), _ = cv.getTextSize(self.quit_text, self.font_face, self.font_scale, self.font_thickness)
        self.secondary_text_position = (self.primary_text_position[0], int(self.primary_text_position[1] + text_height*1.4))
        self.tertiary_text_position = (self.secondary_text_position[0], int(self.secondary_text_position[1] + text_height*1.4))
        self.fourth_text_position = (self.tertiary_text_position[0], int(self.tertiary_text_position[1] + text_height*1.4))

        # open video camera
        try:
            self.cap = cv.VideoCapture(0)
        except:
            print("Cannot acquire camera resource! Quitting...")
            exit(1)

        # facial recognition
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("resources\shape_predictor_68_face_landmarks.dat")

        # 3D facial points - numbers in () indicate numbers on markup reference image - 1
        self.model_points = np.array([
            (-350.0,120.0,-310.0),      # 0 - right cheek
            (-345.0,35.0,-280.0),       # 1 - right cheek
            (-330.0,-50.0,-250.0),      # 2 - right cheek
            (-310.0,-135.0,-220.0),     # 3 - right cheek
            (-260.0, -210.0, -190.0),   # 4 - right jaw
            (-200.0,-260.0,-158.75),    # 5 - right jaw
            (-140.0,-290.0,-127.5),     # 6 - right jaw
            (-70.0,-320.0,-96.25),      # 7 - right chin
            (0.0, -330.0, -65.0),       # 8 - chin
            (70.0,-320.0,-96.25),       # 9 - left chin
            (140.0,-290.0,-127.5),      # 10 - left jaw
            (200.0,-260.0,-158.75),     # 11 - left jaw
            (260.0, -210.0, -190.0),    # 12 - left jaw
            (310.0,-135.0,-220.0),      # 13 - left cheek
            (330.0,-50.0,-250.0),       # 14 - left cheek
            (345.0,35.0,-280.0),        # 15 - left cheek
            (350.0,120.0,-310.0),       # 16 - left cheek
            (-225.0, 245.0, -105.0),    # 19 - right middle eyebrow
            (225.0, 245.0, -105.0),     # 24 - left middle eyebrow
            (0.0, 170.0, -100.0),       # 27 - top of nose
            (0.0, 130.0, -55.0),        # 28 - middle of nose
            (0.0, 90.0, -30.0),         # 29 - middle of nose
            (0.0, 50.0, -15.0),         # 30 - middle of nose
            (-60.0, 15.0, -30.0),       # 31 - nose tip right
            (-30.0, 5.0, -15.0),        # 32 - nose tip right
            (0.0, 0.0, 0.0),            # 33 - nose tip middle
            (30.0, 5.0, -15.0),         # 34 - nose tip left
            (60.0, 15.0, -30.0),        # 35 - nose tip left
            (-240.0, 170.0, -135.0),    # 36 - Right eye outer corner
            (-115.0, 170.0, -135.0),    # 39 - Right eye inner corner
            (115.0, 170.0, -135.0),     # 42 - left eye inner corner
            (240.0, 170.0, -135.0),     # 45 - left eye outer corner
            (-150.0, -150.0, -125.0),   # 48 - right mouth corner
            (150.0, -150.0, -125.0)     # 54 - left mouth corner
        ], dtype=np.float64)

        # camera parameters (default params but could be calibrated)
        _, frame = self.cap.read()
        size = frame.shape
        focal_length = size[1]
        center = (size[1]/2, size[0]/2)
        self.camera_matrix = np.array(
            [[focal_length, 0, center[0]],
             [0, focal_length, center[1]],
             [0, 0, 1]],
            dtype="double")

        # distortion params (assume no distortion)
        self.dist_coeffs = np.zeros((4, 1))

        # coordinate smoothing
        self.last_1 = (0, 0)
        self.last_2 = (0, 0)
        self.last_3 = (0, 0)

        # init pose points
        self.pose_x = -1
        self.pose_y = -1

        # init pose window
        self.pose_width = 0
        self.pose_height = 0
        self.pose_center = (0, 0)

        # init opencv window
        cv.namedWindow('Face Aimer', cv.WINDOW_NORMAL)
        # spawn the window on top of other windows
        cv.setWindowProperty('Face Aimer', cv.WND_PROP_TOPMOST, 1)

        # pause
        self.paused = False
        # create event to stop controllers
        self.stop_controller_event = threading.Event()

        return

    def calibrate(self):
        # keep track of which stage of calibration
        calibrating = True
        stage = 0
        calibration_positions = ['top left',
                                 'top right', 'bottom right', 'bottom left']
        calibration_points = []

        while calibrating:
            _, frame = self.cap.read()
            frame = cv.flip(frame, 1)
            cv.putText(frame, self.quit_text,
                       self.primary_text_position, self.font_face, self.font_scale, self.font_color, self.font_thickness, self.font_linetype)
            cv.putText(frame, f"CALIBRATING: Point your nose at the {calibration_positions[stage]} corner of your monitor, then press spacebar...",
                       self.secondary_text_position, self.font_face, self.font_scale*0.90, self.font_color, self.font_thickness, self.font_linetype)
            cv.imshow('Face Aimer', frame)

            # if spacebar is pressed, move to next stage
            key = cv.waitKey(1)
            if key == 32:
                calibration_point = self.trackFace(frame)[1]
                if calibration_point == (-1, -1):
                    print("COULDN'T FIND FACE, TRY AGAIN")
                else:
                    calibration_points.append(calibration_point)
                    if stage == 3:
                        calibrating = False
                    else:
                        stage += 1
            # if esc key pressed, quit
            elif key == 27:
                self.shutdown()

        # set bounds
        self.x_min = min(calibration_points[0][0], calibration_points[3][0])
        self.x_max = max(calibration_points[1][0], calibration_points[2][0])
        self.y_min = min(calibration_points[0][1], calibration_points[1][1])
        self.y_max = max(calibration_points[3][1], calibration_points[2][1])

        # get width and height of pose coord space
        self.pose_width = self.x_max - self.x_min
        self.pose_height = self.y_max - self.y_min
        # get the average point for center of screen
        self.pose_center = (self.x_min + self.pose_width/2,
                            self.y_min + self.pose_height/2)

        # get deadzone radius for controller method
        self.controller_deadzone_radius = int(
            self.pose_height*face_aimer_settings['controller_deadzone_threshold'])

        return

    def trackFace(self, frame):
        # updates face landmarks and returns x and y values for nose tip and pose position. Not scaled or adjusted

        # convert frame to grayscale
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        # detect a face
        faces = self.detector(gray)

        # if a face was detected
        if len(faces):

            # get facial landmarks
            face = faces[0]
            self.landmarks = self.predictor(gray, face)
            self.landmarks = face_utils.shape_to_np(self.landmarks)

            # get relevant points
            self.image_pts = np.array([self.landmarks[0],       # right cheek
                                       self.landmarks[1],       # right cheek
                                       self.landmarks[2],       # right cheek
                                       self.landmarks[3],       # right cheek
                                       self.landmarks[4],       # right jaw
                                       self.landmarks[5],       # right jaw
                                       self.landmarks[6],       # right jaw
                                       self.landmarks[7],       # right chin
                                       self.landmarks[8],       # chin
                                       self.landmarks[9],       # left chin
                                       self.landmarks[10],      # left jaw
                                       self.landmarks[11],      # left jaw
                                       self.landmarks[12],      # left jaw
                                       self.landmarks[13],      # left cheek
                                       self.landmarks[14],      # left cheek
                                       self.landmarks[15],      # left cheek
                                       self.landmarks[16],      # left cheek
                                       self.landmarks[19],      # right eyebrow
                                       self.landmarks[24],      # left eyebrow
                                       self.landmarks[27],      # top nose
                                       self.landmarks[28],      # mid nose
                                       self.landmarks[29],      # mid nose
                                       self.landmarks[30],      # mid nose
                                       self.landmarks[31],      # nose tip right
                                       self.landmarks[32],      # nose tip right
                                       self.landmarks[33],      # nose tip center
                                       self.landmarks[34],      # nose tip left
                                       self.landmarks[35],      # nose tip left
                                       self.landmarks[36],      # right eye outer corner
                                       self.landmarks[39],      # right eye inner corner
                                       self.landmarks[42],      # left eye inner corner
                                       self.landmarks[45],      # left eye outer corner
                                       self.landmarks[48],      # mouth right
                                       self.landmarks[54]       # mouth left
                                       ], dtype=np.float32)

            # solve for PnP
            (_, rot_vect, trans_vect) = cv.solvePnP(self.model_points, self.image_pts, self.camera_matrix, self.dist_coeffs)

            # get pose point projection in terms of image
            (pose_pt_2D, _) = cv.projectPoints(np.array([0.0, 0.0, 1000]), rot_vect, trans_vect, self.camera_matrix, self.dist_coeffs)

            nosePoint = (self.landmarks[33][0], self.landmarks[33][1])
            posePoint = (pose_pt_2D[0][0][0], pose_pt_2D[0][0][1])

            return (nosePoint, posePoint)

        else:
            # if can't find face, just return negative
            return ((-1, -1), (-1, -1))

    def shutdown(self):
        # stop current controller thread
        self.stop_controller_event.set()
        self.controller_thread.join()
        # release resources
        self.cap.release()
        cv.destroyAllWindows()
        exit(0)

    def startControllerThread(self):
        # select controller
        if self.control_mode == 'mouse':
            self.selected_controller = self.mouse_controller
        elif self.control_mode == 'stick':
            self.selected_controller = self.stick_controller

        # create controller daemon thread
        self.controller_thread = threading.Thread(target=self.selected_controller.start_controller, args=[self.stop_controller_event], daemon=True)
        self.controller_thread.start()
        return

    def run(self, debug=False):
        # calibrate
        self.calibrate()

        # init variables
        self.nosePoint = (0, 0)
        self.posePoint = (0, 0)
        self.controller_queue = queue.Queue()
        pose_dimensions = (self.pose_width, self.pose_height, self.pose_center)

        # initialize the controllers
        self.mouse_controller = mouseController(self.controller_queue, pose_dimensions, (self.x_min, self.y_min))
        self.stick_controller = stickController(self.controller_queue, pose_dimensions, self.controller_deadzone_radius)

        # start controller thread
        self.startControllerThread()

        # start main loop
        while True:
            # read a frame, mirror it
            _, frame = self.cap.read()
            frame = cv.flip(frame, 1)

            # get current nose & pose position
            (self.nosePoint, self.posePoint) = self.trackFace(frame)

            # add targets to controller queue
            if self.paused:
                self.controller_queue.put((-1, -1), block=False)
                pause_status_text = self.unpause_text
            if not self.paused:
                self.controller_queue.put(self.posePoint, block=False)
                pause_status_text = self.pause_text

            # draw controls & status text
            if self.show_text:
                # write quit text
                cv.putText(frame, self.quit_text, self.primary_text_position, self.font_face,
                        self.font_scale, self.font_color, self.font_thickness, self.font_linetype)
                # write switch control text
                cv.putText(frame, self.switch_mode_text, self.secondary_text_position, self.font_face,
                            self.font_scale, self.font_color, self.font_thickness, self.font_linetype)
                # write paused status text
                cv.putText(frame, pause_status_text, self.tertiary_text_position, self.font_face,
                        self.font_scale, self.font_color, self.font_thickness, self.font_linetype)
                # write hide controls text
                cv.putText(frame, self.hide_controls_text, self.fourth_text_position, self.font_face,
                        self.font_scale, self.font_color, self.font_thickness, self.font_linetype)

            # if couldn't find a face, skip all this
            if not (self.posePoint[0] == -1):

                # get points as ints
                nosePointInt = (int(self.nosePoint[0]), int(self.nosePoint[1]))
                posePointInt = (int(self.posePoint[0]), int(self.posePoint[1]))
                poseCenterInt = (int(self.pose_center[0]), int(self.pose_center[1]))

                # draw facial landmarks on frame
                for tracked_pts in self.image_pts:
                    cv.circle(frame, (int(tracked_pts[0]), int(tracked_pts[1])), 2, self.landmarks_color, -1)

                # draw mode-specific overlays
                if self.control_mode == 'stick':
                    # draw gaze line from nose to pose point
                    cv.line(frame, nosePointInt, posePointInt, self.gaze_line_color, 2)
                    # draw deadzone
                    cv.circle(frame, poseCenterInt, self.controller_deadzone_radius, self.deadzone_color, thickness=2)
                elif self.control_mode == 'mouse':
                    # draw target position
                    cv.drawMarker(frame, posePointInt, self.marker_color, cv.MARKER_CROSS, 20, 2, cv.LINE_8)

                if debug:
                    # draw target coords
                    cv.putText(frame, f"X: {self.posePoint[0]}", (20, 100), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), thickness=2)
                    cv.putText(frame, f"Y: {self.posePoint[1]}", (20, 130), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), thickness=2)

            # show the frame
            cv.imshow('Face Aimer', frame)

            # get user input
            key = cv.waitKey(1)
            if key == 27: # 'ESC' key
                #break out of loop
                break
            elif key == 9: # 'TAB' key
                # switch control modes
                # stop current controller thread
                self.stop_controller_event.set()
                self.controller_thread.join()
                # toggle selected control mode
                if self.control_mode == 'mouse':
                    self.control_mode = 'stick'
                elif self.control_mode == 'stick':
                    self.control_mode = 'mouse'
                # set new control text
                self.switch_mode_text = f"'TAB' to switch control modes | {self.control_mode}"
                # initialize new controller thread
                self.stop_controller_event.clear()
                self.startControllerThread()
            elif key == 32: # 'SPACEBAR'
                # toggle pause
                self.paused = not self.paused
            elif (key == 72) or (key == 104): # 'H' or 'h' key
                # toggle hiding controls text
                self.show_text = not self.show_text

        # shutdown
        self.shutdown()


# run the program
if __name__ == '__main__':
    face_aimer = faceAimer()
    face_aimer.run()
