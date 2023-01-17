#!/usr/bin/env python3

"""
Download all the images and videos from a Reddit user account and automatically remove the duplicates 

Duplication removal algorithm using imagededup:

- Extract and save first frame from each video downloaded as a file and in a dict
- Use imagededup lib to get dictionary of all duplicates and originals in working folder
- Iterate through the dictionary
- If the value is in the dict of frames, delete the videos associated with the duplicate images as well as the duplicate images
- Then, delete the original frame
- If the value is not in the dict of frames, delete all the duplicates

#


# TODO: https://pypi.org/project/pmaw/ - MultiThreaded Pushift downloader
# TODO: Wait. All data before november 3rd, 2022 is not available via pushshift. Can be grabbed via reddit api though
# TODO: Convert to Loguru


"""

import requests, datetime
import yt_dlp
import json
import os, sys
import logging
import cv2
from imagededup.methods import PHash


class UserDownload:
    def __init__(self, username, subreddit, post_limit) -> None:
        self.username = username
        self.subreddit = subreddit
        self.post_limit = post_limit
        self.url_list = list()

    # pushshift helper function
    def get_posts(self, post_type, params, cb, limit=-1):
        # if a limit was specified by the user, set the size variable
        if limit != -1:
            if limit >= 100:
                # pushshift caps requests at 100 so if the limit is more than 100, we'll have to do multiple passes
                size = 100
            else:
                size = limit
        else:
            size = 100
        last = int(datetime.datetime.now().timestamp())
        got = 0
        while True:
            logging.info(f"Fetching posts made before {last}")
            req_params = {**params, "size": size, "before": last}
            req_headers = {"User-Agent": "Python requests - Redditstat.py"}
            res = requests.get(
                f"https://api.pushshift.io/reddit/{post_type}/search",
                params=req_params,
                headers=req_headers,
            )
            res.raise_for_status()
            data = res.json()["data"]
            cb(data)
            # stop fetching posts if we've there aren't any more or if we've hit the limit
            if len(data) < 100 or (limit != -1 and got >= limit):
                got += len(data)
                logging.info(f"Total of {got} posts fetched from u/{params['author']}")
                return
            else:
                last = data[-1]["created_utc"]
                got += 100

    def submission_callback(self, data):
        print(len(data))
        for post in data:
            self.process_submission(post)

    def process_submission(self, post):
        try:
            if not post["is_self"] and post["url"] not in self.url_list:
                if not post["is_video"] and "gif" not in post["url"]:
                    try:
                        res = requests.get(post["url"])
                        if res:
                            print("Downloading file")
                            print(post["url"])
                            target_file = os.path.join(
                                "output",
                                post["author"],
                                f"{datetime.datetime.now().strftime('%Y-%m-%dT%H%M%S')}-{post['url'].split('/')[-1]}",
                            )
                            with open(target_file, "wb+") as f:
                                f.write(res.content)
                                logging.info(
                                    f"Photo downloaded from {post['url']} and saved to {f.name}"
                                )
                    except Exception:
                        logging.error(
                            f"Exception downloading {post['url']}.  Skipping."
                        )

                else:
                    print("Downloading video")
                    target_file = os.path.join(
                        "output",
                        post["author"],
                        f"{datetime.datetime.now().strftime('%Y-%m-%dT%H%M%S')}-%(id)s.%(ext)s",
                    )
                    with yt_dlp.YoutubeDL(
                        {"outtmpl": target_file, "max_downloads": 1}
                    ) as ydl:
                        try:
                            info_dict = ydl.extract_info(post["url"], download=False)
                            fn = os.path.basename(ydl.prepare_filename(info_dict))
                            ydl.download([post["url"]])
                            logging.info(
                                f"Video downloaded from {post['url']} and saved to {fn}"
                            )
                        except (
                            yt_dlp.utils.DownloadError,
                            yt_dlp.utils.MaxDownloadsReached,
                        ):
                            print("Unable to download")
        except KeyError:
            print("What?")
        self.url_list.append(post["url"])

    def extractFirstFrame(self, cwd):
        logging.info("Beginning extraction of first frame from videos in the folder")
        videos = []
        # get all the video files downloaded
        for file in os.listdir(cwd):
            if file.endswith(".mp4"):
                videos.append(file)
        print(videos)
        video_images = {}
        # save the first frame from each video file
        for video in videos:
            vidcap = cv2.VideoCapture(os.path.join(cwd, video))
            success, image = vidcap.read()
            if success:
                cv2.imwrite(os.path.join(cwd, video + ".jpg"), image)
                video_images[os.path.basename(video) + ".jpg"] = os.path.basename(video)
            else:
                logging.error(f"Unable to extract first frame from {video}")
        return video_images

    def removeDuplicates(self, duplicates, video_frames, images_dir):
        for image in duplicates:
            if image in video_frames:
                # delete the duplicate image videos then the images
                if duplicates[image]:
                    for img in duplicates[image]:
                        try:
                            os.remove(os.path.join(images_dir, video_frames[img]))
                            os.remove(os.path.join(images_dir, img))
                            logging.info(
                                f"Duplicate video found. Deleting {video_frames[img]}"
                            )
                        except FileNotFoundError as e:
                            print(e)
                        duplicates[img] = []
                try:
                    # delete the jpeg created from the video frame
                    os.remove(os.path.join(images_dir, image))
                except FileNotFoundError as e:
                    print(e)
            else:
                # if it's not a video frame, delete the duplicate images
                if duplicates[image]:
                    for dup in duplicates[image]:
                        try:
                            os.remove(os.path.join(images_dir, dup))
                            logging.info(f"Duplicate picture found. Deleting {dup}")
                        except FileNotFoundError:
                            print(images_dir + dup + " not found")
                        duplicates[dup] = []

    def download(self):

        logging.info(
            f"\n\n{'-'*30}\nBeginning download of media from user u/{self.username}"
        )
        # get working directory
        cwd = os.getcwd()
        images_dir = os.path.join(cwd, "output", self.username)
        # create the folder for the user if it doesn't exist
        try:
            os.makedirs(images_dir)
            logging.info(f"Created folder for reddit user {self.username}")
        except OSError as e:
            logging.info(f"Folder already exists for reddit user {self.username}")
            print(e)
        if self.post_limit:
            self.get_posts(
                "submission",
                {
                    # **json.loads(args.pushshift_params),
                    "subreddit": self.subreddit,
                    "author": self.username,
                },
                self.submission_callback,
                int(self.post_limit),
            )
        else:
            self.get_posts(
                "submission",
                {
                    # **json.loads(args.pushshift_params),
                    "subreddit": self.subreddit,
                    "author": self.username,
                },
                self.submission_callback,
            )
        # get dict of video first frames
        video_frames = self.extractFirstFrame(images_dir)
        # get dict of all duplicates in directory
        logging.info("Beginning hashing function to create dict of duplicates")
        phasher = PHash()
        encodings = phasher.encode_images(image_dir=images_dir)
        duplicates = phasher.find_duplicates(encoding_map=encodings)
        print(video_frames)
        print("\n\n")
        print(duplicates)
        self.removeDuplicates(duplicates, video_frames, images_dir)


