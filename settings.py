# settings dictionary for face_aimer.py

face_aimer_settings = {
    'default_control_mode' : 'stick', # 'stick' or 'mouse'
    'res_x' : 2560, # horizontal resolution
    'res_y' : 1440, # vertical resolution
    'controller_deadzone_threshold' : 0.30, # stick controls - deadzone as a % radius from the center of total facial pose space
    'stick_refresh_rate' : 250, # refresh rate for stick controls in Hz
    'mouse_refresh_rate' : 250, # refresh rate for mouse controls in Hz
    'turn_speed_h' : 35, # stick controls - horizontal turn speed
    'turn_speed_v' : 30, # stick controls - vertical turn speed
    'move_speed' : 80, # mouse controls - mouse movement speed
    'move_smoothing' : 4, # mouse controls - how many camera frames to buffer (increases smoothness, adds latency)
    'marker_color_bgr' : (255,255,0),
    'gaze_line_color_bgr' : (255, 255, 0),
    'deadzone_color_bgr' : (0, 255, 0),
    'facial_landmarks_color_bgr' : (0, 0, 255)
}