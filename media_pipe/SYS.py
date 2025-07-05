import cv2
import mediapipe as mp
import numpy as np
import math
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawings = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1)

# Volume setup
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
vol_range = volume.GetVolumeRange()
min_vol = vol_range[0]
max_vol = vol_range[1]

# Open webcam
video = cv2.VideoCapture(0)

while True:
    success, img = video.read()
    if not success:
        break

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)

    lmlist = []
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawings.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            h, w, _ = img.shape
            for id, lm in enumerate(hand_landmarks.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmlist.append([id, cx, cy])

        if len(lmlist) == 21:
            # Volume: Thumb (4) & Index (8)
            x1, y1 = lmlist[4][1], lmlist[4][2]
            x2, y2 = lmlist[8][1], lmlist[8][2]
            cx1, cy1 = (x1 + x2) // 2, (y1 + y2) // 2
            dist1 = math.hypot(x2 - x1, y2 - y1)

            # Brightness: Index (8) & Middle (12)
            x3, y3 = lmlist[8][1], lmlist[8][2]
            x4, y4 = lmlist[12][1], lmlist[12][2]
            cx2, cy2 = (x3 + x4) // 2, (y3 + y4) // 2
            dist2 = math.hypot(x4 - x3, y4 - y3)

            # Volume Control
            vol = np.interp(dist1, [30, 200], [min_vol, max_vol])
            volume.SetMasterVolumeLevel(vol, None)
            vol_per = int(np.interp(dist1, [30, 200], [0, 100]))

            # Brightness Control
            brightness = int(np.interp(dist2, [10, 200], [0, 100]))
            sbc.set_brightness(brightness)
            
            # Draw Volume Control
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.circle(img, (cx1, cy1), 8, (0, 255, 0), cv2.FILLED)
            cv2.rectangle(img, (50, 150), (85, 400), (0, 0, 255), 2)
            vol_bar = int(np.interp(dist1, [30, 200], [400, 150]))
            cv2.rectangle(img, (50, vol_bar), (85, 400), (0, 0, 255), cv2.FILLED)
            cv2.putText(img, f'Volume: {vol_per}%', (40, 430), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            # Draw Brightness Control
            cv2.line(img, (x3, y3), (x4, y4), (255, 255, 0), 2)
            cv2.circle(img, (cx2, cy2), 8, (255, 255, 0), cv2.FILLED)
            cv2.putText(img, f'Brightness: {brightness}%', (300, 430), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Volume + Brightness Control", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
