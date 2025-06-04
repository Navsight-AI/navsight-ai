# Object Detection Project

This project implements an object detection system using computer vision techniques. It is designed to detect and visualize objects in images using a pre-trained model. Code will run on a Raspberry Pi after development and will be assembled with other hardware components to form a unit.

Key ideas:
1. Object Detection
2. Audio Feedback
3. Navigation Guide

## Project Structure

```
navsight-ai
├── src
│   ├── main.py                # Entry point of the application
│   ├── models
│   │   └── detector.py        # Contains the ObjectDetector class
│   ├── utils
│   │   └── image_utils.py     # Utility functions for image processing
│   └── data
│       └── __init__.py        # Marks the data directory as a package
├── requirements.txt           # Lists project dependencies
├── README.md                  # Project documentation
└── .gitignore                 # Specifies files to ignore in Git
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone https://github.com/wodoame/navsight-ai.git
   cd navsight-ai
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
