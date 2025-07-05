import cv2
import mediapipe as mp
import pyttsx3
import time

mp_hand=mp.solutions.hands
mp_drawing=mp.solutions.drawing_utils
hand=mp_hand.Hands(max_num_hands=1)


engine = pyttsx3.init()
engine.setProperty('rate', 150)

video=cv2.VideoCapture(0)
prev_gesture = ""
word = ""
last_spoken_time = time.time()
while True:
    sucess,img=video.read()
    img1=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    result=hand.process(img1)
    tipids=[4,8,12,16,20]
    lmlist=[]

    if result.multi_hand_landmarks:
        for hand_lanmarks in result.multi_hand_landmarks:
            for id,lm in enumerate(hand_lanmarks.landmark):
                cx=lm.x
                cy=lm.y
                lmlist.append([id,cx,cy])
            if len(lmlist)==21:
                    fingerlist=[]
                    if lmlist[12][1]<lmlist[20][1]:
                        if lmlist[4][1]>lmlist[3][1]:
                            fingerlist.append(0)
                        else:
                            fingerlist.append(1)
                    else:
                        if lmlist[4][1]<lmlist[3][1]:
                            fingerlist.append(0)
                        else:
                            fingerlist.append(1)
                    for i in range(1,5):
                        if lmlist[tipids[i]][2]>lmlist[tipids[i]-2][2]:
                            fingerlist.append(0)
                        else:
                            fingerlist.append(1)
                    # Gesture recognition
                    gesture_name = "Unknown"
                    if (fingerlist) ==[1, 0, 0, 0, 0]:
                        gesture_name = "A"
                    elif (fingerlist) == [0,1,1,1,1]:
                            gesture_name = "B"
                    elif (fingerlist) ==[0, 1, 0, 0, 0]:
                        gesture_name = "D"
                    elif (fingerlist) ==[0, 0, 0, 0, 0]:
                        gesture_name = "E"
                    elif (fingerlist) ==[0, 0, 1, 1, 1]:
                        gesture_name = "F"
                    elif (fingerlist) ==[0,1,1,0,0]:
                        gesture_name = "H"
                    elif (fingerlist)==[0,0,0,0,1]:
                        gesture_name="I"
                    elif fingerlist == [1, 1, 1, 1, 1]:  # All fingers up = Space
                        gesture_name = "Space"
                    elif fingerlist == [0,1,1,1,0]:
                        gesture_name = "Submit"

                # Add to word only if gesture changes
                    current_time = time.time()
                    if gesture_name != "Unknown" and gesture_name != prev_gesture:
                        if gesture_name == "Space":
                           word += " "
                        elif gesture_name=="Submit":
                           if word.strip() != "":
                               engine.say(word.strip())
                               engine.runAndWait()
                               word= " "
                        else:
                            word += gesture_name
                        prev_gesture = gesture_name
                        last_spoken_time = current_time

                    cv2.putText(img, f"Gesture: {gesture_name}", (35, 370),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

            mp_drawing.draw_landmarks(img, hand_lanmarks, mp_hand.HAND_CONNECTIONS)

    # Show the current word on screen
    cv2.putText(img, f"Word: {word}", (35, 420),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    cv2.imshow("Sign Language to Voice", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()


                    
