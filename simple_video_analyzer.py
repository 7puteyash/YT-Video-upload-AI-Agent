import cv2
import os
import numpy as np
from PIL import Image
import json

class SimpleVideoAnalyzer:
    def __init__(self, video_path):
        self.video_path = video_path
        self.video_info = {}
        
    def analyze_video(self):
        """Analyze video using OpenCV (simpler than moviepy)"""
        try:
            cap = cv2.VideoCapture(self.video_path)
            
            # Get basic video info
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            self.video_info = {
                'duration': duration,
                'fps': fps,
                'resolution': (width, height),
                'frame_count': frame_count,
                'has_audio': True  # Assume audio exists
            }
            
            # Extract frames for analysis
            self.video_info['key_frames'] = self._extract_key_frames(cap)
            self.video_info['brightness'] = self._analyze_brightness()
            
            cap.release()
            return self.video_info
            
        except Exception as e:
            print(f"Error analyzing video: {e}")
            return None
    
    def _extract_key_frames(self, cap, num_frames=5):
        """Extract key frames from video"""
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        positions = np.linspace(0, frame_count-1, num_frames, dtype=int)
        frames = []
        
        for pos in positions:
            cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
            ret, frame = cap.read()
            if ret:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame_rgb)
        
        return frames
    
    def _analyze_brightness(self):
        """Analyze brightness levels"""
        if not self.video_info.get('key_frames'):
            return 0
        
        brightness_values = []
        for frame in self.video_info['key_frames']:
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            brightness = np.mean(gray)
            brightness_values.append(brightness)
        
        return np.mean(brightness_values) if brightness_values else 0
    
    def get_best_thumbnail_frame(self):
        """Get the best frame for thumbnail"""
        frames = self.video_info.get('key_frames', [])
        if not frames:
            return None
        
        # Simple heuristic: choose frame with good brightness and contrast
        best_frame = None
        best_score = 0
        
        for frame in frames:
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            brightness = np.mean(gray)
            contrast = np.std(gray)
            
            # Prefer frames with moderate brightness and high contrast
            score = contrast * (1 - abs(brightness - 128) / 128)
            
            if score > best_score:
                best_score = score
                best_frame = frame
        
        return best_frame
    
    def generate_description_prompt(self):
        """Generate a descriptive prompt about the video for AI"""
        info = self.video_info
        
        duration_desc = f"{int(info.get('duration', 0) // 60)}:{int(info.get('duration', 0) % 60):02d}"
        resolution_desc = f"{info.get('resolution', (0, 0))[0]}x{info.get('resolution', (0, 0))[1]}"
        
        # Brightness description
        brightness = info.get('brightness', 0)
        if brightness < 85:
            brightness_desc = "dark/moody"
        elif brightness > 170:
            brightness_desc = "bright/vibrant"
        else:
            brightness_desc = "well-lit"
        
        prompt = f"""Video Analysis:
- Duration: {duration_desc}
- Resolution: {resolution_desc}
- Visual style: {brightness_desc}
- Has audio: {info.get('has_audio', False)}"""
        
        return prompt