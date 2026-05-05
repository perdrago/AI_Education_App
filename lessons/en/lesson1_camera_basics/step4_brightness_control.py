# ============================================================
# LESSON 1: Camera Basics - Step 4
# TITLE: Brightness Control
# TITLE_VI: Điều Chỉnh Độ Sáng
# ============================================================

# Import camera, image processing, and display modules
import camera
import image
import display

# Step 1: Start the camera
# ✏️ INITIALIZE THE CAMERA
# __BLANK__ capture_camera = camera.Init_Camera()

print("[OK] Brightness controller ready!")

# Step 2: Adjust brightness in loop
while True:
    # ✏️ IN THE LOOP, GET A FRAME
    # __BLANK__ camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # ✏️ USE `ADJUST_BRIGHTNESS()` WITH `FACTOR=1.5` TO INCREASE BRIGHTNESS
    # __BLANK__ bright_frame = image.adjust_brightness(input_image = camera_frame, factor = 1.5)

    # ✏️ DISPLAY THE ADJUSTED IMAGE
    # __BLANK__ display.Show_Image(camera_frame = bright_frame)

# Step 3: Clean up
# ✏️ CLOSE THE CAMERA
# __BLANK__ camera.Close_Camera(capture_camera = capture_camera)

    pass  # Placeholder for blank lines