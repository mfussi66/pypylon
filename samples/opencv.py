'''
A simple Program for grabing video from basler camera and converting it to opencv img.
Tested on Basler acA1300-200uc (USB3, linux 64bit , python 3.5)

'''
from pypylon import pylon
import cv2


# Get the transport layer factory.
tlFactory = pylon.TlFactory.GetInstance()

camera_devices = tlFactory.EnumerateDevices()

if len(camera_devices) == 0:
    raise pylon.RuntimeException("No camera present.")


# Create an array of instant cameras for the found devices and avoid exceeding a maximum number of devices.
cameras = pylon.InstantCameraArray(min(len(camera_devices), 2))

l = cameras.GetSize()

# Create and attach all Pylon Devices.
for i, cam in enumerate(cameras):
    cam.Attach(tlFactory.CreateDevice(camera_devices[i]))
    cam.Open()
    cam.Width.SetValue(1920)
    cam.Height.SetValue(1200)
    cam.BslScalingEnable.SetValue(True)
    # Print the model name of the camera.
    cam.AcquisitionFrameRate.SetValue(30.0)

    print("Using device ", cam.GetDeviceInfo().GetModelName())

# conecting to the first available camera
# camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

converter = pylon.ImageFormatConverter()

# converting to opencv bgr format
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

new_size = (1920, 1200)

# Grabing Continusely (video) with minimal delay
cameras.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
while cameras.IsGrabbing():
    grabResult_0 = cameras[0].RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
    grabResult_1 = cameras[1].RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grabResult_0.GrabSucceeded() and grabResult_1.GrabSucceeded():
        # Access the image data
        image0 = converter.Convert(grabResult_0)
        img0 = image0.GetArray()

        img0_resized = cv2.resize(img0, new_size)

        image1 = converter.Convert(grabResult_1)
        img1 = image1.GetArray()

        img1_resized = cv2.resize(img1, new_size)

        cv2.namedWindow('first camera', cv2.WINDOW_NORMAL)
        cv2.imshow('first camera', img0_resized)

        cv2.namedWindow('second camera', cv2.WINDOW_NORMAL)
        cv2.imshow('second camera', img1_resized)

        k = cv2.waitKey(1)
        if k == 27:
            break

    grabResult_0.Release()
    grabResult_1.Release()
    
# Releasing the resource    
cameras.StopGrabbing()

cv2.destroyAllWindows()
