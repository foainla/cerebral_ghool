import os
import requests
import subprocess
from twelvelabs import TwelveLabs
from moviepy.editor import VideoFileClip, concatenate_videoclips

headers = {
    "Content-Type": "application/json",
    "accept": "application/json",
    "x-api-key": "tlk_241Z16H2R70KP22J4CV3K22801XG"
}

# Initialize the TwelveLabs client with your API key
client = TwelveLabs(api_key="tlk_241Z16H2R70KP22J4CV3K22801XG")

# Use the existing index (replace with your actual index ID)
index_id = "66f1cde8163dbc55ba3bb220"

# Get user input for search prompts
prompt1 = input("Enter your first search prompt: ")
prompt2 = input("Enter your second search prompt: ")

# Query to search for specific content in the indexed videos
search_results1 = client.search.query(index_id=index_id, query_text=prompt1, options=["visual", "conversation"])
search_results2 = client.search.query(index_id=index_id, query_text=prompt2, options=["visual", "conversation"])

# Function to download video from a URL using ffmpeg
def download_video(video_url, video_file_path):
    try:
        # Run ffmpeg command to download the video
        ffmpeg_command = ['ffmpeg', '-i', video_url, '-c', 'copy', video_file_path]
        result = subprocess.run(ffmpeg_command, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Error in ffmpeg: {result.stderr}")
            return False

        print(f"Downloaded {video_file_path}")
        return True
    except Exception as e:
        print(f"Failed to download video: {e}")
        return False

# Download the video for the first prompt
video_clips = []
for clip in search_results1.data:
    video_id = clip.video_id
    video_file_path = f"{video_id}.mp4"
    
    # Get the video download URL
    video_file_url = f"https://api.twelvelabs.io/v1.2/indexes/{index_id}/videos/{video_id}"
    try:
        response = requests.get(video_file_url, headers=headers)
        video_download_url = response.json()["hls"]["video_url"]  # Extract video URL

        # Download video using ffmpeg
        if download_video(video_download_url, video_file_path):
            # Load the video into moviepy
            video_clip = VideoFileClip(video_file_path)
            video_clips.append(video_clip)
        break  # Only need one video from this prompt
    except Exception as e:
        print(f"Failed to download video {video_id}: {e}")

# Download the video for the second prompt
for clip in search_results2.data:
    video_id = clip.video_id
    video_file_path = f"{video_id}.mp4"
    
    # Get the video download URL
    video_file_url = f"https://api.twelvelabs.io/v1.2/indexes/{index_id}/videos/{video_id}"
    try:
        response = requests.get(video_file_url, headers=headers)
        video_download_url = response.json()["hls"]["video_url"]  # Extract video URL

        # Download video using ffmpeg
        if download_video(video_download_url, video_file_path):
            # Load the video into moviepy
            video_clip = VideoFileClip(video_file_path)
            video_clips.append(video_clip)
        break  # Only need one video from this prompt
    except Exception as e:
        print(f"Failed to download video {video_id}: {e}")

# Combine both video clips into one
if len(video_clips) == 2:
    final_video = concatenate_videoclips(video_clips)
    final_video_path = r"C:\Users\OscarChen\Desktop\combine video\combined_video.mp4"
    final_video.write_videofile(final_video_path, codec="libx264")
    print(f"Combined video created at {final_video_path}")
else:
    print("Could not download both videos or insufficient clips for stitching.")

# Clean up temporary video files
for clip in video_clips:
    clip.close()
