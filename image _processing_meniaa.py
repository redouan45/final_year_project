import cv2
#opencv ver : 4.5.4.60
cap_y = 180
cap_x = 250
cap_h = 80
cap_w = 120
label_x = 265
label_y = 330
label_w = 120
label_h = 120
cap = cv2.VideoCapture(1)
cv2.useOptimized()
while True:
    succcess, frame = cap.read()
    if succcess:
        #TODO: CAP IMAGE PROCESSING
        hmin = 40; hmax = 179;smin = 35; smax = 255;vmin = 0;vmax = 250
        roi_label = frame[label_y:(label_y + label_h), label_x:(label_x + label_w)]
        roi_cap = frame[cap_y:(cap_y + cap_h), cap_x:(cap_x + cap_w)]
        #cap image processing:
        hsv_cap = cv2.cvtColor(roi_cap, cv2.COLOR_BGR2HSV)
        hsv_blurred_cap = cv2.GaussianBlur(hsv_cap, (5,5), 3)
        color_mask_cap = cv2.inRange(hsv_blurred_cap, (hmin, smin, vmin), (hmax, smax, vmax))
        eroded_cap = cv2.erode(color_mask_cap, (3, 3), iterations=1)
        dialated_cap = cv2.dilate(eroded_cap, (3, 3), iterations=1)
        #edge detection:
        edges_cap = cv2.Canny(dialated_cap, 200, 230)
        dil_edges_cap = cv2.dilate(edges_cap , (3,3))
        contours_cap, hirearchy_cap = cv2.findContours(dil_edges_cap, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        #drawing on original frame cap:
        for i in range(len(contours_cap)):
            if 850 < cv2.contourArea(contours_cap[i]) < 1200:
                cv2.drawContours(frame, contours_cap, i, (0, 255, 0), 1, offset=(250, 180))
                cv2.putText(frame, "Cap detected", (400, 400), cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 255, 0), 2)
                break
            elif 0 <= cv2.contourArea(contours_cap[i]) < 250:
                pass
            else:
                cv2.putText(frame, "Cap not detected", (400, 400), cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 0, 255), 2)
                break
        #TODO:label image processing:
        blurr_roi_label = cv2.GaussianBlur(roi_label, (5, 5), 3)
        hsv_label = cv2.cvtColor(blurr_roi_label , cv2.COLOR_BGR2HSV)
        label_mask = cv2.inRange(hsv_label, (50, 0, 0), (179, 255, 180))
        eroded_label_mask = cv2.erode(label_mask, (3,3) , iterations=1)
        dil_label_mask  =cv2.dilate(eroded_label_mask, (3,3) , iterations=3)
        # edge detection:
        edges_label = cv2.Canny(dil_label_mask, 200, 230 )
        dil_edges_label = cv2.dilate(edges_label, (3, 3))
        contours_label, hirearchy_label = cv2.findContours(dil_edges_label, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        # drawing on original frame label:

        for i in range(len(contours_label)):
            if 4000<= cv2.contourArea(contours_label[i]) < 4550 :
                cv2.drawContours(frame, contours_label, i, (0, 255, 0), 1, offset=(265, 327))
                cv2.putText(frame, "label detected", (150, 400), cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 255, 0), 2)
                break
            elif 500 < cv2.contourArea(contours_label[i]) < 4000:
                cv2.drawContours(frame, contours_label, i, (0, 0, 255), 1, offset=(265, 327))
                cv2.putText(frame, "label not detected", (150, 400), cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 0, 255), 2)
                break

        cv2.imshow("cap",  roi_cap)
        cv2.imshow("mask cap",  label_mask)
        cv2.imshow("erode mask cap",  eroded_label_mask)
        cv2.imshow("dilated label mask",  dil_label_mask)
        cv2.imshow("label edges",  edges_label)

        cv2.imshow("processed_frame",  frame)

        cv2.waitKey(1)

    else:
        pass
