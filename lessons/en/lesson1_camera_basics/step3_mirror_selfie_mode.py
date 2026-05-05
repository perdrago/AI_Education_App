# ============================================================
# LESSON 1: Camera Basics - Step 3
# TITLE: Mirror Selfie Mode
# TITLE_VI: Chế Độ Selfie Gương
# ============================================================

# Import camera, image processing, and display modules
import camera
import image
import display

# Step 1: Start the camera
# ✏️ INITIALIZE THE CAMERA
# __BLANK__ capture_camera = camera.Init_Camera()

print("[OK] Mirror mode activated!")

# Step 2: Show mirrored video
while True:
    # ✏️ IN THE LOOP, GET A FRAME FROM THE CAMERA
    # __BLANK__ camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

    # ✏️ USE `FLIP_IMAGE()` WITH `DIRECTION="HORIZONTAL"` TO FLIP THE IMAGE
    # __BLANK__ mirror_frame = image.flip_image(input_image = camera_frame, direction = 'horizontal')

    # ✏️ DISPLAY THE FLIPPED IMAGE
    # __BLANK__ display.Show_Image(camera_frame = mirror_frame)

# Step 3: Clean up
# ✏️ CLOSE THE CAMERA WHEN DONE
# __BLANK__ camera.Close_Camera(capture_camera = capture_camera)

    pass  # Placeholder for blank lines