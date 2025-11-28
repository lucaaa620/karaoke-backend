FROM ubuntu:22.04

RUN apt update && apt install -y build-essential git curl python3 python3-pip ffmpeg

# Install whisper.cpp
RUN git clone https://github.com/ggerganov/whisper.cpp.git && \
    cd whisper.cpp && make

# Copy backend files
WORKDIR /app
COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
