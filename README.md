# 🤖 AI YouTube Uploader

An intelligent YouTube upload system that uses Grok AI to automatically generate engaging titles, descriptions, thumbnails, and tags for your videos.

## ✨ Features

- 🎯 **AI-Generated Titles**: Engaging, SEO-optimized titles that drive clicks
- 📝 **Smart Descriptions**: Comprehensive descriptions with natural keyword integration
- 🖼️ **Auto Thumbnails**: AI-enhanced thumbnails from best video frames
- 🏷️ **Relevant Tags**: Automatically generated tags for better discoverability
- 📊 **Video Analysis**: Deep analysis of your video content for better AI generation
- 🔐 **Secure Authentication**: OAuth2 integration with Google/YouTube
- 📈 **Upload Reports**: Detailed reports of each upload with AI-generated content

## 🚀 Quick Start

### 1. Setup Configuration Files
First, copy the example files and add your credentials:

```bash
# Copy environment file
copy .env.example .env

# Copy credentials file  
copy credentials.json.example credentials.json
```

### 2. Setup API Keys
```bash
python setup.py
```
Enter your Grok API key when prompted, or manually edit the `.env` file.

### 3. Configure YouTube API
- Visit [Google Cloud Console](https://console.cloud.google.com/)
- Enable YouTube Data API v3
- Create OAuth 2.0 credentials
- Download and replace `credentials.json`

### 4. Basic Upload
```bash
python ai_upload.py
```

### 3. Advanced Usage
```python
from ai_upload import AIYouTubeUploader

uploader = AIYouTubeUploader()

# Upload with custom context
result = uploader.upload_video_with_ai(
    video_file="my_video.mp4",
    custom_prompt="This is a tutorial about Python programming",
    privacy="public"  # or "private", "unlisted"
)

print(f"Video uploaded: {result['video_url']}")
```

## 📁 File Structure

```
AI agent/
├── ai_upload.py           # Main AI-powered upload script
├── upload.py             # Original simple upload script
├── setup.py              # Configuration and setup tool
├── video_analyzer.py     # Video content analysis
├── grok_ai.py           # Grok AI integration
├── thumbnail_generator.py # AI thumbnail creation
├── credentials.json      # YouTube API credentials
├── .env                 # API keys and configuration
└── test_video.mp4       # Your video file
```

## 🔧 Configuration

Edit `.env` file for custom settings:

```env
# Grok API Configuration
GROK_API_KEY=your_actual_grok_api_key

# YouTube Upload Settings
DEFAULT_CATEGORY=22
DEFAULT_PRIVACY=unlisted

# AI Generation Settings
MAX_TITLE_LENGTH=100
MAX_DESCRIPTION_LENGTH=5000
THUMBNAIL_WIDTH=1280
THUMBNAIL_HEIGHT=720
```

## 🎨 AI Features Explained

### Title Generation
- Analyzes video content and generates 3 title options
- Optimizes for engagement and SEO
- Keeps titles between 40-100 characters
- Uses power words and emotional triggers

### Description Generation
- Creates comprehensive descriptions (150-500 words)
- Includes natural keyword integration
- Adds call-to-action elements
- Structures content for readability

### Thumbnail Creation
- Extracts best frames from your video
- Enhances images for thumbnail optimization
- Adds text overlays with title
- Creates fallback text-only thumbnails

### Tag Generation
- Generates 15-20 relevant tags
- Mixes broad and specific terms
- Includes trending keywords
- Optimizes for discoverability

## 📊 Video Analysis

The system analyzes:
- Video duration and resolution
- Dominant colors and brightness
- Motion levels and pacing
- Audio presence
- Best thumbnail frames

## 🔐 Security

- API keys stored in `.env` file (not committed to git)
- OAuth2 authentication with Google
- Secure token storage with `token.pickle`

## 🛠️ Troubleshooting

### Common Issues

1. **"ModuleNotFoundError: No module named 'groq'"**
   - Run: `pip install groq opencv-python Pillow moviepy requests python-dotenv`

2. **"GROK_API_KEY not found"**
   - Run `python setup.py` to configure your API key
   - Or manually add it to the `.env` file

3. **"Google hasn't verified this app"**
   - Click "Advanced" then "Go to [project name] (unsafe)"
   - This is normal for development apps

4. **Port 8080 already in use**
   - The script automatically tries ports 8080-8084
   - Or close other applications using these ports

### Getting API Keys

1. **Grok API Key**:
   - Visit: https://console.groq.com/keys
   - Create account and generate API key

2. **YouTube API Credentials**:
   - Visit: Google Cloud Console
   - Enable YouTube Data API v3
   - Create OAuth 2.0 credentials
   - Download as `credentials.json`

## 📈 Upload Reports

Each upload generates a detailed JSON report containing:
- AI-generated content (title, description, tags)
- Video analysis results
- Alternative title options
- Thumbnail creation details
- Upload timestamp and video URL

## 🎯 Best Practices

1. **Video Quality**: Use high-quality videos for better thumbnail generation
2. **Custom Prompts**: Provide context for better AI generation
3. **Privacy Settings**: Start with "unlisted" for testing
4. **File Names**: Use descriptive video file names
5. **Regular Updates**: Keep your Grok API key secure and active

## 🤝 Support

If you encounter issues:
1. Run `python setup.py` to test configuration
2. Check the upload reports for detailed information
3. Ensure all dependencies are installed
4. Verify API keys are correctly configured

## 📝 Example Output

```
🚀 AI-GENERATED CONTENT PREVIEW
============================================================
📹 Title: 10 Mind-Blowing Python Tricks That Will Change Your Code Forever
📝 Description Preview: Discover game-changing Python techniques that professional developers use to write cleaner, faster, and more efficient code. In this comprehensive tutorial...
🏷️ Tags: python, programming, coding tips, software development, tutorial...
🎨 Thumbnail: thumbnail_my_video.jpg
💡 Alternative Titles: Python Secrets Every Developer Should Know, Advanced Python Techniques for Better Code
============================================================
✅ Video upload successful!
🎬 Video ID: dQw4w9WgXcQ
🔗 Video URL: https://youtube.com/watch?v=dQw4w9WgXcQ
```

---

Made with ❤️ and 🤖 AI
