from ultralytics import YOLO
import cv2
import numpy as np
from tts.tts import text_to_speech
from utils.grammar import get_plural, get_article
from collections import Counter
import time

class RealTimeYOLO:
    def __init__(self, model_path="src/yolo11n_ncnn_model", conf_threshold=0.5):
        """Initialize the real-time YOLO inference system."""
        self.model = YOLO(model_path, task='detect')
        self.conf_threshold = conf_threshold
        self.allowed_names = {
            'person',
            'bench',
            'bicycle',
            'umbrella',
            'book',
            'bus',
            'car',
            'motorcycle',
            'bed',
            'truck',
            'chair',
            'cell phone', 
            'mouse', -
            'keyboard',
            'laptop',
            'tie',
            'bottle',
            'remote',
            'tv', 
            'couch',
            'cup',
            'spoon',
            'fork',
            'knife',
            'bowl',
            'clock'
            }
        
        # For detection tracking
        self.last_detection_time = 0
        self.detection_interval = 1  # Announce detections every 1 second
                
    def announce_detections(self, detected_names):
        """Announce detections immediately using text-to-speech."""
        if detected_names:
            counts = Counter(detected_names)
            for name, count in counts.items():
                announcement = f"I can identify {get_article(count, name)} {name if count == 1 else get_plural(name)}"
                text_to_speech(announcement)
    
    def process_frame(self, frame):
        """Process a single frame and return annotated frame with detections."""
        current_time = time.time()
        
        # Only process frames at the specified interval
        if current_time - self.last_detection_time >= self.detection_interval:
            results = self.model(frame, conf=self.conf_threshold, verbose=False)
            
            allowed_boxes = []
            detected_names = []
            
            if results[0].boxes is not None:
                for box in results[0].boxes:
                    cls_id = int(box.cls[0])
                    name = results[0].names[cls_id]
                    if name in self.allowed_names:
                        allowed_boxes.append(box)
                        detected_names.append(name)
            
            # Update results with filtered boxes
            results[0].boxes = allowed_boxes if allowed_boxes else None
            
            # Get annotated frame
            annotated_frame = results[0].plot() if allowed_boxes else frame
            
            # Queue speech announcements
            self.announce_detections(detected_names)
            
            # Update last detection time
            self.last_detection_time = current_time
            
            return annotated_frame, detected_names
        else:
            # Return original frame without processing when not at interval
            return frame, []

def run_pi_camera_inference():
    """Run real-time inference using Raspberry Pi camera."""
    # Initialize YOLO system
    yolo_system = RealTimeYOLO()
    
    # Initialize Pi camera using OpenCV
    # For Pi Camera Module, use index 0 or try different indices
    cap = cv2.VideoCapture(0)
    
    # Set camera properties for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    print("Starting real-time inference. Press 'q' to quit.")
    
    frame_count = 0
    fps_counter = time.time()
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame")
                break
            
            # Process frame
            annotated_frame, detections = yolo_system.process_frame(frame)
            
            # Add FPS counter
            frame_count += 1
            if frame_count % 30 == 0:  # Update FPS every 30 frames
                current_time = time.time()
                fps = 30 / (current_time - fps_counter)
                fps_counter = current_time
                print(f"FPS: {fps:.1f}, Detections: {len(detections)}")
            else:
                print("Detections:", len(detections))

            # Display frame
            cv2.imshow('Real-time YOLO Detection', annotated_frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\nStopping inference...")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()

def run_picamera2_inference():
    """Alternative implementation using picamera2 library (recommended for Pi)."""
    try:
        from picamera2 import Picamera2
    except ImportError:
        print("picamera2 not installed. Install with: pip install picamera2")
        return
    
    # Initialize YOLO system
    yolo_system = RealTimeYOLO()
    
    # Initialize picamera2
    picam2 = Picamera2()
    
    # Configure camera
    config = picam2.create_preview_configuration(
        main={"size": (640, 480), "format": "RGB888"}
    )
    picam2.configure(config)
    picam2.start()
    
    print("Starting real-time inference with picamera2. Press 'q' to quit.")
    
    frame_count = 0
    fps_counter = time.time()
    
    try:
        while True:
            # Capture frame
            frame = picam2.capture_array()
            
            # Convert RGB to BGR for OpenCV
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Process frame
            annotated_frame, detections = yolo_system.process_frame(frame_bgr)
            
            # Add FPS counter
            frame_count += 1
            if frame_count % 30 == 0:
                current_time = time.time()
                fps = 30 / (current_time - fps_counter)
                fps_counter = current_time
                print(f"FPS: {fps:.1f}, Detections: {len(detections)}")
            else:
                print("Detections:", len(detections))
            
            # Display frame
            cv2.imshow('Real-time YOLO Detection', annotated_frame)
            
            # Check for quit
            if cv2.waitKey(yolo_system.detection_interval * 1000) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\nStopping inference...")
    
    finally:
        picam2.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Real-time YOLO inference with Pi Camera")
    parser.add_argument("--camera", choices=["opencv", "picamera2"], default="picamera2",
                       help="Camera interface to use (default: picamera2)")
    parser.add_argument("--conf", type=float, default=0.5,
                       help="Confidence threshold for detections (default: 0.5)")
    parser.add_argument("--model", default="src/yolo11n_ncnn_model",
                       help="Path to YOLO model (default: src/yolo11n_ncnn_model)")
    
    args = parser.parse_args()
    
    print(f"Using {args.camera} camera interface")
    print(f"Confidence threshold: {args.conf}")
    print(f"Model: {args.model}")
    
    if args.camera == "picamera2":
        run_picamera2_inference()
    else:
        run_pi_camera_inference()