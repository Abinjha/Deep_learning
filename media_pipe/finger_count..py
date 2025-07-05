import cv2
import mediapipe as mp

mp_hands=mp.solutions.hands
mp_drawing=mp.solutions.drawing_utils
hand=mp_hands.Hands(max_num_hands=1)

video=cv2.VideoCapture(0)

while True:
    sucess,img=video.read()
    img1=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    result=hand.process(img1)
    # print(result.multi_hand_landmarks)
    tipids=[4,8,12,16,20]
    lmlist=[]

    if result.multi_hand_landmarks:
        for hand_lanmarks in result.multi_hand_landmarks:
            for id,lm in enumerate(hand_lanmarks.landmark):
                # print(id,lm)
                cx=lm.x
                cy=lm.y
                lmlist.append([id,cx,cy])
                # print(lmlist)
                if len(lmlist)!=0 and len(lmlist)==21:
                    fingerlist=[]
                    #thumb
                    if lmlist[12][1]<lmlist[20][1]:   #12x<20x
                        if lmlist[4][1]>lmlist[3][1]:
                            fingerlist.append(0)
                        else:
                            fingerlist.append(1)
                    else:
                        if lmlist[4][1]<lmlist[3][1]:
                            fingerlist.append(0)
                        else:
                            fingerlist.append(1)
                    for i in range(1,5):#all finger except thumb
                        if lmlist[tipids[i]][2]>lmlist[tipids[i]-2][2]: #iy<i=2y
                            fingerlist.append(0)
                        else:
                            fingerlist.append(1)
                    # print(fingerlist)
                    if len(fingerlist)!=0:
                        finger_count=fingerlist.count(1)
                    # print(finger_count)
                    cv2.putText(img,"count:"+str(finger_count),(35,425),cv2.FONT_HERSHEY_COMPLEX,2,(255,0,0),2)
            mp_drawing.draw_landmarks(img,hand_lanmarks,mp_hands.HAND_CONNECTIONS)

    
    cv2.imshow("finger_count",img)
    if cv2.waitKey(1)&0XFF==ord('q'):
        break
video.release()
cv2.destroyAllWindows()
