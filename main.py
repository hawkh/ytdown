# main.py
import streamlit as st
import os
from pytube import YouTube
from typing import Optional

def download_youtube_video(url: str, quality: str = "720p") -> Optional[str]:
    """Download YouTube video and return file path"""
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(res=quality, progressive=True).first()
        if not stream:
            return None
        
        download_path = stream.download(output_path="downloads")
        return download_path
        
    except Exception as e:
        st.error(f"Download failed: {str(e)}")
        return None

def main():
    st.title("YouTube Video Downloader 🎬")
    st.markdown("Enter a YouTube URL to download videos")
    
    # Input section
    url = st.text_input("YouTube URL:", placeholder="https://youtube.com/watch?v=...")
    quality = st.selectbox("Select Quality:", ["144p", "360p", "720p", "1080p"])
    
    if st.button("Download Video"):
        if url:
            with st.status("Downloading...", expanded=True) as status:
                try:
                    # Create downloads directory
                    os.makedirs("downloads", exist_ok=True)
                    
                    # Show progress
                    st.write("🔍 Analyzing video...")
                    progress_bar = st.progress(0)
                    
                    # Download video
                    st.write("⬇️ Downloading...")
                    file_path = download_youtube_video(url, quality)
                    progress_bar.progress(100)
                    
                    if file_path:
                        status.update(label="Download complete! ✅", state="complete")
                        st.balloons()
                        
                        # Show download info
                        st.subheader("Downloaded Video")
                        st.video(file_path)
                        
                        # Create download button
                        with open(file_path, "rb") as f:
                            st.download_button(
                                label="Save Video",
                                data=f,
                                file_name=os.path.basename(file_path),
                                mime="video/mp4"
                            )
                        
                        # Clean up file after session
                        os.remove(file_path)
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a valid YouTube URL")

if __name__ == "__main__":
    main()