def setup_vars():
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        level="INFO",
        filename="execution.log",
    )
    # logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level='DEBUG', stream=sys.stdout)

    username = input("What User do you want to scrape? ")
    if input("Do you want to limit to a specific subreddit? Yes or No? ").lower() in [
        "y",
        "yes",
    ]:
        subreddit = input(
            f"What is the name of the subreddit you want to scrape {username}'s data from? "
        )
    else:
        subreddit = None
    # parser.add_argument(
    #    "--ydl-args", help="JSON-format youtube-dl options", default="{}"
    # )

    if input(
        "Do you want to only grab a certain number of posts? Yes or No? "
    ).lower() in ["y", "yes"]:
        while True:
            try:
                post_limit = int(input("Enter a number of recent posts to scrape: "))
                break
            except:
                print("Enter a number")
    else:
        post_limit = None
    # TODO: Add pushift date args
    # parser.add_argument(
    #    "--pushshift-params", help="JSON-formatted pushshift parameters", default="{}"
    # )
    # args = parser.parse_args()
    new_download = UserDownload(username, subreddit, post_limit)
    new_download.download()


if __name__ == "__main__":
    setup_vars()
    while True:
        if input(
            "Do you want to download another user's posts? Yes or No? "
        ).lower() in [
            "y",
            "yes",
        ]:
            setup_vars()
        else:
            print("Come back soon!")
            break
