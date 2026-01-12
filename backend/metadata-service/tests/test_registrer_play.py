import pytest
from unittest.mock import patch, AsyncMock
from proto import metadata_pb2 as pb2

@pytest.mark.asyncio
@patch("app.metadata_service.postgres_db", new_callable=AsyncMock)
async def test_register_user_play_new(mock_db, service, fake_context):
    mock_db.side_effect = [
        None,   # no existe registro previo
        None    # insert
    ]

    request = pb2.UserPlayRequest(
        user_id="u1",
        song_id="s1",
        seconds=30.0
    )

    response = await service.RegisterUserPlay(request, fake_context)

    assert response.success is True
    assert mock_db.call_count == 2


@pytest.mark.asyncio
@patch("app.metadata_service.postgres_db", new_callable=AsyncMock)
async def test_register_user_play_update(mock_db, service, fake_context):
    mock_db.side_effect = [
        {"id": 1, "play_count": 2},  # ya existe
        {"id": 1}                   # update
    ]

    request = pb2.UserPlayRequest(
        user_id="u1",
        song_id="s1",
        seconds=10.0
    )

    response = await service.RegisterUserPlay(request, fake_context)

    assert response.success is True
    assert mock_db.call_count == 2
