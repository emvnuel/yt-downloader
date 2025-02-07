FROM python:3-alpine
WORKDIR /service
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN apk add --no-cache ffmpeg
RUN apk add --no-cache nodejs
COPY . ./
EXPOSE 8080
ENTRYPOINT ["python3", "main.py"]