FROM python:3.10.4-slim

COPY . .

RUN apt-get update && apt-get install -y git libsm6 libxext6 ffmpeg libfontconfig1 libxrender1 libgl1-mesa-glx
RUN git --version

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

VOLUME /output

EXPOSE 8501

ENTRYPOINT [ "streamlit","run", "webpage.py"]