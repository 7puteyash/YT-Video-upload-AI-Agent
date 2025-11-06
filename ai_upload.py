import os
import pickle
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.http
from dotenv import load_dotenv
import json

# Import our custom modules
from enhanced_video_analyzer import SimpleVideoAnalyzer as VideoAnalyzer
from grok_ai import GrokAI
from thumbnail_generator import ThumbnailGenerator

# Load environment variables
load_dotenv()

# Scopes (permissions) needed for YouTube upload
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

class AIYouTubeUploader:
    def __init__(self):
        self.youtube_service = None
        self.grok_ai = GrokAI()
        self.thumbnail_generator = ThumbnailGenerator()
        
    def get_authenticated_service(self):
        """Get authenticated YouTube service"""
        if self.youtube_service:
            return self.youtube_service
            
        credentials = None

        # Token stores user session so you don't have to login every time
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                credentials = pickle.load(token)

        if not credentials:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            # Try different ports in case 8080 is busy
            ports_to_try = [8080, 8081, 8082, 8083, 8084]
            credentials = None
            
            for port in ports_to_try:
                try:
                    print(f"🔐 Authenticating using port {port}...")
                    print("📝 Note: If you see 'Google hasn't verified this app' warning:")
                    print("   1. Click 'Advanced' (bottom left)")
                    print("   2. Click 'Go to [your project] (unsafe)'")
                    print("   3. This is normal for development/testing!")
                    credentials = flow.run_local_server(port=port)
                    break
                except OSError as e:
                    if "10048" in str(e) or "Address already in use" in str(e):
                        print(f"Port {port} is busy, trying next port...")
                        continue
                    else:
                        raise e
            
            if not credentials:
                raise Exception("Could not authenticate - all ports are busy")

            with open("token.pickle", "wb") as token:
                pickle.dump(credentials, token)

        self.youtube_service = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
        return self.youtube_service

    def analyze_and_generate_content(self, video_file, custom_prompt=None):
        """Analyze video and generate AI content"""
        print("🔍 Analyzing video...")
        
        # Analyze the video
        analyzer = VideoAnalyzer(video_file)
        video_info = analyzer.analyze_video()
        
        if not video_info:
            raise Exception("Could not analyze video file")
        
        # Generate description prompt from video analysis
        analysis_prompt = analyzer.generate_description_prompt()
        print("📊 Video analysis complete!")
        
        # Generate AI content
        print("🤖 Generating AI-powered title...")
        title_result = self.grok_ai.generate_title(analysis_prompt, custom_prompt)
        title = title_result['title']
        
        print("📝 Generating AI-powered description...")
        description = self.grok_ai.generate_description(analysis_prompt, title, custom_prompt)
        
        print("🏷️ Generating relevant tags...")
        tags = self.grok_ai.generate_tags(title, description, analysis_prompt)
        
        print("🎨 Generating thumbnail concept...")
        thumbnail_concept = self.grok_ai.generate_thumbnail_concept(analysis_prompt, title)
        
        # Generate thumbnail
        print("🖼️ Creating AI-enhanced thumbnail...")
        best_frame = analyzer.get_best_thumbnail_frame()
        
        if best_frame is not None:
            thumbnail = self.thumbnail_generator.create_thumbnail(best_frame, title, thumbnail_concept)
            if thumbnail:
                thumbnail_path = f"thumbnail_{os.path.splitext(os.path.basename(video_file))[0]}.jpg"
                self.thumbnail_generator.save_thumbnail(thumbnail, thumbnail_path)
                print(f"💾 Thumbnail saved as: {thumbnail_path}")
            else:
                thumbnail_path = None
                print("⚠️ Could not create thumbnail from video frame")
        else:
            # Create text-only thumbnail as fallback
            print("📄 Creating text-based thumbnail...")
            thumbnail = self.thumbnail_generator.create_text_thumbnail(title)
            thumbnail_path = f"thumbnail_{os.path.splitext(os.path.basename(video_file))[0]}.jpg"
            self.thumbnail_generator.save_thumbnail(thumbnail, thumbnail_path)
            print(f"💾 Text thumbnail saved as: {thumbnail_path}")
        
        return {
            'title': title,
            'description': description,
            'tags': tags,
            'thumbnail_path': thumbnail_path,
            'thumbnail_concept': thumbnail_concept,
            'title_options': title_result.get('options', []),
            'title_reasoning': title_result.get('reasoning', ''),
            'video_analysis': video_info
        }
    
    def upload_video_with_ai(self, video_file, custom_prompt=None, category="22", privacy="unlisted"):
        """Upload video with AI-generated content"""
        try:
            # Get YouTube service
            youtube = self.get_authenticated_service()
            
            # Generate AI content
            ai_content = self.analyze_and_generate_content(video_file, custom_prompt)
            
            print("\n" + "="*60)
            print("🚀 AI-GENERATED CONTENT PREVIEW")
            print("="*60)
            print(f"📹 Title: {ai_content['title']}")
            print(f"📝 Description Preview: {ai_content['description'][:200]}...")
            print(f"🏷️ Tags: {', '.join(ai_content['tags'][:5])}...")
            print(f"🎨 Thumbnail: {ai_content['thumbnail_path']}")
            if ai_content['title_options']:
                print(f"💡 Alternative Titles: {', '.join(ai_content['title_options'])}")
            print("="*60)
            
            # Prepare video metadata
            video_metadata = {
                "snippet": {
                    "title": ai_content['title'],
                    "description": ai_content['description'],
                    "tags": ai_content['tags'],
                    "categoryId": category
                },
                "status": {
                    "privacyStatus": privacy
                }
            }
            
            # Upload video with resumable upload for large files
            print("⬆️ Uploading video to YouTube...")
            print("⏳ This may take several minutes depending on file size and connection speed...")
            
            # Use resumable upload for better reliability with large files
            media = googleapiclient.http.MediaFileUpload(
                video_file,
                chunksize=10 * 1024 * 1024,  # 10MB chunks
                resumable=True,
                mimetype='video/mp4'
            )
            
            request = youtube.videos().insert(
                part="snippet,status",
                body=video_metadata,
                media_body=media
            )
            
            # Execute with progress tracking
            response = None
            retry_count = 0
            max_retries = 3
            
            while response is None:
                try:
                    status, response = request.next_chunk()
                    if status:
                        file_size = os.path.getsize(video_file)
                        progress = int(status.progress() * 100)
                        print(f"  ⏳ Upload progress: {progress}%", end='\r')
                except Exception as e:
                    retry_count += 1
                    if retry_count <= max_retries:
                        print(f"\n  ⚠️ Upload interrupted, retrying ({retry_count}/{max_retries})...")
                        continue
                    else:
                        raise Exception(f"Upload failed after {max_retries} retries: {e}")
            
            print("\n✅ Video upload successful!")
            video_id = response["id"]
            
            print("✅ Video upload successful!")
            print(f"🎬 Video ID: {video_id}")
            print(f"🔗 Video URL: https://youtube.com/watch?v={video_id}")
            
            # Upload thumbnail if generated
            if ai_content['thumbnail_path'] and os.path.exists(ai_content['thumbnail_path']):
                try:
                    print("🖼️ Uploading custom thumbnail...")
                    thumbnail_request = youtube.thumbnails().set(
                        videoId=video_id,
                        media_body=googleapiclient.http.MediaFileUpload(ai_content['thumbnail_path'])
                    )
                    thumbnail_response = thumbnail_request.execute()
                    print("✅ Custom thumbnail uploaded successfully!")
                except Exception as e:
                    print(f"⚠️ Thumbnail upload failed: {e}")
            
            # Save upload report
            self.save_upload_report(video_file, video_id, ai_content)
            
            return {
                'video_id': video_id,
                'video_url': f"https://youtube.com/watch?v={video_id}",
                'ai_content': ai_content
            }
            
        except Exception as e:
            print(f"\n❌ Upload failed: {e}")
            print("\n💡 Troubleshooting tips:")
            print("  • Check your internet connection")
            print("  • Ensure the video file is not corrupted")
            print("  • Try again - the upload may be retryable")
            print("  • If persistent, try a smaller video file first")
            import traceback
            print("\nDebug info:")
            traceback.print_exc()
            return None
    
    def save_upload_report(self, video_file, video_id, ai_content):
        """Save detailed upload report"""
        # Convert numpy arrays and int64 to JSON-serializable types
        def convert_to_serializable(obj):
            if hasattr(obj, 'tolist'):  # numpy arrays
                return obj.tolist()
            elif hasattr(obj, 'item'):  # numpy scalars
                return obj.item()
            elif isinstance(obj, (int, float, str, bool, list, dict, type(None))):
                return obj
            else:
                return str(obj)
        
        video_analysis = ai_content.get('video_analysis', {})
        if 'key_frames' in video_analysis:
            del video_analysis['key_frames']  # Remove frames as they're not JSON serializable
        
        # Clean the video analysis data
        clean_analysis = {}
        for key, value in video_analysis.items():
            clean_analysis[key] = convert_to_serializable(value)
        
        report = {
            'video_file': video_file,
            'video_id': video_id,
            'video_url': f"https://youtube.com/watch?v={video_id}",
            'upload_timestamp': str(__import__('datetime').datetime.now()),
            'ai_generated_content': {
                'title': ai_content['title'],
                'description': ai_content['description'],
                'tags': ai_content['tags'],
                'thumbnail_path': ai_content['thumbnail_path'],
                'title_options': ai_content.get('title_options', []),
                'title_reasoning': ai_content.get('title_reasoning', ''),
                'thumbnail_concept': ai_content.get('thumbnail_concept', '')
            },
            'video_analysis': clean_analysis
        }
        
        report_filename = f"upload_report_{video_id}.json"
        try:
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"📊 Upload report saved: {report_filename}")
        except Exception as e:
            print(f"⚠️ Could not save report: {e}")

def main():
    """Main function for standalone usage"""
    # Initialize uploader
    uploader = AIYouTubeUploader()
    
    # Example usage
    video_file = "test_video.mp4"  # Change this to your video file
    custom_prompt = "This is an educational video about technology"  # Optional: provide context
    
    if not os.path.exists(video_file):
        print(f"❌ Video file not found: {video_file}")
        return
    
    print("🤖 Starting AI-Powered YouTube Upload...")
    print(f"📁 Video file: {video_file}")
    
    result = uploader.upload_video_with_ai(
        video_file=video_file,
        custom_prompt=custom_prompt,
        category="22",  # People & Blogs
        privacy="public"  # Change to "public", "private", or "unlisted"
    )
    
    if result:
        print("\n🎉 Upload completed successfully!")
        print(f"🎬 Your video is now live at: {result['video_url']}")
    else:
        print("\n❌ Upload failed. Please check the errors above.")

if __name__ == "__main__":
    main()