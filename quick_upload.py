#!/usr/bin/env python3
"""
🚀 ONE-CLICK YouTube Upload with AI
Quick upload script for your AI YouTube uploader
"""

import os
import sys
from pathlib import Path
from ai_upload import AIYouTubeUploader


def find_latest_video():
    """Find the latest MP4 video in the current directory"""
    videos = list(Path(".").glob("*.mp4"))
    if not videos:
        return None
    # Return the most recently modified video
    return max(videos, key=lambda p: p.stat().st_mtime)


def interactive_upload():
    """Interactive one-click upload"""
    print("\n" + "="*60)
    print("🎥 AI-POWERED YOUTUBE UPLOADER - ONE CLICK UPLOAD")
    print("="*60)
    
    # Find video
    video_file = find_latest_video()
    
    if not video_file:
        print("❌ No video file found in this directory!")
        print("📁 Please upload a .mp4 video file to this folder first.")
        return False
    
    print(f"\n✅ Found video: {video_file.name}")
    print(f"📊 Size: {video_file.stat().st_size / (1024*1024):.2f} MB")
    
    # Ask for custom prompt (optional)
    print("\n📝 Enter a brief description of your video (or press Enter to skip):")
    custom_prompt = input(">>> ").strip()
    if not custom_prompt:
        custom_prompt = None
    
    # Ask for privacy setting
    print("\n🔒 Privacy settings:")
    print("1. Public - Everyone can see it")
    print("2. Unlisted - Only people with link can see it")
    print("3. Private - Only you can see it")
    
    privacy_choice = input("Choose (1/2/3, default=2): ").strip() or "2"
    privacy_map = {"1": "public", "2": "unlisted", "3": "private"}
    privacy = privacy_map.get(privacy_choice, "unlisted")
    
    # Start upload
    print("\n" + "="*60)
    print("🚀 STARTING UPLOAD...")
    print("="*60)
    
    try:
        uploader = AIYouTubeUploader()
        result = uploader.upload_video_with_ai(
            video_file=str(video_file),
            custom_prompt=custom_prompt,
            privacy=privacy
        )
        
        if result:
            print("\n" + "="*60)
            print("🎉 SUCCESS! VIDEO UPLOADED!")
            print("="*60)
            print(f"✅ Video URL: {result['video_url']}")
            print(f"🎬 Video ID: {result['video_id']}")
            print(f"📹 Title: {result['ai_content']['title']}")
            print(f"🏷️ Tags: {', '.join(result['ai_content']['tags'][:5])}")
            print("\n💾 Detailed report saved!")
            print("="*60)
            return True
        else:
            print("\n❌ Upload failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def batch_upload():
    """Upload all MP4 files in the directory"""
    videos = list(Path(".").glob("*.mp4"))
    
    if not videos:
        print("❌ No video files found!")
        return False
    
    print(f"\n📁 Found {len(videos)} video(s) to upload:")
    for i, video in enumerate(videos, 1):
        print(f"  {i}. {video.name}")
    
    confirm = input("\n⚠️ Upload all videos? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Cancelled.")
        return False
    
    uploader = AIYouTubeUploader()
    successful = 0
    
    for video in videos:
        print(f"\n📹 Uploading: {video.name}")
        try:
            result = uploader.upload_video_with_ai(
                video_file=str(video),
                privacy="unlisted"
            )
            if result:
                print(f"✅ Success: {result['video_url']}")
                successful += 1
            else:
                print(f"❌ Failed: {video.name}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n📊 Results: {successful}/{len(videos)} videos uploaded successfully!")
    return successful > 0


if __name__ == "__main__":
    # Check if setup is complete
    if not os.path.exists(".env"):
        print("❌ Configuration missing!")
        print("📋 Please run: python setup.py")
        sys.exit(1)
    
    if not os.path.exists("credentials.json"):
        print("❌ YouTube credentials missing!")
        print("📋 Please add credentials.json (see README for instructions)")
        sys.exit(1)
    
    # Show menu
    print("\n" + "="*60)
    print("🎥 AI YOUTUBE UPLOADER")
    print("="*60)
    print("1. Upload latest video (ONE CLICK)")
    print("2. Upload all videos")
    print("3. Exit")
    
    choice = input("\nChoose option (1/2/3): ").strip()
    
    if choice == "1":
        interactive_upload()
    elif choice == "2":
        batch_upload()
    elif choice == "3":
        print("Goodbye! 👋")
    else:
        print("Invalid choice!")
