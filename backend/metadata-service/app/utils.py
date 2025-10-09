import uuid
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

def generate_song_id():
    return str(uuid.uuid4())

def extract_metadata(file_path):
    audio = MP3(file_path, ID3=ID3)
    metadata = {
        "title": audio.get("TIT2", "Unknown").text[0] if "TIT2" in audio else "Unknown",
        "artist": audio.get("TPE1", "Unknown").text[0] if "TPE1" in audio else "Unknown",
        "album": audio.get("TALB", "Unknown").text[0] if "TALB" in audio else "Unknown",
        "year": int(audio.get("TDRC", "0").text[0]) if "TDRC" in audio else 0,
        "genre": audio.get("TCON", "Unknown").text[0] if "TCON" in audio else "Unknown",
        "duration": audio.info.length,
        "album_cover": audio.tags.get("APIC:").data if "APIC:" in audio.tags else b""
    }
    return metadata
