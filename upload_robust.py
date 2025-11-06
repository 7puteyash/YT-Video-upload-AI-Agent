#!/usr/bin/env python3
"""
🎥 ROBUST UPLOAD - With Retry Logic
Handles network timeouts and large files better
"""

import os
import sys
import time
from ai_upload import AIYouTubeUploader

def upload_with_retry(video_file, custom_prompt=None, privacy="unlisted", max_attempts=3):
    """Upload video with automatic retry logic"""
    
    print("\n" + "="*60)
    print("🚀 YOUTUBE UPLOAD WITH AUTOMATIC RETRY")
    print("="*60)
    print(f"📹 Video: {video_file}")
    print(f"📊 Size: {os.path.getsize(video_file) / (1024*1024):.2f} MB")
    print(f"🔒 Privacy: {privacy}")
    
    uploader = AIYouTubeUploader()
    
    for attempt in range(1, max_attempts + 1):
        try:
            print(f"\n🔄 Attempt {attempt}/{max_attempts}")
            print("-" * 60)
            
            result = uploader.upload_video_with_ai(
                video_file=video_file,
                custom_prompt=custom_prompt,
                privacy=privacy
            )
            
            if result:
                print("\n" + "="*60)
                print("✅ SUCCESS! VIDEO UPLOADED!")
                print("="*60)
                print(f"🎬 Video ID: {result['video_id']}")
                print(f"🔗 Watch: {result['video_url']}")
                print(f"📹 Title: {result['ai_content']['title']}")
                print(f"🏷️ Tags: {', '.join(result['ai_content']['tags'][:5])}...")
                return True
            else:
                if attempt < max_attempts:
                    wait_time = attempt * 10
                    print(f"\n⚠️ Upload failed, retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"\n❌ Upload failed after {max_attempts} attempts")
                    return False
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            if attempt < max_attempts:
                wait_time = attempt * 10
                print(f"⚠️ Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"❌ Upload failed after {max_attempts} attempts")
                return False
    
    return False


def main():
    # Configuration checks
    if not os.path.exists(".env"):
        print("❌ Configuration missing!")
        print("Run: python setup.py")
        sys.exit(1)
    
    if not os.path.exists("credentials.json"):
        print("❌ YouTube credentials missing!")
        print("Add credentials.json file")
        sys.exit(1)
    
    # Find video
    from pathlib import Path
    videos = list(Path(".").glob("*.mp4"))
    
    if not videos:
        print("❌ No MP4 videos found!")
        sys.exit(1)
    
    video_file = max(videos, key=lambda p: p.stat().st_mtime)
    print(f"📹 Found video: {video_file.name}")
    
    # Get description
    print("\n📝 Enter description (or press Enter to skip):")
    custom_prompt = input(">>> ").strip() or None
    
    # Get privacy setting
    print("\n🔒 Privacy (1=Public, 2=Unlisted, 3=Private, default=2):")
    choice = input(">>> ").strip() or "2"
    privacy_map = {"1": "public", "2": "unlisted", "3": "private"}
    privacy = privacy_map.get(choice, "unlisted")
    
    # Upload with retry
    success = upload_with_retry(
        str(video_file),
        custom_prompt=custom_prompt,
        privacy=privacy,
        max_attempts=3
    )
    
    if success:
        print("\n🎉 Done! Check YouTube Studio to manage your video.")
    else:
        print("\n💡 The upload appears to be having issues.")
        print("Tips:")
        print("  1. Check internet connection")
        print("  2. Try with a smaller test video first")
        print("  3. Make sure credentials.json is valid")
        print("  4. Try again in a few moments")


if __name__ == "__main__":
    main()
