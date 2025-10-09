import uuid
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

def generate_song_id():
    return str(uuid.uuid4())

from mutagen.mp3 import MP3
from mutagen.id3 import ID3

def extract_metadata(file_path):
    try:
        audio = MP3(file_path, ID3=ID3)
        if not audio or not hasattr(audio, "info"):
            raise ValueError("Archivo sin metadatos o no válido")

        metadata = {
            "title": audio.get("TIT2").text[0] if audio.get("TIT2") else "no data",
            "artist": audio.get("TPE1").text[0] if audio.get("TPE1") else "no data",
            "album": audio.get("TALB").text[0] if audio.get("TALB") else "no data",
            "year": int(audio.get("TDRC").text[0]) if audio.get("TDRC") else 0,
            "genre": audio.get("TCON").text[0] if audio.get("TCON") else "no data",
            "duration": audio.info.length if hasattr(audio, "info") else 0.0,
            "album_cover": (
                audio.tags.get("APIC:").data if audio.tags and "APIC:" in audio.tags else b""
            )
        }

        return metadata

    except Exception as e:
        print(f"[WARN] No se pudieron extraer metadatos de {file_path}: {e}")
        return {
            "title": "no data",
            "artist": "no data",
            "album": "no data",
            "year": 0,
            "genre": "no data",
            "duration": 0.0,
            "album_cover": b""
        }
