FROM python:3.8

COPY . /

RUN apt-get update && apt-get install -y git libsm6 libxext6 ffmpeg libfontconfig1 libxrender1 libgl1-mesa-glx
RUN git --version
RUN pip install -r requirements.txt

VOLUME /output

ENTRYPOINT ["python3", "reddit-media-downloader.py"]