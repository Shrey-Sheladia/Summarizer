import streamlit as st
from PIL import Image
import io
import requests
from Utils import *

# Streamlit App
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.set_page_config(page_title="YouTube Video Summarizer", layout="centered", page_icon="ShreyIconS2.png")
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("YouTube Video Summarizer")

video_url = st.text_input("Enter a YouTube video URL:")
chat_history = []

# Initialize the previous_video_url, message_history, and other variables in session_state
if "previous_video_url" not in st.session_state:
    st.session_state.previous_video_url = ""
if "message_history" not in st.session_state:
    st.session_state.message_history = []
if "thumbnail" not in st.session_state:
    st.session_state.thumbnail = None
if "video_title" not in st.session_state:
    st.session_state.video_title = ""
if "channel_name" not in st.session_state:
    st.session_state.channel_name = ""
if "summary" not in st.session_state:
    st.session_state.summary = ""

# Create placeholders for video information, thumbnail, and summary
video_info_placeholder1 = st.empty()
video_info_placeholder2 = st.empty()

thumbnail_placeholder = st.empty()
summary_placeholder1 = st.empty()
summary_placeholder2 = st.empty()
working = True

if video_url:
    working = True
    # Call get_summary() and get_info() only if the video_url has changed
    if st.session_state.previous_video_url != video_url:
        try:
            st.session_state.video_title, st.session_state.channel_name, thumbnail_url, info2send = get_info(video_url)
            working = True
        except Exception as e:
            video_info_placeholder1.error("Incorrect Video Link")
            video_url = ""  # Reset the video_url to prevent further processing
            working = False
            print(e)

        if working:
            response = requests.get(thumbnail_url)
            st.session_state.thumbnail = Image.open(io.BytesIO(response.content))
            print("Done Thumbnail")
        else:
            print("Error", 1)
    if working:
        # Update video information, thumbnail placeholders
        video_info_placeholder1.subheader(st.session_state.video_title)
        video_info_placeholder2.write(f"By {st.session_state.channel_name}")
        thumbnail_placeholder.image(st.session_state.thumbnail)
        summary_placeholder1.subheader("Summary:")
        summary_placeholder2.write(f"<p style='font-size: 18px;'>Loading Summary</p>", unsafe_allow_html=True)


        if st.session_state.previous_video_url != video_url:
            try:
                st.session_state.summary, st.session_state.message_history = get_summary(info2send)
            except:
                summary_placeholder2.error("Video length too long")
                

            # Update the previous_video_url in session_state
            st.session_state.previous_video_url = video_url

        # Update video information, thumbnail placeholders
        video_info_placeholder1.subheader(str(st.session_state.video_title))
        video_info_placeholder2.write(f"By {st.session_state.channel_name}")
        thumbnail_placeholder.image(st.session_state.thumbnail)
        summary_placeholder1.subheader("Summary:")

        # Check if the summary is available and display it
        if st.session_state.summary:
            summary_placeholder1.subheader("Summary:")
            summary_placeholder2.write(f"<p style='font-size: 20px;'>{st.session_state.summary}</p>", unsafe_allow_html=True)

        st.markdown("""---""")
        st.subheader("Ask something about the Video:")
        # Create a placeholder for chat history
        chat_history_placeholder = st.empty()

        # Create a placeholder for user input
        user_input_placeholder = st.empty()

        user_message = user_input_placeholder.text_input("Ask a Question")

        if user_message:
            bot_response, st.session_state.message_history = get_response(user_message, st.session_state.message_history)
            chat_history.append({"name": "Summarizer", "message": bot_response})

            # Update the chat history
            with chat_history_placeholder:
                st.write("\n")
                for chat in chat_history:
                    print((f"{chat['name']}: {chat['message']}"))
                    st.write(f"{chat['name']}: {chat['message']}")

    else:
        print("Error", 2)