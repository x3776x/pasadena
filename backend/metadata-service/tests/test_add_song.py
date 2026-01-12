import pytest
from unittest.mock import patch, AsyncMock
from proto import metadata_pb2 as pb2

@pytest.mark.asyncio
@patch("app.metadata_service.save_audio")
@patch("app.metadata_service.postgres_db", new_callable=AsyncMock)
async def test_add_song_ok(mock_db, mock_save_audio, service, fake_context):
    # Orden REAL de llamadas en AddSong
    mock_db.side_effect = [
        None,                 # UUID no existe
        None,                 # artista no existe
        {"id": 1},            # insert artista
        None,                 # género no existe
        {"id": 2},            # insert género
        None,                 # álbum no existe
        {"id": 3},            # insert álbum
        None                  # insert canción
    ]

    request = pb2.AddSongRequest(
        title="Solo",
        artist="Muse",
        album="Absolution",
        genre="Rock",
        duration=120.0,
        year="2025",
        album_cover=b"img",
        file_data=b"audio"
    )

    response = await service.AddSong(request, fake_context)

    assert response.message == "Created"
    assert response.song.title == "Solo"
    assert response.song.artist_id == 1
    assert response.song.album_id == 3
    assert response.song.genre_id == 2
    mock_save_audio.assert_called_once()
