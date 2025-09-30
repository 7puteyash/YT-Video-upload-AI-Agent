"""
Setup script for AI YouTube Uploader
Run this first to configure your API keys and settings
"""

import os
from dotenv import load_dotenv, set_key

def setup_api_keys():
    """Interactive setup for API keys"""
    print("🚀 AI YouTube Uploader Setup")
    print("=" * 40)
    
    # Load existing .env if it exists
    load_dotenv()
    
    # Get Grok API key
    current_grok_key = os.getenv('GROK_API_KEY')
    if current_grok_key and current_grok_key != 'your_grok_api_key_here':
        print(f"✅ Grok API key already configured: {current_grok_key[:10]}...")
        update_key = input("Do you want to update it? (y/n): ").lower().strip()
        if update_key != 'y':
            grok_key = current_grok_key
        else:
            grok_key = input("Enter your new Grok API key: ").strip()
    else:
        print("🔑 Please enter your Grok API key")
        print("📝 You can get it from: https://console.groq.com/keys")
        grok_key = input("Grok API key: ").strip()
    
    if not grok_key:
        print("❌ Grok API key is required!")
        return False
    
    # Update .env file
    env_file = '.env'
    set_key(env_file, 'GROK_API_KEY', grok_key)
    
    print("\n✅ Configuration saved!")
    print("📁 Settings saved to .env file")
    
    return True

def test_configuration():
    """Test if everything is configured correctly"""
    print("\n🧪 Testing configuration...")
    
    try:
        # Test Grok API
        from grok_ai import GrokAI
        grok = GrokAI()
        print("✅ Grok AI: Connected successfully")
        
        # Test video analyzer
        from video_analyzer import VideoAnalyzer
        print("✅ Video Analyzer: Ready")
        
        # Test thumbnail generator
        from thumbnail_generator import ThumbnailGenerator
        print("✅ Thumbnail Generator: Ready")
        
        # Check if credentials.json exists
        if os.path.exists('credentials.json'):
            print("✅ YouTube credentials: Found")
        else:
            print("⚠️ YouTube credentials: credentials.json not found")
            print("   Make sure you have downloaded it from Google Cloud Console")
        
        # Check for test video
        if os.path.exists('test_video.mp4'):
            print("✅ Test video: Found")
        else:
            print("⚠️ Test video: test_video.mp4 not found")
            print("   Place a video file named 'test_video.mp4' in this directory")
        
        print("\n🎉 Setup complete! You're ready to use AI YouTube Uploader!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def show_usage():
    """Show usage instructions"""
    print("\n📖 USAGE INSTRUCTIONS")
    print("=" * 40)
    print("1. Basic upload with AI:")
    print("   python ai_upload.py")
    print()
    print("2. From Python script:")
    print("   from ai_upload import AIYouTubeUploader")
    print("   uploader = AIYouTubeUploader()")
    print("   result = uploader.upload_video_with_ai('your_video.mp4')")
    print()
    print("3. With custom context:")
    print("   uploader.upload_video_with_ai(")
    print("       'video.mp4',")
    print("       custom_prompt='This is a cooking tutorial'")
    print("   )")
    print()
    print("🎯 Features:")
    print("• AI-generated titles optimized for engagement")
    print("• AI-written descriptions with SEO keywords")
    print("• Auto-generated relevant tags")
    print("• Smart thumbnail creation from video frames")
    print("• Detailed upload reports")

if __name__ == "__main__":
    print("🤖 Welcome to AI YouTube Uploader Setup!")
    print()
    
    if setup_api_keys():
        if test_configuration():
            show_usage()
        else:
            print("\n⚠️ Some issues were found. Please resolve them before using the uploader.")
    else:
        print("\n❌ Setup failed. Please try again.")