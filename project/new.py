import cv2
import mediapipe as mp
import pyttsx3
import time
import math

# Pose setup
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose()

# Speech engine
engine = pyttsx3.init()

# Word and gesture tracking
detected_word = ""
last_detect_time = 0
speak_timeout = 3
last_gesture = None
added = False

# Track head movement
prev_nose_x = None
prev_nose_y = None
head_movement_timer = time.time()

# Distance helper function
def distance(p1, p2):
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

# Start video
video = cv2.VideoCapture(0)

while True:
    success, img = video.read()
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = pose.process(img_rgb)

    current_time = time.time()
    gesture_name = "Unknown"
    gesture_char = None

    if result.pose_landmarks:
        lm = result.pose_landmarks.landmark

        # Landmarks
        rw = lm[mp_pose.PoseLandmark.RIGHT_WRIST]
        lw = lm[mp_pose.PoseLandmark.LEFT_WRIST]
        re = lm[mp_pose.PoseLandmark.RIGHT_ELBOW]
        rs = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        le = lm[mp_pose.PoseLandmark.LEFT_ELBOW]
        ls = lm[mp_pose.PoseLandmark.LEFT_SHOULDER]
        nose = lm[mp_pose.PoseLandmark.NOSE]

         # SIGN: Goodbye – left wrist above nose
        if rw.y < nose.y:
            gesture_name = "Goodbye"
            gesture_char = " Goodbye "

        # SIGN: Namaste – wrists close together
        elif distance(rw, lw) < 0.1:
            gesture_name = "Namaste"
            gesture_char = " Namaste "

        # SIGN: Sorry – left wrist near right shoulder
        elif distance(rw, ls) < 0.15:
            gesture_name = "Sorry"
            gesture_char = " Sorry "

        # SIGN: Eat – right wrist near mouth
        elif distance(rw, nose) < 0.15:
            gesture_name = "Eat"
            gesture_char = " Eat "

        # SIGN: Drink – wrist near nose & elbow raised
        elif distance(rw, nose) < 0.15 and re.y > rw.y:
            gesture_name = "Drink"
            gesture_char = " Drink "


        # SIGN: Help – wrists close together below face
        elif distance(rw, lw) < 0.15 and rw.y > nose.y:
            gesture_name = "Help"
            gesture_char = " Help "



        # SIGN: Yes – head nod (downward)
        elif prev_nose_y and (nose.y - prev_nose_y) > 0.05 and current_time - head_movement_timer < 1:
            gesture_name = "Yes"
            gesture_char = " Yes "

        # SIGN: No – head shake (side movement)
        elif prev_nose_x and abs(nose.x - prev_nose_x) > 0.03 and current_time - head_movement_timer < 0.8:
            gesture_name = "No"
            gesture_char = " No "
        # SIGN: Goodnight – right wrist near left side of head (like sleeping gesture)
        elif distance(rw, nose) < 0.2 and rw.x < nose.x:
            gesture_name = "Goodnight"
            gesture_char = " Goodnight "
        # SIGN: Thank You – right hand near chin and slightly to the right
        elif distance(rw, nose) < 0.15 and rw.x > nose.x:
            gesture_name = "Thank You"
            gesture_char = " Thank You "




        # Update nose position for head movement detection
        prev_nose_x = nose.x
        prev_nose_y = nose.y
        head_movement_timer = current_time

        # Draw pose landmarks
        mp_drawing.draw_landmarks(img, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # Handle new gesture
        if gesture_char and gesture_name != last_gesture and not added:
            detected_word += gesture_char
            engine.say(gesture_char)
            engine.runAndWait()
            last_detect_time = current_time
            last_gesture = gesture_name
            added = True

    else:
        last_gesture = None
        added = False

    # Speak entire sentence if timeout
    if time.time() - last_detect_time > speak_timeout and detected_word.strip():
        engine.say(detected_word.strip())
        engine.runAndWait()
        print("✅ Spoken:", detected_word.strip())
        detected_word = ""
        last_gesture = None
        added = False

    # Overlay text
    cv2.putText(img, f"Gesture: {gesture_name}", (30, 370), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(img, f"Text: {detected_word[-30:]}", (30, 420), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Show video
    cv2.imshow("ISL Pose-Based Sign Recognition", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
