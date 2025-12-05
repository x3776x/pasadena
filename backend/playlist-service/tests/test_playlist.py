from fastapi import status
from sqlalchemy import text
import io

# ============================================
# playlist
# ============================================

def test_create_playlist(client):
    response = client.post(
        "/playlist",
        json={"name": "Rock Classics", "is_public": True},
        headers={"Authorization": "Bearer faketoken"}
    )
    print("Response JSON:", response.json())
    assert response.status_code == 200
    assert response.json()["name"] == "Rock Classics"


def test_delete_playlist(client):
    pl = client.post("/playlist", json={"name": "Pop", "is_public": True}).json()
    print("Create response:", pl)

    res = client.delete(f"/playlist/{pl['id']}")
    print("Delete response:", res.json()) 

    assert res.status_code == 200
    assert res.json()["message"] == "deleted"


def test_update_playlist(client):
    # Crear
    res = client.post("/playlist", json={"name": "Rock", "is_public": True})
    pl = res.json()

    # Actualizar
    update_res = client.put(
        f"/playlist/{pl['id']}",
        json={"name": "Rock Reloaded"},
    )

    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Rock Reloaded"


def test_get_all_playlists(client):
    response = client.get(
        "/playlist/all",
        headers={"Authorization": "Bearer faketoken"}
    )
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# ============================================
# likes
# ============================================

def test_like_playlist(client):
    pl = client.post("/playlist", json={"name": "Jazz", "is_public": True}).json()

    res = client.post(f"/playlist/{pl['id']}/like")

    assert res.status_code == 200


def test_unlike_playlist(client):
    pl = client.post("/playlist", json={"name": "Metal", "is_public": True}).json()

    client.post(f"/playlist/{pl['id']}/like")  # like primero

    res = client.post(f"/playlist/{pl['id']}/unlike")

    assert res.status_code == 200
    assert res.json()["message"] == "unliked"


# ============================================
# cancion_playlist
# ============================================

def test_add_song_to_playlist(client, db_session):

    # Insertar canción en metadata
    db_session.execute(text("INSERT INTO song (song_id) VALUES ('AAA')"))
    db_session.commit()

    pl = client.post("/playlist", json={"name": "EDM", "is_public": True}).json()

    res = client.post(
        f"/playlist/{pl['id']}/songs",
        json={"song_id": "AAA", "position": 1},
    )

    assert res.status_code == 200

def test_get_songs_in_playlist(client, db_session):

    # Insertar canción en metadata
    db_session.execute(text("INSERT INTO song (song_id) VALUES ('AAA')"))
    db_session.commit()

    pl = client.post("/playlist", json={"name": "Chill", "is_public": True}).json()

    client.post(f"/playlist/{pl['id']}/songs", json={"song_id": "AAA", "position": 1})

    res = client.get(f"/playlist/{pl['id']}/songs")

    assert res.status_code == 200
    assert len(res.json()) == 1

def test_remove_song_from_playlist(client, db_session):
    # Insertar canción en metadata
    db_session.execute(text("INSERT INTO song (song_id) VALUES ('AAA')"))
    db_session.commit()

    pl = client.post("/playlist", json={"name": "Trap", "is_public": True}).json()

    client.post(f"/playlist/{pl['id']}/songs", json={"song_id": "AAA", "position": 1})

    res = client.delete(f"/playlist/{pl['id']}/songs/AAA")

    assert res.status_code == 200



def test_clear_playlist(client):
    pl = client.post("/playlist", json={"name": "Workout", "is_public": True}).json()

    client.post(f"/playlist/{pl['id']}/songs", json={"song_id": "A", "position": 1})
    client.post(f"/playlist/{pl['id']}/songs", json={"song_id": "B", "position": 2})

    res = client.delete(f"/playlist/{pl['id']}/songs")

    assert res.status_code == 200
    assert "songs deleted" in res.json()["message"]

# ============================================
# cover 
# ============================================

def test_upload_cover(client):
    pl = client.post("/playlist", json={"name": "CoverTest", "is_public": True}).json()

    file_data = io.BytesIO(b"fake image content")

    res = client.post(
        f"/playlist/{pl['id']}/cover",
        files={"file": ("photo.png", file_data, "image/png")},
    )

    assert res.status_code == 200
    assert res.json()["playlist_cover"].endswith(".png")


