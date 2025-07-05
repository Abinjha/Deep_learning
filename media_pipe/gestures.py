import cv2
import mediapipe as mp

mp_hand=mp.solutions.hands
mp_drawing=mp.solutions.drawing_utils
hand=mp_hand.Hands(max_num_hands=1)

video=cv2.VideoCapture(0)
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
                if len(lmlist)!=0 and len(lmlist)==21:
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
                    if (fingerlist) ==[0, 0, 0, 0, 0]:
                        gesture_name = "Power"
                    elif (fingerlist) == [1, 0, 0, 0, 0]:
                        if lmlist[4][2]<lmlist[3][2]:
                            gesture_name = "Like"
                        else:
                            gesture_name="Dislike"
                    elif (fingerlist) ==[0, 1, 1, 0, 0]:
                        gesture_name = "Peace"
                    elif (fingerlist) ==[0, 1, 0, 0, 1]:
                        gesture_name = "Rock"
                    elif (fingerlist) ==[1, 0, 0, 0, 1]:
                        gesture_name = "Call Me"
                    elif (fingerlist) ==[1, 1, 1, 1, 1]:
                        gesture_name = "hai"
                    elif (fingerlist)==[1,1,0,0,0]:
                        gesture_name="L"
                    elif (fingerlist)==[0,0,1,1,1]:
                        gesture_name="Ok"
                    elif (fingerlist)==[0,1,0,0,0]:
                        if lmlist[8][2]<lmlist[7][2]:
                            gesture_name="Up"
                        elif lmlist[8][2]>lmlist[7][2]:
                            gesture_name="Down"


                    cv2.putText(img, f"Gesture: {gesture_name}", (35, 370),cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
            mp_drawing.draw_landmarks(img,hand_lanmarks,mp_hand.HAND_CONNECTIONS)

    cv2.imshow("finger_count",img)
    if cv2.waitKey(1)&0XFF==ord('q'):
        break
video.release()
cv2.destroyAllWindows()
