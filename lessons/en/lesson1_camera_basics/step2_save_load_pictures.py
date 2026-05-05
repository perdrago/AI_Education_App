# ============================================================
# LESSON 1: Camera Basics - Step 2
# TITLE: Save & Load Pictures
# TITLE_VI: Lưu Và Tải Ảnh
# ============================================================

# Import camera and display modules
import camera
import display

# Step 1: Start the camera
# ✏️ INITIALIZE THE CAMERA
# __BLANK__ capture_camera = camera.Init_Camera()

# Step 2: Capture one frame
# ✏️ GET A FRAME FROM THE CAMERA
# __BLANK__ camera_frame = camera.Get_Camera_Frame(capture_camera = capture_camera)

# Step 3: Save the frame
# ✏️ USE `SAVE_FRAME()` TO SAVE THE IMAGE WITH NAME "MY_PHOTO.JPG"
# __BLANK__ camera.Save_Frame(camera_frame = camera_frame, file_path = 'my_photo.jpg')

# Step 4: Close the camera
# ✏️ CLOSE THE CAMERA
# __BLANK__ camera.Close_Camera(capture_camera = capture_camera)

# Step 5: Load the saved image
# ✏️ USE `LOAD_IMAGE()` TO LOAD THE SAVED IMAGE
# __BLANK__ loaded_image = camera.Load_Image(file_path = 'my_photo.jpg')

# Step 6: Display the loaded image
# ✏️ DISPLAY THE LOADED IMAGE
# __BLANK__ display.Show_Image(camera_frame = loaded_image)

print("[OK] Photo saved and loaded!")
