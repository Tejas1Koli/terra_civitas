"""
CCTV-Optimized Crime Detection System
Tuned for top-down/angled CCTV footage with improved accuracy
"""

import os
import cv2
import numpy as np
from collections import deque, defaultdict
import time
from typing import Tuple, List, Dict, Optional
import onnxruntime as rt


class CCTVCrimeDetector:
    """Optimized detector specifically for CCTV surveillance footage."""
    
    def __init__(self, gun_model_path: str = "normal.onnx", use_gpu: bool = True):
        """Initialize CCTV-optimized detector."""
        
        # ONNX model for gun detection
        providers = []
        if use_gpu:
            if 'CoreMLExecutionProvider' in rt.get_available_providers():
                providers.append('CoreMLExecutionProvider')
            elif 'CUDAExecutionProvider' in rt.get_available_providers():
                providers.append('CUDAExecutionProvider')
        providers.append('CPUExecutionProvider')
        
        try:
            self.session = rt.InferenceSession(gun_model_path, providers=providers)
            self.device = "GPU (Metal)" if 'CoreMLExecutionProvider' in providers else \
                         "GPU (CUDA)" if 'CUDAExecutionProvider' in providers else "CPU"
        except Exception as e:
            print(f"⚠️ ONNX model failed: {e}")
            self.session = None
            self.device = "CPU"
        
        self.input_name = self.session.get_inputs()[0].name if self.session else None
        self.output_name = self.session.get_outputs()[0].name if self.session else None
        
        # CCTV-specific settings
        self.cctv_gun_confidence = 0.35  # More sensitive for CCTV
        self.cctv_weapon_size_min = 15   # Lower min size
        self.cctv_weapon_size_max = 600  # Higher max
        
        # Motion-based threat detection (for CCTV)
        self.prev_frame = None
        self.motion_history = deque(maxlen=30)
        self.high_motion_regions = []
        
        # Person-like region tracking
        self.person_regions = defaultdict(lambda: deque(maxlen=10))
        self.region_violence_score = defaultdict(float)
        
        # Statistics
        self.frame_count = 0
        self.threat_history = deque(maxlen=100)
        self.inference_time = 0.0
        
        print(f"✅ CCTV Crime Detector initialized on {self.device}")
    
    def preprocess_for_cctv(self, frame: np.ndarray) -> Tuple[np.ndarray, float]:
        """Preprocess frame specifically for CCTV."""
        h, w = frame.shape[:2]
        
        # For CCTV: maintain aspect ratio
        scale = min(640 / w, 640 / h)
        new_w, new_h = int(w * scale), int(h * scale)
        
        resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        # Letter-box to 640x640
        canvas = np.full((640, 640, 3), 114, dtype=np.uint8)
        y_off = (640 - new_h) // 2
        x_off = (640 - new_w) // 2
        canvas[y_off:y_off+new_h, x_off:x_off+new_w] = resized
        
        # Normalize
        processed = canvas.astype(np.float32) / 255.0
        processed = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
        processed = np.transpose(processed, (2, 0, 1))
        processed = np.expand_dims(processed, 0)
        
        return processed, scale
    
    def detect_weapons_cctv(self, frame: np.ndarray) -> List[Dict]:
        """Detect weapons in CCTV footage."""
        if self.session is None:
            return []
        
        start = time.time()
        processed, scale = self.preprocess_for_cctv(frame)
        
        try:
            outputs = self.session.run([self.output_name], {self.input_name: processed})
            self.inference_time = (time.time() - start) * 1000
        except:
            return []
        
        # Parse outputs [1, 6, 8400]
        output = outputs[0].squeeze(0).transpose(1, 0)
        
        x_center = output[:, 0]
        y_center = output[:, 1]
        widths = output[:, 2]
        heights = output[:, 3]
        conf = output[:, 4]
        
        # Sigmoid normalize
        conf = np.where(conf > 1.0, 1.0 / (1.0 + np.exp(-conf)), conf)
        
        # CCTV threshold: more lenient
        mask = conf >= self.cctv_gun_confidence
        if not np.any(mask):
            return []
        
        detections = []
        h, w = frame.shape[:2]
        
        for i in np.where(mask)[0]:
            x1 = int((x_center[i] - widths[i]/2) / scale)
            y1 = int((y_center[i] - heights[i]/2) / scale)
            x2 = int((x_center[i] + widths[i]/2) / scale)
            y2 = int((y_center[i] + heights[i]/2) / scale)
            
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            
            box_w = x2 - x1
            box_h = y2 - y1
            
            # CCTV-specific filtering
            if box_w < self.cctv_weapon_size_min or box_h < self.cctv_weapon_size_min:
                continue
            if box_w > self.cctv_weapon_size_max or box_h > self.cctv_weapon_size_max:
                continue
            
            aspect = box_w / (box_h + 1e-6)
            if aspect < 0.2 or aspect > 5.0:  # Wider tolerance for CCTV angles
                continue
            
            detections.append({
                'box': (x1, y1, x2, y2),
                'confidence': float(conf[i]),
                'class': 'weapon'
            })
        
        return detections
    
    def detect_motion_threats(self, frame: np.ndarray) -> Tuple[float, List[Dict]]:
        """Detect motion-based threats using optical flow (CCTV-optimized)."""
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_gray = cv2.GaussianBlur(frame_gray, (5, 5), 0)
        
        motion_score = 0.0
        motion_regions = []
        
        if self.prev_frame is not None and self.prev_frame.shape == frame_gray.shape:
            # Optical flow - only calculate if frames have same dimensions
            flow = cv2.calcOpticalFlowFarneback(
                self.prev_frame, frame_gray, None,
                0.5, 3, 15, 3, 5, 1.2, 0
            )
            
            mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            
            # CCTV: large motion = threat (more sensitive)
            high_motion = mag > 15  # More sensitive (was 30)
            motion_area = np.sum(high_motion)
            
            if motion_area > 500:  # More sensitive (was 1000)
                motion_score = min(1.0, motion_area / 50000.0)
                
                # Find motion regions
                contours, _ = cv2.findContours(
                    high_motion.astype(np.uint8),
                    cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                )
                
                for cnt in contours:
                    area = cv2.contourArea(cnt)
                    if area > 500:
                        m = cv2.moments(cnt)
                        if m['m00'] > 0:
                            cx, cy = int(m['m10']/m['m00']), int(m['m01']/m['m00'])
                            motion_regions.append({
                                'center': (cx, cy),
                                'area': area,
                                'threat_level': min(1.0, area / 10000.0)
                            })
        
        self.prev_frame = frame_gray.copy()
        self.motion_history.append(motion_score)
        self.high_motion_regions = motion_regions
        
        return motion_score, motion_regions
    
    def detect_person_clustering(self, frame: np.ndarray) -> Tuple[float, List[Dict]]:
        """Detect suspicious person clustering (crowding = potential crime in CCTV)."""
        
        # Simple background subtraction to find moving objects
        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Detect motion blobs
        blurred = cv2.GaussianBlur(frame_hsv, (7, 7), 0)
        
        # Use Canny edge detection for CCTV
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Dilate to find connected regions
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        dilated = cv2.dilate(edges, kernel, iterations=2)
        
        # Find contours (person-like regions)
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        regions = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if 500 < area < 20000:  # Person-like size
                m = cv2.moments(cnt)
                if m['m00'] > 0:
                    cx, cy = int(m['m10']/m['m00']), int(m['m01']/m['m00'])
                    regions.append((cx, cy, area))
        
        # Check for clustering (multiple people close together)
        cluster_threat = 0.0
        clustering_events = []
        
        if len(regions) > 2:
            # Calculate pairwise distances
            cluster_count = 0
            for i, (x1, y1, a1) in enumerate(regions):
                neighbors = 0
                for j, (x2, y2, a2) in enumerate(regions):
                    if i != j:
                        dist = np.sqrt((x1-x2)**2 + (y1-y2)**2)
                        if dist < 100:  # Close proximity
                            neighbors += 1
                
                if neighbors >= 2:
                    cluster_count += 1
                    clustering_events.append({
                        'center': (x1, y1),
                        'people_nearby': neighbors,
                        'threat_level': min(1.0, neighbors / 5.0)
                    })
            
            cluster_threat = min(1.0, cluster_count / 10.0)
        
        return cluster_threat, clustering_events
    
    def detect_frame(self, frame: np.ndarray) -> Dict:
        """Detect crimes in CCTV frame."""
        self.frame_count += 1
        h, w = frame.shape[:2]
        
        # Get threat scores
        weapons = self.detect_weapons_cctv(frame)
        motion_score, motion_regions = self.detect_motion_threats(frame)
        cluster_score, clustering = self.detect_person_clustering(frame)
        
        # CCTV Crime scoring (adjusted for surveillance)
        # High motion + clustering + weapons = crime
        crime_score = 0.0
        
        # Weapons are very strong indicator
        if weapons:
            crime_score += 0.7 * len(weapons) * np.mean([w['confidence'] for w in weapons])
        
        # Unusual motion patterns
        if motion_score > 0.5:
            crime_score += 0.2 * motion_score
        
        # Person clustering with motion = potential threat
        if cluster_score > 0.3 and motion_score > 0.3:
            crime_score += 0.1 * cluster_score
        
        crime_score = min(1.0, crime_score)
        self.threat_history.append(crime_score)
        
        # Temporal smoothing for CCTV (use last 10 frames)
        if len(self.threat_history) >= 10:
            smoothed_score = np.mean(list(self.threat_history)[-10:])
        else:
            smoothed_score = crime_score
        
        # CCTV Classification: stricter thresholds
        is_crime = smoothed_score >= 0.35  # More sensitive (was 0.4)
        confidence = min(1.0, smoothed_score) if is_crime else min(1.0, 1.0 - smoothed_score)
        
        return {
            'frame_num': self.frame_count,
            'weapons': weapons,
            'motion_score': float(motion_score),
            'cluster_score': float(cluster_score),
            'crime_score': float(crime_score),
            'smoothed_score': float(smoothed_score),
            'is_crime': is_crime,
            'confidence': float(confidence),
            'motion_regions': motion_regions,
            'clustering_events': clustering
        }
    
    def annotate_frame(self, frame: np.ndarray, results: Dict) -> np.ndarray:
        """Annotate frame with detections."""
        h, w = frame.shape[:2]
        
        # Draw weapons
        for weapon in results['weapons']:
            x1, y1, x2, y2 = weapon['box']
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            label = f"WEAPON {weapon['confidence']:.0%}"
            cv2.putText(frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.6, (0, 0, 255), 2)
        
        # Draw motion regions
        for region in results['motion_regions']:
            cx, cy = region['center']
            threat = region['threat_level']
            color = (0, int(255 * threat), 255)
            cv2.circle(frame, (cx, cy), 20, color, 2)
        
        # Draw clustering
        for cluster in results['clustering_events']:
            cx, cy = cluster['center']
            threat = cluster['threat_level']
            color = (0, int(200 * threat), 255)
            cv2.circle(frame, (cx, cy), 15, color, 2)
            cv2.putText(frame, f"G{cluster['people_nearby']}", (cx-10, cy-20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        # Draw crime status (large overlay)
        overlay = frame.copy()
        status = "🚨 CRIME" if results['is_crime'] else "✓ NORMAL"
        color = (0, 0, 255) if results['is_crime'] else (0, 255, 0)
        
        cv2.rectangle(overlay, (0, 0), (w, 100), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
        
        cv2.putText(frame, status, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                   1.2, color, 3)
        cv2.putText(frame, f"Score: {results['smoothed_score']:.2f}", 
                   (20, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Stats
        cv2.putText(frame, f"Frame: {results['frame_num']}", (w-200, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        cv2.putText(frame, f"Weapons: {len(results['weapons'])}", (w-200, 65),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        cv2.putText(frame, f"Motion: {results['motion_score']:.2f}", (w-200, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        return frame
    
    def get_stats(self) -> Dict:
        """Get detector statistics."""
        avg_threat = float(np.mean(self.threat_history)) if self.threat_history else 0.0
        
        return {
            'total_frames': self.frame_count,
            'average_threat_score': avg_threat,
            'device': self.device,
            'inference_time_ms': self.inference_time,
            'motion_regions': len(self.high_motion_regions)
        }
