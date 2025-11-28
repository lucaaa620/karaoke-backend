
FROM ubuntu:22.04

# Basic dependencies
RUN apt update && apt install -y \
    curl \
    unzip \
    ffmpeg \
    python3 \
    python3-pip

# Download prebuilt whisper.cpp binary (Linux version)
WORKDIR /whisper
RUN curl -L -o whisper.tar.gz https://huggingface.co/ggerganov/whisper.cpp/resolve/main/whisper-linux-x64.tar.gz && \
    tar -xvf whisper.tar.gz && \
    rm whisper.tar.gz

# App files
WORKDIR /app
COPY . .

RUN pip3 install --break-system-packages -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
