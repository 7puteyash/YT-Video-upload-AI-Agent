import os
import pickle
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.http

# Scopes (permissions) needed for YouTube upload
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    credentials = None

    # Token stores user session so you don’t have to login every time
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

    return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

def upload_video(file, title, description, category="22", privacy="public"):
    youtube = get_authenticated_service()

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "categoryId": category
            },
            "status": {
                "privacyStatus": privacy
            }
        },
        media_body=googleapiclient.http.MediaFileUpload(file)
    )

    response = request.execute()
    print("✅ Upload successful!")
    print("Video ID:", response["id"])

# Example usage
if __name__ == "__main__":
    upload_video(
        file="test_video.mp4",  # Place a video file in same folder
        title="My First AI Upload",
        description="This video was uploaded using Python & YouTube API 🚀",
        category="22",  # People & Blogs
        privacy="unlisted"  # public / private / unlisted
    )
