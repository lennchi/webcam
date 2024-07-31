import cv2
import time
import glob
import os
from datetime import datetime
from emaling import send_email


video = cv2.VideoCapture(0)
time.sleep(1)

init_frame = None
status_list = []


def clear_img_folder():
    """Clear the images folder"""
    img_folder = glob.glob("img/*.png")
    for img in img_folder:
        os.remove(img)


while True:
    status = 0  # Status 0 means no movement in frame

    # Check if cam is working, start making frames
    check, frame = video.read()

    # Convert to grayscale and apply blur to optimize
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_frame_gau = cv2.GaussianBlur(gray_frame, (21, 21), 0)  # (21, 21) is the amount of blur, 0 is st deviation
#    cv2.imshow("My vid", frame)  # My vid is the name of the window
#    cv2.imshow("My vid",gray_frame_gau)

    # Store the initial frame as reference
    if init_frame is None:
        init_frame = gray_frame_gau

    # Check diff btw init frame and current frame
    delta_frame = cv2.absdiff(init_frame, gray_frame_gau)

    # Set threshold: any pixel >= 30 will be assigned the value of 255
    thresh_frame = cv2.threshold(delta_frame, 60, 255, cv2.THRESH_BINARY)[1]

    # Increase the white area or size of an object boundary; reduce noise/enchance features in binary images
    dil_frame = cv2.dilate(thresh_frame, None, iterations=2)

#    cv2.imshow("My vid", dil_frame)

    # Create contours around white areas
    contours, check = cv2.findContours(dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter out small/uninteresting objects
    for contour in contours:
        if cv2.contourArea(contour) < 4000:
            continue

        # Get coors, width and height of the moving object
        x, y, w, h = cv2.boundingRect(contour)
        # Create rectangle on frame, coors of top left and bottom right corners; color; border thickness
        rectangle = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 3)

        # Change status if there's movement in frame
        if rectangle.any():
            status = 1

            # Save img
            now = datetime.now()
            ts = now.strftime("%Y%m%d%H%M%S%f")
            cv2.imwrite(f"img/{ts}.png", frame)

            all_img = glob.glob("img/*.png")
            index = int(len(all_img) / 2)
            img_with_movement = all_img[index]

    # Get the last two statuses to see if the object has existed the frame
    status_list.append(status)
    status_list = status_list[-2:]

    # When the object exists the frame, send email
    if status_list[0] == 1 and status_list[1] == 0:
        send_email(img_with_movement)
        clear_img_folder()

    cv2.imshow("Video", frame)
    key = cv2.waitKey(1)

    # Press q to stop the cam
    if key == ord("q"):
        break

video.release()


