# ============================================================
# LESSON 1: Camera Basics - Step 1
# TITLE: My First Camera
# TITLE_VI: Camera Đầu Tiên Của Em
# ============================================================

# Import camera and display modules
import camera
import display

# Step 1: Start the camera
# ✏️ USE `INIT_CAMERA()` TO INITIALIZE THE CAMERA
# __BLANK__ capture_camera = camera.Init_Camera()

print("[OK] Camera is ready!")

while True:
    # Step 2: Show live video in a loop
    # ✏️ INSIDE THE `WHILE TRUE` LOOP, USE `GET_CAMERA_FRAME()` TO GET A FRAME
    # __BLANK__ camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)
    
    # Step 3: Display the frame
    # ✏️ USE `SHOW_IMAGE()` TO DISPLAY THE FRAME
    # __BLANK__ display.Show_Image(camera_frame = camera_frame)
    pass  # Placeholder for blank lines

# Step 4: Clean up when done
# ✏️ FINALLY, USE `CLOSE_CAMERA()` TO CLOSE THE CAMERA
# __BLANK__ camera.Close_Camera(capture_camera = capture_camera)

print("[OK] Camera closed.")
