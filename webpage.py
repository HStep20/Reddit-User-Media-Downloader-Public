import streamlit as st
from reddit_media_downloader_core import UserDownload


st.set_page_config(
    page_title="Machine Learning Scraper", page_icon=":shark:", menu_items=None
)
st.header("Reddit User Media Downloader")

with st.form(key="user_download_data"):
    username = st.text_input("Username: ", help="required")
    # post_type = st.selectbox("Media Type: ", ["Pictures", "Comments"])
    subreddit = st.text_input("Subreddit Restriction: ")
    post_limit = st.number_input("Post Limit: ", step=1, format="%d")
    start_date = st.date_input("Start Date: ", help="required")
    end_date = st.date_input("End Date: ", help="required")
    if st.form_submit_button("Download User Media"):
        print(username)
        print(subreddit)
        print(post_limit)
        print(start_date)
        print(end_date)
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
            try:
                new_download.download()
                st.success("Done")
            except KeyError as e:
                st.error(e)
