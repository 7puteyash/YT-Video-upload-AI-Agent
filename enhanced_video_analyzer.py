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
        """Analyze video and extract comprehensive information"""
        try:
            cap = cv2.VideoCapture(self.video_path)
            
            if not cap.isOpened():
                print(f"Error: Could not open video file {self.video_path}")
                return None
            
            # Get basic video properties
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
                'file_size': os.path.getsize(self.video_path) if os.path.exists(self.video_path) else 0
            }
            
            # Enhanced analysis
            self.video_info.update(self._analyze_content_deeply(cap))
            
            cap.release()
            return self.video_info
            
        except Exception as e:
            print(f"Error analyzing video: {e}")
            return None
    
    def _analyze_content_deeply(self, cap):
        """Perform deep content analysis"""
        analysis = {
            'scene_changes': 0,
            'motion_level': 'static',
            'brightness_levels': [],
            'color_variety': 'low',
            'visual_complexity': 'simple',
            'content_type': 'unknown',
            'dominant_colors': [],
            'key_frames': [],
            'text_presence': False
        }
        
        try:
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_frames = min(20, max(5, total_frames // 50))  # Sample more frames
            
            previous_frame = None
            brightness_values = []
            motion_scores = []
            color_histograms = []
            key_frames = []
            
            for i in range(sample_frames):
                frame_pos = i * (total_frames // sample_frames)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                ret, frame = cap.read()
                
                if not ret:
                    continue
                
                # Analyze brightness
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                brightness = np.mean(gray)
                brightness_values.append(brightness)
                
                # Analyze motion
                if previous_frame is not None:
                    diff = cv2.absdiff(previous_frame, gray)
                    motion_score = np.mean(diff)
                    motion_scores.append(motion_score)
                    
                    if motion_score > 10:  # Significant change
                        analysis['scene_changes'] += 1
                
                # Analyze colors
                color_hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                color_histograms.append(color_hist.flatten())
                
                # Store key frame for thumbnail
                if len(key_frames) < 5:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    key_frames.append(frame_rgb)
                
                # Check for text (simplified)
                edges = cv2.Canny(gray, 50, 150)
                if np.sum(edges) > gray.shape[0] * gray.shape[1] * 10:  # Many edges might indicate text
                    analysis['text_presence'] = True
                
                previous_frame = gray
            
            # Process analysis results
            if brightness_values:
                avg_brightness = np.mean(brightness_values)
                analysis['brightness_levels'] = {
                    'average': float(avg_brightness),
                    'variation': float(np.std(brightness_values)),
                    'description': self._describe_brightness(avg_brightness)
                }
            
            if motion_scores:
                avg_motion = np.mean(motion_scores)
                analysis['motion_level'] = self._describe_motion(avg_motion)
                analysis['average_motion_score'] = float(avg_motion)
            
            # Analyze color variety
            if color_histograms:
                analysis['color_variety'] = self._analyze_color_variety(color_histograms)
                analysis['dominant_colors'] = self._extract_dominant_colors(color_histograms[0])
            
            # Determine content type based on analysis
            analysis['content_type'] = self._determine_content_type(analysis)
            analysis['visual_complexity'] = self._determine_complexity(analysis)
            analysis['key_frames'] = key_frames
            
        except Exception as e:
            print(f"Error in deep analysis: {e}")
        
        return analysis
    
    def _describe_brightness(self, brightness):
        """Describe brightness level"""
        if brightness < 80:
            return "dark/low-light"
        elif brightness > 180:
            return "bright/high-key"
        else:
            return "well-balanced"
    
    def _describe_motion(self, motion_score):
        """Describe motion level"""
        if motion_score < 5:
            return "minimal/static"
        elif motion_score < 15:
            return "moderate"
        elif motion_score < 30:
            return "active/dynamic"
        else:
            return "high-motion/fast-paced"
    
    def _analyze_color_variety(self, color_histograms):
        """Analyze color variety in video"""
        if not color_histograms:
            return "unknown"
        
        # Calculate color variance
        hist_array = np.array(color_histograms[0])
        non_zero_bins = np.count_nonzero(hist_array)
        total_bins = len(hist_array)
        
        variety_ratio = non_zero_bins / total_bins
        
        if variety_ratio < 0.1:
            return "monochromatic"
        elif variety_ratio < 0.3:
            return "limited palette"
        elif variety_ratio < 0.6:
            return "moderate variety"
        else:
            return "rich/diverse colors"
    
    def _extract_dominant_colors(self, color_hist):
        """Extract dominant colors from histogram"""
        # Simplified dominant color extraction
        dominant_indices = np.argsort(color_hist)[-3:]  # Top 3
        colors = []
        
        for idx in dominant_indices:
            # Convert back to RGB (simplified)
            r = (idx // 64) * 32
            g = ((idx % 64) // 8) * 32
            b = (idx % 8) * 32
            colors.append([r, g, b])
        
        return colors
    
    def _determine_content_type(self, analysis):
        """Determine likely content type based on analysis"""
        motion = analysis.get('average_motion_score', 0)
        scene_changes = analysis.get('scene_changes', 0)
        text_presence = analysis.get('text_presence', False)
        
        if text_presence and motion < 10:
            return "tutorial/presentation"
        elif scene_changes > 5 and motion > 20:
            return "dynamic/entertainment"
        elif motion < 5:
            return "talking-head/interview"
        elif scene_changes > 3:
            return "documentary/narrative"
        else:
            return "general content"
    
    def _determine_complexity(self, analysis):
        """Determine visual complexity"""
        color_variety = analysis.get('color_variety', 'low')
        motion = analysis.get('average_motion_score', 0)
        scene_changes = analysis.get('scene_changes', 0)
        
        complexity_score = 0
        if color_variety in ['rich/diverse colors', 'moderate variety']:
            complexity_score += 2
        if motion > 15:
            complexity_score += 2
        if scene_changes > 3:
            complexity_score += 2
        
        if complexity_score >= 4:
            return "high complexity"
        elif complexity_score >= 2:
            return "moderate complexity"
        else:
            return "simple/clean"
    
    def get_best_thumbnail_frame(self):
        """Get the best frame for thumbnail"""
        key_frames = self.video_info.get('key_frames', [])
        if not key_frames:
            return None
        
        # Choose middle frame as a safe bet, or analyze for best contrast
        middle_idx = len(key_frames) // 2
        return key_frames[middle_idx]
    
    def generate_description_prompt(self):
        """Generate a comprehensive prompt for AI based on video analysis"""
        info = self.video_info
        
        duration_str = f"{int(info.get('duration', 0) // 60)}:{int(info.get('duration', 0) % 60):02d}"
        
        prompt = f"""Detailed Video Content Analysis:

TECHNICAL SPECS:
- Duration: {duration_str} minutes
- Resolution: {info.get('resolution', 'unknown')}
- Frame rate: {info.get('fps', 'unknown')} fps

VISUAL CHARACTERISTICS:
- Lighting: {info.get('brightness_levels', {}).get('description', 'unknown')}
- Motion level: {info.get('motion_level', 'unknown')}
- Color palette: {info.get('color_variety', 'unknown')}
- Visual complexity: {info.get('visual_complexity', 'unknown')}
- Scene changes: {info.get('scene_changes', 0)} detected

CONTENT ANALYSIS:
- Likely content type: {info.get('content_type', 'unknown')}
- Text/graphics present: {'Yes' if info.get('text_presence') else 'No'}
- Pacing: {info.get('motion_level', 'unknown')}

This analysis suggests the video is a {info.get('content_type', 'general content')} with {info.get('visual_complexity', 'unknown')} visual style and {info.get('motion_level', 'unknown')} pacing."""
        
        return prompt