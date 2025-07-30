from ultralytics import YOLO
import matplotlib.pyplot as plt
from tts.tts import text_to_speech
import os
from utils.grammar import get_plural, get_article
from collections import Counter

# # Load a YOLO11n PyTorch model
# model = YOLO("yolo11n.pt")

# # Export the model to NCNN format
# model.export(format="ncnn")  # creates 'yolo11n_ncnn_model'

# Load the exported NCNN model
ncnn_model = YOLO("src/yolo11n_ncnn_model")

image_formats = ['.jpg', '.jpeg', '.png']

# Get all image files in the current directory
image_dir = 'src/data'
image_files = [f for f in os.listdir(image_dir) if os.path.splitext(f)[1].lower() in image_formats]
ALLOWED_NAMES = {'person', 'bench', 'bicycle', 'umbrella', 'book', 'bus', 'car', 'bed', 'truck', 'chair'}

for i, image in enumerate(image_files, start=1):
    results = ncnn_model(f'{image_dir}/{image}', conf=0.5)

    allowed_boxes = []
    detected_names = []

    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        name = results[0].names[cls_id]
        if name in ALLOWED_NAMES:
            allowed_boxes.append(box)
            detected_names.append(name)

    results[0].boxes = allowed_boxes

    if detected_names:
        annotated_img = results[0].plot()
        plt.imshow(annotated_img[:, :, ::-1])
        plt.axis('off')
        plt.show()
        
        counts = Counter(detected_names)
        text_to_speech(f'image {i}')
        for name, count in counts.items():
            text_to_speech(f"I can identify {get_article(count, name)} {name if count == 1 else get_plural(name)}")

        