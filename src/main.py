import cv2
from models.detector import ObjectDetector
from utils.image_utils import load_image, save_image

def main():
    # Initialize the object detection model
    detector = ObjectDetector()
    detector.load_model('path/to/pretrained/model')

    # Load an image for detection
    image = load_image('path/to/image.jpg')

    # Process the image for detection
    detections = detector.detect_objects(image)

    # Draw detections on the image
    output_image = detector.draw_detections(image, detections)

    # Save the output image with detections
    save_image(output_image, 'path/to/output_image.jpg')

if __name__ == "__main__":
    main()