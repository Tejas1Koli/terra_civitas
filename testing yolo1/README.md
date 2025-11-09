# 🔍 Real-time Weapon Detection Pipeline

A machine learning pipeline that performs real-time weapon detection in live video streams using ONNX model inference and a Streamlit web interface.

## Features

✅ **Real-time Detection**: Process live video from webcam or uploaded files
✅ **ONNX Model**: Fast inference using ONNX Runtime
✅ **Web Interface**: User-friendly Streamlit frontend
✅ **Confidence Control**: Adjustable detection confidence threshold
✅ **Detailed Metrics**: Frame count, detection count, FPS tracking
✅ **Visual Feedback**: Bounding boxes with confidence scores

## Project Structure

```
.
├── main.py                  # Main entry point with documentation
├── app.py                   # Streamlit web application
├── weapon_detector.py       # ONNX model inference wrapper
├── requirements.txt         # Python dependencies
├── normal.onnx             # Weapon detection ONNX model
└── README.md               # This file
```

## Installation

### 1. Navigate to Project Directory
```bash
cd "/Users/tejaskoli/testing yolo1"
```

### 2. Activate Virtual Environment (if needed)
```bash
source yolo/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Usage

### Start the Application
```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

### Using the Interface

1. **Load Model**
   - The default model path is pre-filled
   - Click "Load Model" button in the sidebar
   - Wait for the model to load

2. **Select Video Source**
   - **Webcam**: Uses your system's default camera
   - **Upload Video File**: Upload MP4, AVI, MOV, MKV, FLV, or WMV files

3. **Adjust Settings**
   - Use the confidence threshold slider to control detection sensitivity
   - Lower threshold = more detections (higher false positives)
   - Higher threshold = fewer detections (higher confidence)

4. **Start Detection**
   - Click "Start Detection" button
   - Video will stream with real-time detection

5. **Monitor Statistics**
   - **Frame Count**: Total frames processed
   - **Detections in Frame**: Weapons found in current frame
   - **Total Detections**: Cumulative detection count
   - **FPS**: Frames per second

## Technical Details

### WeaponDetector Class

Located in `weapon_detector.py`, this class handles:

- **Model Loading**: Initializes ONNX Runtime session
- **Image Preprocessing**: Resizing, normalization, format conversion
- **Inference**: Runs model predictions
- **Post-processing**: Extracts bounding boxes and confidence scores
- **Visualization**: Draws detection boxes on frames

### Key Methods

```python
detector = WeaponDetector("normal.onnx")

# Detect weapons in image
detections = detector.detect(frame)

# Draw boxes on image
annotated = detector.draw_detections(frame, detections)

# Adjust threshold
detector.set_confidence_threshold(0.6)
```

### Detection Output Format

```python
{
    'boxes': [[x1, y1, x2, y2], ...],      # Bounding box coordinates
    'scores': [0.95, 0.87, ...],           # Confidence scores
    'class_ids': [0, 0, ...],              # Class indices
    'class_names': ['Weapon']              # Class names
}
```

## Configuration

### Model Path
Default: `/Users/tejaskoli/testing yolo1/normal.onnx`

Edit in sidebar or modify `app.py` to use different model.

### Confidence Threshold
- **Range**: 0.0 to 1.0
- **Default**: 0.5
- **Use**: Filter detections by confidence score

### Video Input Size
- **Model Input**: 640x640 pixels
- **Display Size**: 640x480 pixels (adjustable in code)

## Requirements

- Python 3.8+
- streamlit >= 1.28.0
- opencv-python >= 4.8.0
- numpy >= 1.24.0
- onnxruntime >= 1.16.0
- Pillow >= 10.0.0

## Troubleshooting

### Model Failed to Load
- Verify `normal.onnx` exists in the workspace
- Check file permissions
- Ensure ONNX Runtime is properly installed

### Webcam Not Working
- Check camera permissions in system settings
- Verify camera is not in use by another application
- Try index 1 if available instead of 0

### Slow Performance
- Reduce display size in code
- Increase confidence threshold
- Check CPU/GPU usage
- Use GPU-accelerated ONNX Runtime if available

### Video File Issues
- Ensure video codec is supported
- Try converting to MP4 with H.264 codec
- Check file path for special characters

## Performance Tips

1. **Optimize Confidence Threshold**: Higher threshold = faster processing
2. **Use GPU**: Install `onnxruntime-gpu` for faster inference
3. **Adjust Input Size**: Modify `model_width` and `model_height` in `weapon_detector.py`
4. **Frame Skipping**: Add frame skipping logic for real-time streams

## Model Information

**Model**: normal.onnx
- **Type**: YOLO-based object detection
- **Input**: RGB images (640x640)
- **Output**: Bounding boxes with confidence scores
- **Classes**: Weapon detection

## Future Enhancements

- [ ] Multi-class weapon detection
- [ ] GPU acceleration
- [ ] Video recording with annotations
- [ ] Detection history/analytics
- [ ] REST API endpoint
- [ ] Alert notifications
- [ ] Batch processing
- [ ] Custom model upload

## License

This project uses the provided ONNX model (normal.onnx). Ensure you have proper licensing for model usage.

## Support

For issues or questions, check:
1. Model path configuration
2. ONNX Runtime installation
3. Camera permissions
4. Video file format compatibility

## Author

Created with ❤️ for real-time weapon detection
