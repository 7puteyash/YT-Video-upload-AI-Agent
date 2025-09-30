import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os
import requests
from io import BytesIO

class ThumbnailGenerator:
    def __init__(self, width=1280, height=720):
        self.width = width
        self.height = height
        self.aspect_ratio = width / height
        
    def create_thumbnail(self, base_frame, title, concept_description=None):
        """Create an engaging thumbnail from a video frame"""
        
        if base_frame is None:
            return None
            
        try:
            # Convert numpy array to PIL Image
            if isinstance(base_frame, np.ndarray):
                pil_image = Image.fromarray(base_frame)
            else:
                pil_image = base_frame
            
            # Resize and crop to thumbnail dimensions
            thumbnail = self._resize_and_crop(pil_image)
            
            # Enhance the image
            thumbnail = self._enhance_image(thumbnail)
            
            # Add title overlay if provided
            if title:
                thumbnail = self._add_title_overlay(thumbnail, title)
            
            # Add visual effects
            thumbnail = self._add_visual_effects(thumbnail)
            
            return thumbnail
            
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
            return None
    
    def _resize_and_crop(self, image):
        """Resize and crop image to thumbnail dimensions"""
        # Get current dimensions
        current_width, current_height = image.size
        current_ratio = current_width / current_height
        
        if current_ratio > self.aspect_ratio:
            # Image is wider, crop width
            new_height = self.height
            new_width = int(new_height * current_ratio)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Center crop
            left = (new_width - self.width) // 2
            image = image.crop((left, 0, left + self.width, self.height))
        else:
            # Image is taller, crop height
            new_width = self.width
            new_height = int(new_width / current_ratio)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Center crop
            top = (new_height - self.height) // 2
            image = image.crop((0, top, self.width, top + self.height))
        
        return image
    
    def _enhance_image(self, image):
        """Enhance image for better thumbnail visibility"""
        # Increase contrast and saturation for more vibrant thumbnail
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.2)
        
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.1)
        
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.05)
        
        return image
    
    def _add_title_overlay(self, image, title):
        """Add title text overlay to thumbnail"""
        # Create a copy to work with
        overlay_image = image.copy()
        draw = ImageDraw.Draw(overlay_image)
        
        # Try to load a bold font, fallback to default
        font_size = 60
        try:
            # Try to use a bold font if available
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("calibri.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        # Prepare title text (limit length and split lines if needed)
        title = title[:80]  # Limit title length
        words = title.split()
        lines = []
        current_line = ""
        
        # Split title into multiple lines if too long
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] <= self.width - 100:  # Leave margins
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # Limit to 2 lines max
        lines = lines[:2]
        
        # Position text in bottom third of image
        line_height = font_size + 10
        total_height = len(lines) * line_height
        start_y = self.height - total_height - 80
        
        # Add semi-transparent background for text
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2]
            x = (self.width - text_width) // 2
            y = start_y + (i * line_height)
            
            # Create background rectangle
            padding = 20
            rect_coords = [
                x - padding,
                y - padding//2,
                x + text_width + padding,
                y + line_height + padding//2
            ]
            
            # Draw semi-transparent background
            rect_overlay = Image.new('RGBA', overlay_image.size, (0, 0, 0, 0))
            rect_draw = ImageDraw.Draw(rect_overlay)
            rect_draw.rectangle(rect_coords, fill=(0, 0, 0, 120))
            overlay_image = Image.alpha_composite(overlay_image.convert('RGBA'), rect_overlay).convert('RGB')
            
            # Redraw on the updated image
            draw = ImageDraw.Draw(overlay_image)
            
            # Draw text outline (for better visibility)
            outline_width = 2
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0, 255))
            
            # Draw main text
            draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
        
        return overlay_image
    
    def _add_visual_effects(self, image):
        """Add subtle visual effects to make thumbnail more engaging"""
        # Add a subtle vignette effect
        vignette = self._create_vignette_mask()
        
        # Convert to RGBA for blending
        image_rgba = image.convert('RGBA')
        vignette_rgba = vignette.convert('RGBA')
        
        # Blend with vignette
        blended = Image.alpha_composite(image_rgba, vignette_rgba)
        
        return blended.convert('RGB')
    
    def _create_vignette_mask(self):
        """Create a vignette mask for subtle darkening at edges"""
        # Create radial gradient
        mask = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(mask)
        
        # Calculate center and maximum distance
        center_x, center_y = self.width // 2, self.height // 2
        max_distance = min(self.width, self.height) // 2
        
        # Create gradient circles
        for i in range(max_distance):
            alpha = int(30 * (i / max_distance))  # Subtle effect
            draw.ellipse([
                center_x - max_distance + i,
                center_y - max_distance + i,
                center_x + max_distance - i,
                center_y + max_distance - i
            ], fill=(0, 0, 0, alpha))
        
        return mask
    
    def save_thumbnail(self, thumbnail, filename):
        """Save thumbnail to file"""
        try:
            thumbnail.save(filename, 'JPEG', quality=95)
            return True
        except Exception as e:
            print(f"Error saving thumbnail: {e}")
            return False
    
    def create_text_thumbnail(self, title, background_color=(41, 128, 185), text_color=(255, 255, 255)):
        """Create a text-only thumbnail as fallback"""
        # Create background
        image = Image.new('RGB', (self.width, self.height), background_color)
        draw = ImageDraw.Draw(image)
        
        # Add gradient background
        for y in range(self.height):
            gradient_color = tuple(
                int(background_color[i] + (50 * y / self.height))
                for i in range(3)
            )
            draw.line([(0, y), (self.width, y)], fill=gradient_color)
        
        # Add title
        font_size = 80
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Word wrap the title
        words = title.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] <= self.width - 100:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # Position and draw text
        line_height = font_size + 20
        total_height = len(lines) * line_height
        start_y = (self.height - total_height) // 2
        
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2]
            x = (self.width - text_width) // 2
            y = start_y + (i * line_height)
            
            # Draw text with outline
            outline_width = 3
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0))
            
            draw.text((x, y), line, font=font, fill=text_color)
        
        return image