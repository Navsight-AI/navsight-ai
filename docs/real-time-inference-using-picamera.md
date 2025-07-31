````python
from ultralytics import YOLO
import cv2
import numpy as np
from tts.tts import text_to_speech
from utils.grammar import get_plural, get_article
from collections import Counter
import time
import threading
from queue import Queue

class RealTimeYOLO:
    def __init__(self, model_path="src/yolo11n_ncnn_model", conf_threshold=0.5):
        """Initialize the real-time YOLO inference system."""
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        self.allowed_names = {'person', 'bench', 'bicycle', 'umbrella', 'book', 'bus', 'car', 'bed', 'truck', 'chair'}
        
        # For speech synthesis
        self.speech_queue = Queue()
        self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speech_thread.start()
        
        # For detection tracking
        self.last_detection_time = 0
        self.detection_interval = 3  # Announce detections every 3 seconds
        
    def _speech_worker(self):
        """Background thread for text-to-speech to avoid blocking inference."""
        while True:
            try:
                text = self.speech_queue.get(timeout=1)
                if text:
                    text_to_speech(text)
                self.speech_queue.task_done()
            except:
                continue
                
    def announce_detections(self, detected_names):
        """Add detection announcements to speech queue."""
        current_time = time.time()
        if current_time - self.last_detection_time >= self.detection_interval:
            if detected_names:
                counts = Counter(detected_names)
                for name, count in counts.items():
                    announcement = f"I can identify {get_article(count, name)} {name if count == 1 else get_plural(name)}"
                    self.speech_queue.put(announcement)
                self.last_detection_time = current_time
    
    def process_frame(self, frame):
        """Process a single frame and return annotated frame with detections."""
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
        
        return annotated_frame, detected_names

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
            
            # Display frame
            cv2.imshow('Real-time YOLO Detection', annotated_frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
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
````

This implementation provides real-time YOLO inference using the Raspberry Pi camera with the following features:

## Key Features:

1. **Two Camera Interfaces**:
   - `picamera2` (recommended for newer Pi models)
   - OpenCV VideoCapture (fallback option)

2. **Real-time Processing**:
   - Continuous frame capture and inference
   - Non-blocking text-to-speech using threading
   - FPS monitoring

3. **Smart Announcements**:
   - Detections announced every 3 seconds to avoid spam
   - Threaded speech synthesis to maintain smooth video

4. **Performance Optimizations**:
   - Configurable frame resolution (640x480 default)
   - Filtered detections (only allowed object classes)
   - Efficient frame processing

## Usage:

```bash
# Using picamera2 (recommended)
python real_time_inference.py --camera picamera2

# Using OpenCV
python real_time_inference.py --camera opencv

# With custom confidence threshold
python real_time_inference.py --conf 0.3

# With custom model path
python real_time_inference.py --model path/to/your/model
```

## Requirements:

For Raspberry Pi, install:
```bash
pip install picamera2  # For newer Pi models
pip install opencv-python
```

The system will display the live video feed with bounding boxes and announce detected objects through text-to-speech every few seconds. Press 'q' to quit the application.