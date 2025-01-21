# main.py
import streamlit as st
import os
import yt_dlp
from typing import Tuple, Optional
from pathlib import Path

# Configuration
DOWNLOAD_FOLDER = "yt_downloads"
Path(DOWNLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

def download_video(url: str, quality: str) -> Tuple[Optional[str], Optional[str]]:
    """Download YouTube video using yt-dlp with progress tracking"""
    ydl_opts = {
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'format': f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]',
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
        'noprogress': False,
        'progress_hooks': [lambda d: st.session_state.progress.update(d)],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            filename = ydl.prepare_filename(info)
            
            if not st.session_state.get('download_started', False):
                st.session_state.download_started = True
                ydl.download([url])
                
            return filename, info.get('title', 'video')
    except yt_dlp.utils.DownloadError as e:
        st.error(f"Download failed: {str(e)}")
        return None, None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None, None

def progress_update(d):
    """Handle download progress updates"""
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', "0%")
        speed = d.get('_speed_str', "N/A")
        st.session_state.progress.progress(float(percent.strip('%'))/100, text=f"Downloading... {percent} at {speed}")

def main():
    st.title("YouTube Video Downloader 🎬")
    st.markdown("### Download videos from YouTube")
    
    # Initialize session state
    if 'progress' not in st.session_state:
        st.session_state.progress = st.progress(0)
    if 'download_started' not in st.session_state:
        st.session_state.download_started = False

    # UI Elements
    url = st.text_input("Enter YouTube URL:", placeholder="https://youtube.com/watch?v=...")
    quality = st.selectbox("Select Quality:", ["144p", "360p", "720p", "1080p", "Best Available"])
    quality = quality.replace("p", "").split()[0] if quality != "Best Available" else "2160"

    if st.button("Download Video"):
        if url:
            try:
                st.session_state.download_started = False
                with st.status("Starting download...", expanded=True) as status:
                    # Start download
                    file_path, title = download_video(url, quality)
                    
                    if file_path and os.path.exists(file_path):
                        status.update(label="Download Complete! ✅", state="complete")
                        st.balloons()
                        
                        # Show video preview
                        st.subheader(f"Downloaded: {title}")
                        st.video(file_path)
                        
                        # Create download button
                        with open(file_path, "rb") as f:
                            st.download_button(
                                label="Save Video File",
                                data=f,
                                file_name=os.path.basename(file_path),
                                mime="video/mp4"
                            )
                        
                        # Cleanup
                        os.remove(file_path)
            except Exception as e:
                st.error(f"Error during download: {str(e)}")
        else:
            st.warning("Please enter a valid YouTube URL")

    # Debug section
    with st.expander("Troubleshooting Tips"):
        st.markdown("""
        - If downloads fail:
          1. Try a different video quality
          2. Check if the video is age-restricted
          3. Use a VPN if region-blocked
        - Supported formats: Regular videos, shorts, playlists
        """)

if __name__ == "__main__":
    main()
