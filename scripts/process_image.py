from PIL import Image
import base64
import io

input_path = "/home/tele/.gemini/antigravity/brain/ce891ee6-db09-435a-bea5-10f3879a44eb/uploaded_image_1767354887862.jpg"
output_path = "profile_optimized.jpg"

try:
    with Image.open(input_path) as img:
        img = img.convert('RGB')
        img.thumbnail((400, 400)) # Resize to max 400x400
        img.save(output_path, "JPEG", quality=85)
        
    with open(output_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        print(f"BASE64_START{encoded_string}BASE64_END")
except Exception as e:
    print(f"Error: {e}")
