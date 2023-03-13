import queue
from collections import deque
from math import copysign, sqrt
from time import perf_counter, sleep

import win32api
import win32con
from pynput.mouse import Controller

from settings import face_aimer_settings


class mouseController():

    def __init__(self, pose_point_queue, pose_dimensions, coord_mins):
        # input parameters
        self.x_min = coord_mins[0]
        self.y_min = coord_mins[1]
        self.pose_width = pose_dimensions[0]
        self.pose_height = pose_dimensions[1]
        self.pose_center = pose_dimensions[2]
        self.pose_queue = pose_point_queue

        # import settings
        self.res_x = face_aimer_settings['res_x']
        self.res_y = face_aimer_settings['res_x']
        self.refresh_time = 1/face_aimer_settings['mouse_refresh_rate']
        self.move_factor = face_aimer_settings['move_speed']*self.refresh_time
        self.smoothing_count = face_aimer_settings['move_smoothing']

        # initialize mouse controller
        self.mouse = Controller()

        # initialize variables
        self.pose_point = self.pose_center
        self.smooth_x = 0
        self.smooth_y = 0
        self.offset_x = 0
        self.offset_y = 0
        self.move_allowed = False

        # initialize smoothing array
        self.smoothing_deque = deque()
        for _ in range(self.smoothing_count):
            self.smoothing_deque.appendleft((0,0))

    def poseToResolution(self, pose_coord):
        # normalize current pose coordinate
        x_norm = (pose_coord[0]-self.x_min)/self.pose_width
        y_norm = (pose_coord[1]-self.y_min)/self.pose_height

        # scale to resolution
        x_pix = int(x_norm * self.res_x)
        y_pix = int(y_norm * self.res_y)

        # adjust for overshoot
        if x_pix < 0:
            x_pix = 0
        elif x_pix > self.res_x:
            x_pix = self.res_x

        if y_pix < 0:
            y_pix = 0
        elif y_pix > self.res_y:
            y_pix = self.res_y

        return (x_pix, y_pix)

    def updateOffset(self, smooth_coords):
        self.offset_x = smooth_coords[0] - self.mouse.position[0]
        self.offset_y = smooth_coords[1] - self.mouse.position[1]

    def smoothCoords(self, current_coord):
        smooth_x = 0
        smooth_y = 0

        # get previous values
        for i in range(self.smoothing_count):
            val = self.smoothing_deque[i]
            smooth_x += val[0]
            smooth_y += val[1]

        # add new value and average over smoothing count
        smooth_x += current_coord[0]
        smooth_y += current_coord[1]
        smooth_x = int(smooth_x/(self.smoothing_count + 1))
        smooth_y = int(smooth_y/(self.smoothing_count + 1))

        # update deque
        self.smoothing_deque.pop()
        self.smoothing_deque.appendleft((smooth_x, smooth_y))

        return (smooth_x, smooth_y)

    def start_controller(self, stop_controller_event):
        while(True):
            # get start time
            tic = perf_counter()

            # exit thread if stop event is set
            if stop_controller_event.isSet():
                return

            # check queue for new target value
            try:
                self.pose_point = self.pose_queue.get(False)
                # if no face detected, stop moving
                if self.pose_point == (-1,-1):
                    self.pose_point = self.pose_center
                    self.move_allowed = False
                else:
                    rawpixcoords = self.poseToResolution(self.pose_point) # convert pose space to screen resolution space
                    (self.smooth_x, self.smooth_y) = self.smoothCoords(rawpixcoords) # smooth by averaging past 3 frames
                    self.move_allowed = True             
            except queue.Empty:
                pass

            if self.move_allowed:
                # get updated offset from target
                self.updateOffset((self.smooth_x, self.smooth_y))

                # move mouse towards target
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(self.offset_x*self.move_factor), int(self.offset_y*self.move_factor))

            # get end time
            toc = perf_counter()

            # standardize refresh rate
            time_diff_s = toc-tic
            if time_diff_s < self.refresh_time:
                sleep(self.refresh_time - time_diff_s)


class stickController():

    def __init__(self, pose_point_queue, pose_dimensions, deadzone_radius):
        # input parameters
        self.pose_queue = pose_point_queue
        self.pose_width = pose_dimensions[0]
        self.pose_height = pose_dimensions[1]
        self.pose_center = pose_dimensions[2]
        self.deadzone_radius = deadzone_radius

        # import settings
        self.refresh_time = 1/face_aimer_settings['stick_refresh_rate']
        self.turn_speed_h = face_aimer_settings['turn_speed_h']
        self.turn_speed_v = face_aimer_settings['turn_speed_v']

        # initialize variables
        self.pose_point = self.pose_center
        self.move_allowed = False

    def start_controller(self, stop_controller_event):
        while(True):
            # get start time
            tic = perf_counter()

            # exit thread if stop event is set
            if stop_controller_event.isSet():
                return

            # check queue for new value
            try:
                self.pose_point = self.pose_queue.get(False)
                # if no face detected, stop moving
                if self.pose_point == (-1,-1):
                    self.pose_point = self.pose_center
                    self.move_allowed = False
                else:
                    self.move_allowed = True
            except queue.Empty:
                pass
            
            if self.move_allowed:
                # get distance from center of pose space
                delta_x = self.pose_point[0] - self.pose_center[0]
                delta_y = self.pose_point[1] - self.pose_center[1]

                # get distance from deadzone
                distance = sqrt(delta_x**2 + delta_y**2)
                deadzone_dist = distance - self.deadzone_radius

                # if outside the deadzone
                if deadzone_dist > 0:
                    # get sqrt of dist from center, add sign back
                    norm_x = abs(delta_x)/self.pose_width
                    norm_y = abs(delta_y)/self.pose_height
                    strength_x = copysign(norm_x, delta_x)
                    strength_y = copysign(norm_y, delta_y)
                    # move mouse
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(strength_x*self.turn_speed_h), int(strength_y*self.turn_speed_v))
                else:
                    pass
            
            # get end time
            toc = perf_counter()

            # standardize refresh rate
            time_diff_s = toc-tic
            if time_diff_s < self.refresh_time:
                sleep(self.refresh_time - time_diff_s)
