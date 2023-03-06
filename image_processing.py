import cv2
cap_y = 210
cap_x = 245
cap_h = 80
cap_w = 120
label_x = 245
label_y = 275
label_w = 120
label_h = 65
H_low = 0
H_high = 179
S_low= 0
S_high = 255
V_low= 0
V_high = 255


cap = cv2.VideoCapture(0)
while True:
    succcess, frame = cap.read()
    if succcess:
        hmin = 85; hmax = 120;smin = 35; smax = 255;vmin = 35;vmax = 230
        roi_label = frame[label_y:(label_y + label_h), label_x:(label_x + label_w)]
        roi_cap = frame[cap_y:(cap_y + cap_h), cap_x:(cap_x + cap_w)]
        #cap image processing:
        hsv_cap = cv2.cvtColor(roi_cap, cv2.COLOR_BGR2HSV)
        hsv_blurred_cap = cv2.GaussianBlur(hsv_cap, (5, 5), 5, None, 5)
        color_mask_cap = cv2.inRange(hsv_blurred_cap, (hmin, smin, vmin), (hmax, smax, vmax))
        eroded_cap = cv2.erode(color_mask_cap, (3, 3), iterations=11)
        dialated_cap = cv2.dilate(eroded_cap, (3, 3), iterations=11)
        #edge detection:
        edges_cap = cv2.Canny(dialated_cap, 200, 230)
        dil_edges_cap = cv2.dilate(edges_cap , (3,3))
        contours_cap, hirearchy_cap = cv2.findContours(dil_edges_cap, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        #drawing on original frame cap:
        for i in range(len(contours_cap)):
            if 500 < cv2.contourArea(contours_cap[i]) < 2400:
                cv2.drawContours(frame, contours_cap, i, (0, 255, 0), 1, offset=(245, 200))
                cv2.putText(frame, "Cap detected", (400, 400), cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 255, 0), 2)
                break
            else:
                cv2.putText(frame, "Cap not detected", (400, 400), cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 0, 255), 2)
        #TODO:label image processing :
        hsv_label = cv2.cvtColor(roi_label , cv2.COLOR_BGR2HSV)
        # edge detection:
        edges_label = cv2.Canny(roi_label, S_low, S_high)
        dil_edges_label = cv2.dilate(edges_label, (3, 3))
        contours_label, hirearchy_label = cv2.findContours(dil_edges_label, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # drawing on original frame label:

        for i in range(len(contours_label)):
            if 1800< cv2.contourArea(contours_label[i]) < 2500 :
                cv2.drawContours(frame, contours_label, i, (0, 255, 0), 1, offset=(245, 270))
                print(cv2.contourArea(contours_label[i]))
                cv2.putText(frame, "label detected", (150, 400), cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 255, 0), 2)

            elif 160<cv2.contourArea(contours_label[i])< 1800  :
                cv2.drawContours(frame, contours_label, i, (0, 0, 255), 1, offset=(245, 270))
                print(f"bad area : {cv2.contourArea(contours_label[i])}")
                cv2.putText(frame, "label not detected", (150, 400), cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 0, 255), 2)

        cv2.imshow("label",  roi_label)

        cv2.imshow("label edges",  edges_label)
        cv2.imshow("feed", frame)
        cv2.waitKey(33)

    else:
        pass
