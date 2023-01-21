FROM python:3.8

RUN mkdir build

WORKDIR /build

COPY . .

RUN apt-get update && apt-get install -y git libsm6 libxext6 ffmpeg libfontconfig1 libxrender1 libgl1-mesa-glx
RUN git --version
RUN pip install -r requirements.txt

WORKDIR /build/app

VOLUME /output

EXPOSE 4167

CMD python -m uvicorn form_routes:app --host 0.0.0.0 --port 4167