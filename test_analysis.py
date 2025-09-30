"""
Video Analysis Test Script
This script shows you exactly what the AI sees in your video
"""

from enhanced_video_analyzer import SimpleVideoAnalyzer as VideoAnalyzer
from grok_ai import GrokAI
import json

def analyze_video_content(video_file="test_video.mp4"):
    print("🔍 DEEP VIDEO ANALYSIS TEST")
    print("=" * 50)
    
    # Analyze the video
    analyzer = VideoAnalyzer(video_file)
    video_info = analyzer.analyze_video()
    
    if not video_info:
        print("❌ Could not analyze video")
        return
    
    print("📊 TECHNICAL SPECIFICATIONS:")
    print(f"   Duration: {int(video_info.get('duration', 0) // 60)}:{int(video_info.get('duration', 0) % 60):02d}")
    print(f"   Resolution: {video_info.get('resolution')}")
    print(f"   FPS: {video_info.get('fps', 0):.1f}")
    print(f"   Total Frames: {video_info.get('frame_count', 0):,}")
    
    print("\n🎨 VISUAL ANALYSIS:")
    brightness = video_info.get('brightness_levels', {})
    print(f"   Lighting: {brightness.get('description', 'unknown')}")
    print(f"   Brightness Score: {brightness.get('average', 0):.1f}/255")
    print(f"   Lighting Consistency: {brightness.get('variation', 0):.1f}")
    
    print(f"   Motion Level: {video_info.get('motion_level', 'unknown')}")
    print(f"   Motion Score: {video_info.get('average_motion_score', 0):.1f}")
    print(f"   Scene Changes: {video_info.get('scene_changes', 0)} detected")
    
    print(f"   Color Variety: {video_info.get('color_variety', 'unknown')}")
    print(f"   Visual Complexity: {video_info.get('visual_complexity', 'unknown')}")
    
    print("\n🤖 CONTENT CLASSIFICATION:")
    print(f"   Content Type: {video_info.get('content_type', 'unknown')}")
    print(f"   Text/Graphics: {'Present' if video_info.get('text_presence') else 'Minimal'}")
    
    print("\n📝 AI PROMPT GENERATION:")
    prompt = analyzer.generate_description_prompt()
    print("Generated analysis prompt for AI:")
    print("-" * 30)
    print(prompt)
    print("-" * 30)
    
    # Test AI generation
    print("\n🤖 TESTING AI TITLE GENERATION...")
    try:
        grok = GrokAI()
        title_result = grok.generate_title(prompt, "Test video content analysis")
        
        print(f"✅ Generated Title: {title_result['title']}")
        if title_result.get('options'):
            print("   Alternative options:")
            for i, option in enumerate(title_result['options'][:3], 1):
                print(f"   {i}. {option}")
        
        if title_result.get('reasoning'):
            print(f"   AI Reasoning: {title_result['reasoning']}")
            
    except Exception as e:
        print(f"❌ AI Title Generation Error: {e}")
    
    print("\n💾 RAW ANALYSIS DATA:")
    # Save detailed analysis
    with open('detailed_analysis.json', 'w') as f:
        # Convert numpy types for JSON
        clean_data = {}
        for key, value in video_info.items():
            if key == 'key_frames':
                clean_data[key] = f"[{len(value)} frames stored]"
            elif hasattr(value, 'item'):  # numpy scalar
                clean_data[key] = value.item()
            elif hasattr(value, 'tolist'):  # numpy array
                clean_data[key] = value.tolist()
            else:
                clean_data[key] = value
        
        json.dump(clean_data, f, indent=2)
    
    print("   Detailed analysis saved to 'detailed_analysis.json'")
    print("\n🎯 ANALYSIS COMPLETE!")
    
    return video_info

if __name__ == "__main__":
    analyze_video_content()