import streamlit as st
from reddit_media_downloader_core import UserDownload


st.header("Reddit User Media Downloader")


username = st.text_input("Username: ")
# post_type = st.selectbox("Media Type: ", ["Pictures", "Comments"])
subreddit = st.text_input("Subreddit Restriction: ")
post_limit = st.number_input("Post Limit: ")
start_date = st.date_input("Start Date: ")
end_date = st.date_input("End Date: ")


if st.button("Download User Media"):
    new_download = UserDownload(
        username=username,
        subreddit=subreddit,
        post_limit=post_limit,
        start_date=start_date,
        end_date=end_date,
    )
    with st.spinner(
        text=f"Downloading and Deduplicating {username}'s posts between {start_date} and {end_date}"
    ):
        new_download.download()
        st.success("Done")
