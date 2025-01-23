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
    """Download YouTube video using pre-merged formats"""
    ydl_opts = {
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'format': f'bestvideo[ext=mp4][height<={quality}]+bestaudio[ext=m4a]/best[ext=mp4]',
        'quiet': True,
        'no_warnings': True,
        'noprogress': False,
        'progress_hooks': [lambda d: progress_update(d)],
        'ignoreerrors': True,
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename, info.get('title', 'video')
    except yt_dlp.utils.DownloadError as e:
        st.error(f"Download failed: {str(e)}")
        return None, None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None, None

def progress_update(d):
    """Handle download progress updates"""
    if d['status'] == 'downloading' and '_percent_str' in d:
        try:
            percent = float(d['_percent_str'].strip('%'))
            speed = d.get('_speed_str', 'N/A')
            st.session_state.progress.progress(percent/100, text=f"Downloading... {percent:.1f}% at {speed}")
        except Exception as e:
            st.session_state.progress.progress(0, text="Downloading...")

def main():
    st.title("YouTube Video Downloader 🎬")
    st.markdown("### Download videos from YouTube (No FFmpeg required)")
    
    # Initialize session state
    if 'progress' not in st.session_state:
        st.session_state.progress = st.progress(0)
    if 'download_started' not in st.session_state:
        st.session_state.download_started = False

    # UI Elements
    url = st.text_input("Enter YouTube URL:", placeholder="https://youtube.com/watch?v=...")
    quality = st.selectbox("Select Quality:", ["360p", "480p", "720p", "Best Available"])

    if st.button("Download Video"):
        if url:
            try:
                st.session_state.download_started = True
                st.session_state.progress.progress(0)
                
                with st.status("Starting download...", expanded=True) as status:
                    # Convert quality selection
                    quality_value = quality.replace("p", "") if quality != "Best Available" else "720"
                    
                    # Start download
                    file_path, title = download_video(url, quality_value)
                    
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
            finally:
                st.session_state.download_started = False
                st.session_state.progress.progress(100)
        else:
            st.warning("Please enter a valid YouTube URL")

    # Troubleshooting section
    with st.expander("Troubleshooting Guide"):
        st.markdown("""
        **Common Issues:**
        1. *Age-restricted content*: Try different video quality
        2. *Region restrictions*: Use a VPN
        3. *Download errors*: Check URL validity
        4. *Quality not available*: Select "Best Available"
        
        **Supported Content:**
        - Regular videos
        - Shorts
        - 720p or lower pre-merged formats
        """)

if __name__ == "__main__":
    main()
