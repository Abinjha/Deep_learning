import cv2
import mediapipe as mp
import pyttsx3
import time

mp_hand = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hand = mp_hand.Hands(max_num_hands=1)

engine = pyttsx3.init()
detected_word = ""
last_letter_time = 0
word_complete_timeout = 3
last_gesture = None
added = False

video = cv2.VideoCapture(0)
while True:
    success, img = video.read()
    img = cv2.flip(img, 1)
    img1 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hand.process(img1)
    tipids = [4, 8, 12, 16, 20]
    lmlist = []

    current_time = time.time()
    gesture_name = "Unknown"
    gesture_char = None

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            for id, lm in enumerate(hand_landmarks.landmark):
                cx = lm.x
                cy = lm.y
                lmlist.append([id, cx, cy])

            # ✅ FIXED: logic moved outside the loop
            if len(lmlist) == 21:
                fingerlist = []

                if lmlist[12][1] < lmlist[20][1]:
                    fingerlist.append(0)
                else:
                    fingerlist.append(1)

                for i in range(1, 5):  # Index to pinky
                    if lmlist[tipids[i]][2] > lmlist[tipids[i]-2][2]:
                        fingerlist.append(0)
                    else:
                        fingerlist.append(1)

                finger_tuple = tuple(fingerlist)

                if fingerlist == [0, 0, 0, 0, 0]:
                    gesture_name = "SPACE"
                    gesture_char = " "
                else:
                    pattern_map = {
                        (1, 0, 0, 0, 0): "A",
                        (0, 1, 1, 1, 1): "B",
                        (0, 1, 0, 0, 0): "D",
                    }

                    gesture_char = pattern_map.get(finger_tuple)
                    if gesture_char:
                        gesture_name = gesture_char

                if gesture_char and gesture_name != last_gesture and not added:
                    detected_word += gesture_char
                    last_letter_time = current_time
                    last_gesture = gesture_name
                    added = True

            mp_drawing.draw_landmarks(img, hand_landmarks, mp_hand.HAND_CONNECTIONS)
    else:
        last_gesture = None
        added = False

    if last_gesture != gesture_name:
        added = False

    if time.time() - last_letter_time > word_complete_timeout and detected_word:
        engine.say(f"{detected_word.strip()}")
        engine.runAndWait()
        print("✅ Spoken:", detected_word.strip())
        detected_word = ""
        last_gesture = None
        added = False

    cv2.putText(img, f"Gesture: {gesture_name}", (30, 370), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(img, f"Text: {detected_word[-30:]}", (30, 420), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("ASL A-Z + Sentence Mode", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
