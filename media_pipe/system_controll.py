import cv2
import mediapipe as mp
import numpy as np
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbc  # <-- missing earlier

# Setup MediaPipe
mp_hands = mp.solutions.hands
mp_drawings = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1)

# Setup volume
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
vol_range = volume.GetVolumeRange()
min_vol = vol_range[0]
max_vol = vol_range[1]

video = cv2.VideoCapture(0)
tipids = [4, 8, 12, 16, 20]  # all 5 fingers

while True:
    succ, img = video.read()
    img1 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(img1)
    lmlist = []
    gesture_name = ""

    if result.multi_hand_landmarks:
        for hand_lanmarks in result.multi_hand_landmarks:
             for id,lm in enumerate(hand_lanmarks.landmark):
                cx=lm.x
                cy=lm.y
                lmlist.append([id,cx,cy])
        if len(lmlist) == 21:
            fingerlist = []

            # Thumb logic (based on hand direction)
            if lmlist[12][1] < lmlist[20][1]:
                # Right hand
                if lmlist[4][1] > lmlist[3][1]:
                    fingerlist.append(1)
                else:
                    fingerlist.append(0)
            else:
                # Left hand
                if lmlist[4][1] < lmlist[3][1]:
                    fingerlist.append(1)
                else:
                    fingerlist.append(0)

            # Other fingers
            for i in range(1, 5):
                if lmlist[tipids[i]][2] < lmlist[tipids[i] - 2][2]:
                    fingerlist.append(1)
                else:
                    fingerlist.append(0)

            # Gesture conditions
            if fingerlist == [1, 0, 0, 0, 0]:
                        if lmlist[4][2]<lmlist[3][2]:
                            gesture_name = "Volume up"
                            current_vol = volume.GetMasterVolumeLevel()
                            new_vol = min(current_vol + 2.0, max_vol)
                            volume.SetMasterVolumeLevel(new_vol, None)
                        else:
                            gesture_name = "Volume Down"
                            current_vol = volume.GetMasterVolumeLevel()
                            new_vol = max(current_vol - 2.0, min_vol)
                            volume.SetMasterVolumeLevel(new_vol, None)
            elif fingerlist == [0, 1, 0, 0, 0]:
                gesture_name = "Brightness Up"
                curr = sbc.get_brightness(display=0)[0]
                sbc.set_brightness(min(curr + 10, 100))
                

            elif fingerlist == [0, 1, 1, 0, 0]:
                gesture_name = "Brightness Down"
                curr = sbc.get_brightness(display=0)[0]
                sbc.set_brightness(max(curr - 10, 0))
            

            # Display gesture name
            if gesture_name:
                cv2.putText(img, f'{gesture_name}', (10, 450), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0,0, 255), 2)
            mp_drawings.draw_landmarks(img,hand_lanmarks,mp_hands.HAND_CONNECTIONS)


    cv2.imshow("Gesture Volume/Brightness Control", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
