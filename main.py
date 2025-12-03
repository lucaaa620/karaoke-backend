from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uuid, shutil, json, os, requests
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
AUDIO_DIR = UPLOAD_DIR / "audio"
THUMB_DIR = UPLOAD_DIR / "thumbs"
SONGS_FILE = BASE_DIR / "songs.json"

ADMIN_TOKEN = "myadmin123"

# Create folders
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
THUMB_DIR.mkdir(parents=True, exist_ok=True)
if not SONGS_FILE.exists():
    SONGS_FILE.write_text("[]", encoding="utf-8")

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static
app.mount("/static", StaticFiles(directory=str(UPLOAD_DIR)), name="static")

def load_songs():
    try:
        return json.loads(SONGS_FILE.read_text())
    except:
        return []

def save_songs(data):
    SONGS_FILE.write_text(json.dumps(data, indent=2))

async def save_file(file, dest):
    with open(dest, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    file.file.close()

def abs_url(request, path: str):
    return str(request.base_url).rstrip("/") + path

@app.get("/")
def home():
    return {"status": "backend running"}

# =======================================================
# 🔥 NEW FINAL PERMANENT SONGS API (GitHub Storage)
# =======================================================

GITHUB_JSON_URL = "https://raw.githubusercontent.com/lucaaa620/karaoke-storage/main/songs.json"

@app.get("/songs")
def get_songs():
    try:
        data = requests.get(GITHUB_JSON_URL, timeout=5).json()
        return data
    except:
        return {"songs": []}


# =======================================================
# 🔥 ADMIN UPLOAD (OPTIONAL - local)
# =======================================================

@app.post("/admin/upload")
async def upload(
    request: Request,
    token: str = Form(...),
    title: str = Form(...),
    artist: str = Form(""),
    audio: UploadFile = File(...),
    lyrics_file: UploadFile = File(None),
    thumb: UploadFile = File(None)
):
    if token != ADMIN_TOKEN:
        raise HTTPException(401, "Invalid token")

    song_id = str(uuid.uuid4())

    # audio
    a_ext = Path(audio.filename).suffix
    a_name = f"{song_id}{a_ext}"
    a_path = AUDIO_DIR / a_name
    await save_file(audio, a_path)

    # thumb
    t_url = ""
    if thumb:
        t_ext = Path(thumb.filename).suffix
        t_name = f"{song_id}{t_ext}"
        t_path = THUMB_DIR / t_name
        await save_file(thumb, t_path)
        t_url = f"/static/thumbs/{t_name}"

    # lyrics
    l_url = ""
    if lyrics_file:
        l_name = f"{song_id}.lrc"
        l_path = AUDIO_DIR / l_name
        await save_file(lyrics_file, l_path)
        l_url = f"/static/audio/{l_name}"

    entry = {
        "id": song_id,
        "title": title,
        "artist": artist,
        "audioUrl": f"/static/audio/{a_name}",
        "thumbUrl": t_url,
        "lyricsLrc": l_url
    }

    db = load_songs()
    db.append(entry)
    save_songs(db)

    entry["audioUrl"] = abs_url(request, entry["audioUrl"])
    if t_url:
        entry["thumbUrl"] = abs_url(request, entry["thumbUrl"])
    if l_url:
        entry["lyricsLrc"] = abs_url(request, entry["lyricsLrc"])

    return {"ok": True, "song": entry}


# =======================================================
# 🔥 DELETE SONG LOCAL (OPTIONAL)
# =======================================================

@app.post("/admin/delete/{song_id}")
def delete(song_id: str, token: str = Form(...)):
    if token != ADMIN_TOKEN:
        raise HTTPException(401, "Invalid token")
    db = load_songs()
    db = [s for s in db if s["id"] != song_id]
    save_songs(db)
    return {"ok": True}
