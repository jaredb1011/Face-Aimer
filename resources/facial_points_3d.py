import numpy as np

# To figure our the angle of the face, we need to map the tracked landmarks from the 68-pt dlib model to points in 3D space.
# This array contains 3D coordinates for all the dlib points (see facial_landmarks_68markup.jpg).
# The scale of the points is arbitrary, but the relative spacing between each other is what matters.
# The tip of the nose (landmark 33 in this array) is the origin from which other points are defined.

model_points = np.array([
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
            (-300.0,235.0,-140.0),      # 17 - right eyebrow
            (-260.0,245.0,-120.0),      # 18 - right eyebrow
            (-215.0,250.0,-110.0),      # 19 - right eyebrow
            (-160.0,245.0,-100.0),      # 20 - right eyebrow
            (-110.0,240.0,-90.0),       # 21 - right eyebrow
            (110.0,240.0,-90.0),        # 22 - left eyebrow
            (160.0,245.0,-100.0),       # 23 - left eyebrow
            (215.0,250.0,-110.0),       # 24 - left eyebrow
            (260.0,245.0,-120.0),       # 25 - left eyebrow
            (300.0,235.0,-140.0),       # 26 - left eyebrow
            (0.0, 170.0, -100.0),       # 27 - top of nose
            (0.0, 130.0, -55.0),        # 28 - middle of nose
            (0.0, 90.0, -30.0),         # 29 - middle of nose
            (0.0, 50.0, -15.0),         # 30 - middle of nose
            (-60.0, 15.0, -30.0),       # 31 - nose tip right
            (-30.0, 5.0, -15.0),        # 32 - nose tip right
            (0.0, 0.0, 0.0),            # 33 - nose tip middle
            (30.0, 5.0, -15.0),         # 34 - nose tip left
            (60.0, 15.0, -30.0),        # 35 - nose tip left
            (-240.0, 170.0, -135.0),    # 36 - Right eye
            (-200.0,185.0,-135.0),      # 37 - Right eye
            (-160.0,185.0,-135.0),      # 38 - Right eye
            (-115.0,170.0,-135.0),      # 39 - Right eye
            (-160.0,155.0,-135.0),      # 40 - Right eye
            (-200.0,155.0,-135.0),      # 41 - Right eye
            (115.0,170.0,-135.0),       # 42 - left eye
            (160.0,185.0,-135.0),       # 43 - left eye
            (200.0,185.0,-135.0),       # 44 - left eye
            (240.0,170.0,-135.0),       # 45 - left eye
            (200.0,155.0,-135.0),       # 46 - left eye
            (160.0,155.0,-135.0),       # 47 - left eye
            (-150.0, -150.0, -125.0),   # 48 - outer lips
            (-100.0,-115.0,-115.0),     # 49 - outer lips
            (-50.0,-95.0,-110.0),       # 50 - outer lips
            (0.0,-100.0,-105.0),        # 51 - outer lips
            (50,-95.0,-110.0),          # 52 - outer lips
            (100,-115.0,-115.0),        # 53 - outer lips
            (150.0,-150.0,-125.0),      # 54 - outer lips
            (100,-180.0,-115.0),        # 55 - outer lips
            (50,-195.0,-110.0),         # 56 - outer lips
            (0,-200.0,-105.0),          # 57 - outer lips
            (-50,-195.0,-110.0),        # 58 - outer lips
            (-100,-180.0,-115.0),       # 59 - outer lips
            (-100,-145.0,-125.0),       # 60 - inner lips
            (-50,-130.0,-125.0),        # 61 - inner lips
            (0,-125.0,-125.0),          # 62 - inner lips
            (50,-130.0,-125.0),         # 63 - inner lips
            (100,-145.0,-125.0),        # 64 - inner lips
            (50,-165.0,-125.0),         # 65 - inner lips
            (0,-170.0,-125.0),          # 66 - inner lips
            (-50,-165.0,-125.0)         # 67 - inner lips
        ], dtype=np.float64)