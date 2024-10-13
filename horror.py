import os
import requests
from twelvelabs import TwelveLabs
from moviepy.editor import VideoFileClip, concatenate_videoclips

# Initialize the TwelveLabs client with your API key
client = TwelveLabs(api_key="tlk_241Z16H2R70KP22J4CV3K22801XG")

# Use the existing index (replace with your actual index ID)
index_id = "66f1cde8163dbc55ba3bb220"

# Get user input for search prompts
prompt1 = input("Enter your first search prompt: ")
prompt2 = input("Enter your second search prompt: ")

# Example query to search for specific content in the indexed videos
search_results1 = client.search.query(index_id=index_id, query_text=prompt1, options=["visual", "conversation"])
search_results2 = client.search.query(index_id=index_id, query_text=prompt2, options=["visual", "conversation"])

# Filtered video IDs based on high confidence score
high_confidence_videos = []

# Set a threshold for confidence (you can adjust this value)
confidence_threshold = "high"  # Example numerical threshold

# Process search results for the first prompt
for clip in search_results1.data:
    if clip.confidence == confidence_threshold:  # Changed to a numerical comparison
        high_confidence_videos.append(clip.video_id)

# Process search results for the second prompt
for clip in search_results2.data:
    if clip.confidence == confidence_threshold:  # Changed to a numerical comparison
        high_confidence_videos.append(clip.video_id)

# Remove duplicates by converting the list to a set and back to a list
high_confidence_videos = list(set(high_confidence_videos))

# Generate video snippets and combine them
video_clips = []
for video_id in high_confidence_videos:
    print(f"Generating summary for video: {video_id}")
    
    # Generate a summary if needed
    res = client.generate.summarize(video_id=video_id, type="summary")
    print(f"Summary for video {video_id}: {res.summary}")

    # Correct URL for fetching video file
    video_file_url = f"https://api.twelvelabs.io/v1.2/indexes/{index_id}/videos/{video_id}"  # Adjusted URL

    video_file_path = f"{video_id}.mp4"  # Temporary local file

    # Download the video file
    try:
        print(f"Downloading video from {video_file_url}...")
        print(response.json()["hls"]["video_url"])
        response = requests.get(video_file_url)
        response.raise_for_status()  # Raise an error for bad responses
        

        # Extract the video URL from the response if needed
        video_data = response.json()
        video_download_url = video_data.get("video_url")  # Adjust based on actual response structure

        if video_download_url:
            video_response = requests.get(video_download_url, stream=True)
            video_response.raise_for_status()  # Raise an error for bad responses
            
            with open(video_file_path, 'wb') as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Downloaded {video_file_path}")
        else:
            print(f"No video URL found for video {video_id}")

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred while downloading video {video_id}: {e}")
        continue  # Skip this video and proceed to the next
    except Exception as e:
        print(f"Failed to download video {video_id}: {e}")
        continue  # Skip this video and proceed to the next

    # Load video snippet into moviepy
    try:
        video_clip = VideoFileClip(video_file_path)
        video_clips.append(video_clip)
    except Exception as e:
        print(f"Failed to load video clip {video_id}: {e}")

# Combine all video clips into one
if video_clips:
    final_video = concatenate_videoclips(video_clips)
    final_video_path = r"C:\Users\OscarChen\Desktop\combine video\combined_video.mp4"
    final_video.write_videofile(final_video_path, codec="libx264")

    print(f"Combined video created at {final_video_path}")
else:
    print("No high confidence videos found.")

# Clean up temporary video files (optional)
for clip in video_clips:
    clip.close()
