import cv2

ip_camera_url = 'rtsp://admin:SMSS@2022@192.168.0.103:554/main/1'

cap = cv2.VideoCapture(ip_camera_url)

if not cap.isOpened():
    print("Error opening the camera stream")
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        print("Error reading the frame")
        break

    cv2.imshow('IP Camera Stream', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()


