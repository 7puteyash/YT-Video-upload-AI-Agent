#!/usr/bin/env python3
"""
🎥 UPLOAD final_demo.mp4 - ONE CLICK
Direct upload script for your latest video
"""

import os
from ai_upload import AIYouTubeUploader

def main():
    video_file = "final_demo.mp4"
    
    if not os.path.exists(video_file):
        print(f"❌ Video not found: {video_file}")
        return
    
    print("\n" + "="*60)
    print("🚀 UPLOADING TO YOUTUBE")
    print("="*60)
    print(f"📹 Video: {video_file}")
    
    # Ask for optional context
    print("\n📝 Brief description of your video (optional, press Enter to skip):")
    custom_prompt = input(">>> ").strip() or None
    
    # Ask for privacy
    print("\n🔒 Privacy setting?")
    print("1. Public (everyone can see)")
    print("2. Unlisted (only with link)")
    print("3. Private (only you)")
    choice = input("Choose (1/2/3, default=2): ").strip() or "2"
    privacy_map = {"1": "public", "2": "unlisted", "3": "private"}
    privacy = privacy_map.get(choice, "unlisted")
    
    print("\n⏳ Starting upload (this may take 2-5 minutes)...")
    print("="*60 + "\n")
    
    try:
        uploader = AIYouTubeUploader()
        result = uploader.upload_video_with_ai(
            video_file=video_file,
            custom_prompt=custom_prompt,
            privacy=privacy
        )
        
        if result:
            print("\n" + "="*60)
            print("✅ SUCCESS! VIDEO UPLOADED TO YOUTUBE!")
            print("="*60)
            print(f"\n🎬 Video ID: {result['video_id']}")
            print(f"🔗 Watch here: {result['video_url']}")
            print(f"\n📹 Title: {result['ai_content']['title']}")
            print(f"📝 First 100 chars of description:\n   {result['ai_content']['description'][:100]}...")
            print(f"\n🏷️ Tags: {', '.join(result['ai_content']['tags'][:5])}...")
            print(f"\n🖼️ Custom thumbnail: {result['ai_content']['thumbnail_path']}")
            print("\n💾 Detailed report saved!")
            print("="*60)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if not os.path.exists(".env"):
        print("❌ Please run: python setup.py")
        exit(1)
    if not os.path.exists("credentials.json"):
        print("❌ Please add credentials.json")
        exit(1)
    main()
