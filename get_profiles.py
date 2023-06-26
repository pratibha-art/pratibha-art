from onvif import ONVIFCamera
import cv2

# Create a camera object and connect to the camera
camera = ONVIFCamera('192.168.0.103', '80', 'admin', 'SMSS@2022')

# Create a media service object
media_service = camera.create_media_service()

# Get the profiles and print them
profiles = media_service.GetProfiles()
print(profiles)