from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uuid, json, shutil, logging, os
from pathlib import Path

# =======================
# DIRECTORIES
# =======================
BASE = Path(__file__).resolve().parent
UPLOAD = BASE / "uploads"
AUDIO = UPLOAD / "audio"
THUMBS = UPLOAD / "thumbs"
SONGS_JSON = BASE / "songs.json"

AUDIO.mkdir(parents=True, exist_ok=True)
THUMBS.mkdir(parents=True, exist_ok=True)
if not SONGS_JSON.exists():
    SONGS_JSON.write_text("[]", encoding="utf-8")

# =======================
# CONSTANTS
# =======================
ADMIN_TOKEN = "myadmin123"   # FIXED TOKEN
MAX_SIZE = 50 * 1024 * 1024  # 50 MB

# =======================
# APP + CORS
# =======================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # FULL OPEN
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(UPLOAD)), name="static")


# =======================
# HELPERS
# =======================
def load_songs():
    return json.loads(SONGS_JSON.read_text())

def save_songs(data):
    SONGS_JSON.write_text(json.dumps(data, indent=2))


async def save_file(upload: UploadFile, dest: Path):
    with dest.open("wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)
    upload.file.close()


def abs_url(req: Request, path: str):
    return str(req.base_url).rstrip("/") + path


# =======================
# ROUTES
# =======================
@app.get("/")
def home():
    return {"status": "Backend OK"}

@app.get("/songs")
def songs():
    return {"songs": load_songs()}


@app.post("/admin/upload")
async def upload(
    request: Request,
    token: str = Form(...),
    title: str = Form(...),
    artist: str = Form(""),
    audio: UploadFile = File(...),
    lyrics_file: UploadFile = File(None),
    thumb: UploadFile = File(None),
):

    if token != ADMIN_TOKEN:
        raise HTTPException(401, "Invalid token")

    s_id = str(uuid.uuid4())

    # AUDIO SAVE
    a_ext = Path(audio.filename).suffix
    a_name = f"{s_id}{a_ext}"
    a_path = AUDIO / a_name
    await save_file(audio, a_path)

    # THUMB
    thumb_url = ""
    if thumb:
        t_ext = Path(thumb.filename).suffix
        t_name = f"{s_id}{t_ext}"
        t_path = THUMBS / t_name
        await save_file(thumb, t_path)
        thumb_url = f"/static/thumbs/{t_name}"

    # LRC
    lrc_url = ""
    if lyrics_file:
        l_name = f"{s_id}.lrc"
        l_path = AUDIO / l_name
        await save_file(lyrics_file, l_path)
        lrc_url = f"/static/audio/{l_name}"

    new = {
        "id": s_id,
        "title": title,
        "artist": artist,
        "audioUrl": f"/static/audio/{a_name}",
        "thumbUrl": thumb_url,
        "lyricsLrc": lrc_url
    }

    data = load_songs()
    data.append(new)
    save_songs(data)

    new["audioUrl"] = abs_url(request, new["audioUrl"])
    if thumb_url:
        new["thumbUrl"] = abs_url(request, thumb_url)
    if lrc_url:
        new["lyricsLrc"] = abs_url(request, lrc_url)

    return {"ok": True, "song": new}


@app.post("/admin/delete/{song_id}")
def delete(song_id: str, token: str = Form(...)):
    if token != ADMIN_TOKEN:
        raise HTTPException(401, "Invalid token")

    data = load_songs()
    data = [s for s in data if s["id"] != song_id]
    save_songs(data)

    return {"ok": True}


@app.get("/health")
def health():
    return {"status": "ok"}
