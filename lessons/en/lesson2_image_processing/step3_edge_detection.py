# ============================================================
# LESSON 2: Image Processing - Step 3
# TITLE: Edge Detection
# TITLE_VI: Phát Hiện Cạnh
# ============================================================

# Import camera, image processing, and display modules
import camera
import image
import display

# Step 1: Start the camera
# ✏️ INITIALIZE THE CAMERA
# __BLANK__ capture_camera = camera.Init_Camera()

print("[OK] Edge detection ready!")

# Step 2: Detect edges in loop
while True:
    # ✏️ IN THE LOOP, GET A FRAME
    # __BLANK__ camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # ✏️ USE `DETECT_EDGES()` WITH `THRESHOLD1=100`, `THRESHOLD2=200`
    # __BLANK__ edges_frame = image.detect_edges(input_image = camera_frame, threshold1 = 100, threshold2 = 200)

    # ✏️ DISPLAY THE EDGE IMAGE
    # __BLANK__ display.Show_Image(camera_frame = edges_frame)

# Step 3: Clean up
# ✏️ CLOSE THE CAMERA
# __BLANK__ camera.Close_Camera(capture_camera = capture_camera)

    pass  # Placeholder for blank lines