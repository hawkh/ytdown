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
    """Download YouTube video with robust error handling"""
    ydl_opts = {
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'noprogress': False,
        'progress_hooks': [lambda d: progress_update(d)],
        'ignoreerrors': True,
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Validate URL and extract info
            try:
                info = ydl.extract_info(url, download=False)
            except Exception as e:
                st.error(f"Invalid URL or unavailable video: {str(e)}")
                return None, None

            if not info or 'formats' not in info:
                st.error("Could not retrieve video information")
                return None, None

            # Check available formats
            available_heights = sorted({
                fmt.get('height') for fmt in info['formats'] 
                if fmt.get('height') and fmt.get('ext') == 'mp4'
            }, reverse=True)

            # Handle quality selection
            if quality != "Best Available":
                target_height = int(quality.replace("p", ""))
                if target_height not in available_heights:
                    st.error(f"{quality} not available. Available resolutions: {', '.join(map(str, available_heights))}p")
                    return None, None
                ydl_opts['format'] = f'bestvideo[height={target_height}][ext=mp4]+bestaudio/best'

            # Start download
            st.session_state.progress.progress(0.1, text="Initializing download...")
            ydl.download([url])
            
            filename = ydl.prepare_filename(info)
            return filename, info.get('title') or "untitled"

    except yt_dlp.utils.DownloadError as e:
        st.error(f"Download failed: {str(e)}")
        return None, None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None, None

def progress_update(d):
    """Robust progress updates with null checks"""
    if not d or 'status' not in d:
        return
        
    try:
        if d['status'] == 'downloading':
            percent = float(d.get('_percent_str', '0%').strip('%')) if d.get('_percent_str') else 0
            speed = d.get('_speed_str', 'N/A')
            text = f"Downloading... {percent:.1f}% at {speed}"
            st.session_state.progress.progress(percent/100, text=text)
    except Exception as e:
        st.session_state.progress.progress(0, text="Download in progress...")

def main():
    st.title("YouTube Video Downloader 🎬")
    st.markdown("### Safe and reliable video downloads")
    
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
                
                with st.status("Processing...", expanded=True) as status:
                    file_path, title = download_video(url, quality)
                    
                    if file_path and os.path.exists(file_path):
                        status.update(label="Download Complete! ✅", state="complete")
                        st.balloons()
                        
                        # Show preview
                        st.subheader(f"Downloaded: {title}")
                        st.video(file_path)
                        
                        # Create download button
                        with open(file_path, "rb") as f:
                            st.download_button(
                                label="Save Video",
                                data=f,
                                file_name=os.path.basename(file_path),
                                mime="video/mp4"
                            )
                        
                        # Cleanup
                        try:
                            os.remove(file_path)
                        except Exception as e:
                            st.error(f"Cleanup failed: {str(e)}")
                    else:
                        status.update(label="Download Failed ❌", state="error")
            except Exception as e:
                st.error(f"Fatal error: {str(e)}")
            finally:
                st.session_state.download_started = False
                st.session_state.progress.progress(100)
        else:
            st.warning("Please enter a valid YouTube URL")

    # Troubleshooting guide
    with st.expander("ℹ️ Troubleshooting Guide"):
        st.markdown("""
        **Common Solutions:**
        1. For age-restricted content: Try different quality
        2. Region-blocked videos: Use a VPN
        3. Invalid URL errors: Check the URL format
        4. Quality not available: Use 'Best Available' option

        **Supported Content:**
        - Regular videos
        - Shorts
        - 720p or lower pre-merged MP4s
        """)

if __name__ == "__main__":
    main()
