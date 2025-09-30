import cv2
import os
from moviepy.editor import VideoFileClip
import numpy as np
from PIL import Image
import json

class VideoAnalyzer:
    def __init__(self, video_path):
        self.video_path = video_path
        self.video_info = {}
        
    def analyze_video(self):
        """Analyze video and extract key information"""
        try:
            # Get basic video info using moviepy
            with VideoFileClip(self.video_path) as clip:
                self.video_info = {
                    'duration': clip.duration,
                    'fps': clip.fps,
                    'resolution': (clip.w, clip.h),
                    'has_audio': clip.audio is not None
                }
            
            # Extract frames for analysis
            self.video_info['key_frames'] = self._extract_key_frames()
            self.video_info['colors'] = self._analyze_colors()
            self.video_info['brightness'] = self._analyze_brightness()
            self.video_info['motion'] = self._analyze_motion()
            
            return self.video_info
            
        except Exception as e:
            print(f"Error analyzing video: {e}")
            return None
    
    def _extract_key_frames(self, num_frames=5):
        """Extract key frames from video"""
        cap = cv2.VideoCapture(self.video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calculate frame positions to extract
        positions = np.linspace(0, total_frames-1, num_frames, dtype=int)
        frames = []
        
        for pos in positions:
            cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
            ret, frame = cap.read()
            if ret:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame_rgb)
        
        cap.release()
        return frames
    
    def _analyze_colors(self):
        """Analyze dominant colors in the video"""
        if not self.video_info.get('key_frames'):
            return []
        
        dominant_colors = []
        for frame in self.video_info['key_frames']:
            # Reshape frame for color analysis
            pixels = frame.reshape(-1, 3)
            
            # Simple dominant color detection (you can enhance this)
            unique_colors = np.unique(pixels, axis=0)
            if len(unique_colors) > 0:
                # Get the most common color (simplified)
                mean_color = np.mean(pixels, axis=0).astype(int)
                dominant_colors.append(mean_color.tolist())
        
        return dominant_colors
    
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
    
    def _analyze_motion(self):
        """Analyze motion in video (simplified)"""
        cap = cv2.VideoCapture(self.video_path)
        
        ret, frame1 = cap.read()
        if not ret:
            cap.release()
            return 0
        
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        motion_scores = []
        
        # Sample a few frames to analyze motion
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        sample_frames = min(10, total_frames // 10)
        
        for i in range(sample_frames):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i * (total_frames // sample_frames))
            ret, frame2 = cap.read()
            if not ret:
                break
                
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            
            # Calculate frame difference
            diff = cv2.absdiff(gray1, gray2)
            motion_score = np.mean(diff)
            motion_scores.append(motion_score)
            
            gray1 = gray2
        
        cap.release()
        return np.mean(motion_scores) if motion_scores else 0
    
    def get_best_thumbnail_frame(self):
        """Get the best frame for thumbnail"""
        if not self.video_info.get('key_frames'):
            self.analyze_video()
        
        frames = self.video_info.get('key_frames', [])
        if not frames:
            return None
        
        # Simple heuristic: choose frame with good brightness and contrast
        best_frame = None
        best_score = 0
        
        for frame in frames:
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            
            # Calculate score based on brightness and contrast
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
        
        duration_desc = f"{int(info.get('duration', 0) // 60)}:{int(info.get('duration', 0) % 60):02d}" if info.get('duration') else "unknown"
        resolution_desc = f"{info.get('resolution', ['unknown', 'unknown'])[0]}x{info.get('resolution', ['unknown', 'unknown'])[1]}"
        
        # Brightness description
        brightness = info.get('brightness', 0)
        if brightness < 85:
            brightness_desc = "dark/moody"
        elif brightness > 170:
            brightness_desc = "bright/vibrant"
        else:
            brightness_desc = "well-lit"
        
        # Motion description
        motion = info.get('motion', 0)
        if motion < 10:
            motion_desc = "static/slow-paced"
        elif motion > 30:
            motion_desc = "dynamic/fast-paced"
        else:
            motion_desc = "moderate movement"
        
        prompt = f"""Video Analysis:
- Duration: {duration_desc}
- Resolution: {resolution_desc}
- Visual style: {brightness_desc}
- Pacing: {motion_desc}
- Has audio: {info.get('has_audio', False)}"""
        
        return prompt