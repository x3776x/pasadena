import pytest
from unittest.mock import patch, AsyncMock
from proto import metadata_pb2 as pb2

@pytest.mark.asyncio
@patch("app.metadata_service.postgres_db", new_callable=AsyncMock)
async def test_get_user_statistics(mock_db, service, fake_context):
    mock_db.side_effect = [
        [{"total_songs": 5}],   # total canciones
        [{"total_time": 300}],  # tiempo total
        [                       # top songs
            {"song_id": "s1", "title": "Song 1", "play_count": 3}
        ],
        [                       # top artists
            {"name": "Muse", "plays": 5}
        ],
        [                       # top genres
            {"name": "Rock", "plays": 5}
        ],
        [                       # last played
            {"song_id": "s1", "title": "Song 1", "last_play": "2025-01-01"}
        ]
    ]

    request = pb2.UserStatisticsRequest(user_id="u1")

    response = await service.GetUserStatistics(request, fake_context)

    assert response.totalSongs == 5
    assert response.totalTime == 300
    assert response.topSongs[0].title == "Song 1"
    assert response.topArtists[0].name == "Muse"
    assert response.topGenres[0].name == "Rock"
