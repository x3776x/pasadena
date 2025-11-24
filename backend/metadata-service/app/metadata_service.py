import uuid


import grpc
import uuid
import grpc
from proto import metadata_pb2 as pb2
from proto import metadata_pb2_grpc as pb2_grpc
import sqlalchemy as sa

from models.mongo import save_audio, delete_audio
from models.song_model import Artist, Album, Song, Genre
from utils import execute_db_query as postgres_db, safe_str, safe_float, safe_bytes_from_db, safe_int

def ensure_list(value):
    return value if isinstance(value, list) else []


class MetadataServiceServicer(pb2_grpc.MetadataServiceServicer):



    # -------------------------------------------------------------
    #                       ADD SONG
    # -------------------------------------------------------------


    async def AddSong(self, request, context):
        """Guarda una canción con relaciones a artista, álbum y género."""
        try:
            song_id = str(uuid.uuid4())

            # ---------- ARTISTA ----------
            artist_table = Artist.__table__
            query_artist = artist_table.select().where(artist_table.c.name == request.artist)
            artist = await postgres_db(query_artist)

            if artist:
                artist_id = artist["id"]
            else:
                insert_artist = artist_table.insert().values(name=request.artist)
                artist_id = await postgres_db(insert_artist)

            # ---------- GÉNERO ----------
            genre_table = Genre.__table__
            query_genre = genre_table.select().where(genre_table.c.name == request.genre)
            genre = await postgres_db(query_genre)

            if genre:
                genre_id = genre["id"]
            else:
                insert_genre = genre_table.insert().values(name=request.genre)
                genre_id = await postgres_db(insert_genre)

            # ---------- ÁLBUM ----------
            album_table = Album.__table__
            query_album = album_table.select().where(album_table.c.name == request.album)
            album = await postgres_db(query_album)

            if album:
                album_id = album["id"]
            else:
                insert_album = album_table.insert().values(
                    name=request.album,
                    release_date=request.year if request.year else None,
                    cover=request.album_cover,
                    artist_id=artist_id
                )
                album_id = await postgres_db(insert_album)

            # ---------- CANCIÓN ----------
            song_table = Song.__table__
            insert_song = song_table.insert().values(
                song_id=song_id,
                title=request.title,
                duration=request.duration,
                album_id=(album_id),
                genre_id=genre_id,
                artist_id=artist_id
            )
            await postgres_db(insert_song)

            # ---------- AUDIO EN MONGO ----------
            save_audio(song_id, request.file_data)

            song_msg = pb2.Song(
                song_id=song_id,
                title=safe_str(request.title),
                artist=safe_str(request.artist),
                album=safe_str(request.album),
                year=safe_str(request.year),
                genre=safe_str(request.genre),
                duration=safe_float(request.duration),
                album_cover=safe_bytes_from_db(request.album_cover),
                artist_id=safe_int(artist_id),
                album_id=safe_int(album_id),
                genre_id=safe_int(genre_id)
            )
            return pb2.SongResponse(song=song_msg, message="Created")

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pb2.SongResponse()

    # -------------------------------------------------------------
    #                     GET SONG METADATA
    # -------------------------------------------------------------
    async def GetSongMetadata(self, request, context):
        """Obtiene los metadatos de una canción."""
        try:
            song_table = Song.__table__
            query = song_table.select().where(song_table.c.song_id == request.song_id)
            song = await postgres_db(query)

            if not song:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Song not found")
                return pb2.SongResponse()

            return pb2.SongResponse(
                song_id=song["song_id"],
                title=song["title"],
                duration=song["duration"],
                album=str(song["album_id"]),
                genre=str(song["genre_id"]),
                artist=str(song["artist_id"]),
                album_cover=b""
            )

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pb2.SongResponse()

    # -------------------------------------------------------------
    #                     GET SONG PATH
    # -------------------------------------------------------------
    async def GetSongPath(self, request, context):
        """Retorna una ruta virtual o ID (Mongo)."""
        return pb2.SongPathResponse(path=f"/songs/{request.song_id}")

    # -------------------------------------------------------------
    #                     DELETE SONG
    # -------------------------------------------------------------
    async def DeleteSong(self, request, context):
        """Elimina la canción de Postgres y Mongo."""
        try:
            song_table = Song.__table__
            query = song_table.delete().where(song_table.c.song_id == request.song_id)
            await postgres_db(query)

            delete_audio(request.song_id)

            return pb2.DeleteResponse(success=True, message="Deleted successfully")

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pb2.DeleteResponse(success=False, message=str(e))


    # -------------------------------------------------------------
    #                     SEARCH SONGS
    # -------------------------------------------------------------
    async def SearchSongs(self, request, context):
        try:
            q = f"%{request.query.lower()}%"

            song_table = Song.__table__
            artist_table = Artist.__table__
            album_table = Album.__table__
            genre_table = Genre.__table__

            query = (
                sa.select(
                    song_table.c.song_id,
                    song_table.c.title,
                    song_table.c.duration,
                    song_table.c.album_id,
                    song_table.c.genre_id,
                    song_table.c.artist_id,
                    artist_table.c.name.label("artist_name"),
                    album_table.c.name.label("album_name"),
                    genre_table.c.name.label("genre_name"),
                    album_table.c.cover
                )
                .select_from(
                    song_table
                    .join(artist_table, song_table.c.artist_id == artist_table.c.id)
                    .join(album_table, song_table.c.album_id == album_table.c.id)
                    .join(genre_table, song_table.c.genre_id == genre_table.c.id)
                )
                .where(
                    (song_table.c.title.ilike(q)) |
                    (artist_table.c.name.ilike(q)) |
                    (album_table.c.name.ilike(q)) |
                    (genre_table.c.name.ilike(q))
                )
            )

            rows = ensure_list(await postgres_db(query))

            songs = []
            for row in rows:
                songs.append(pb2.Song(
                    song_id=safe_str(row.get("song_id")),
                    title=safe_str(row.get("title")),
                    artist=safe_str(row.get("artist_name")),
                    album=safe_str(row.get("album_name")),
                    genre=safe_str(row.get("genre_name")),
                    duration=safe_float(row.get("duration")),
                    album_cover=safe_bytes_from_db(row.get("cover")),
                    artist_id=safe_int(row.get("artist_id")),
                    album_id=safe_int(row.get("album_id")),
                    genre_id=safe_int(row.get("genre_id"))
                ))

            return pb2.SearchSongsResponse(songs=songs)

        except Exception as e:
            print(e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pb2.SearchSongsResponse()


    # -------------------------------------------------------------
    #                     SEARCH ARTISTS
    # -------------------------------------------------------------
    async def SearchArtists(self, request, context):
        try:
            q = f"%{request.query.lower()}%"
            artist_table = Artist.__table__

            query = artist_table.select().where(artist_table.c.name.ilike(q))
            rows = ensure_list(await postgres_db(query))

            artists = [
                pb2.Artist(
                    artist_id=row["id"],
                    name=row["name"]
                )
                for row in rows
            ]

            return pb2.SearchArtistsResponse(artists=artists)

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pb2.SearchArtistsResponse()


    # -------------------------------------------------------------
    #                     SEARCH ALBUMS
    # -------------------------------------------------------------
    async def SearchAlbums(self, request, context):
        try:
            q = f"%{request.query.lower()}%"
            album_table = Album.__table__
            artist_table = Artist.__table__

            query = (
                album_table.join(artist_table, album_table.c.artist_id == artist_table.c.id)
                .select()
                .where(album_table.c.name.ilike(q))
            )

            rows = ensure_list(await postgres_db(query))

            albums = []
            for row in rows:
                albums.append(pb2.Album(
                    id=row["id"],
                    name=row["name"],
                    artist_id=row["artist_id"],
                    cover=row["cover"] if row["cover"] else b""
                ))

            return pb2.SearchAlbumsResponse(albums=albums)

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pb2.SearchAlbumsResponse()


    # -------------------------------------------------------------
    #                     SEARCH GENRES
    # -------------------------------------------------------------
    async def SearchGenres(self, request, context):
        try:
            q = f"%{request.query.lower()}%"
            genre_table = Genre.__table__

            query = genre_table.select().where(genre_table.c.name.ilike(q))
            rows = ensure_list(await postgres_db(query))

            genres = [
                pb2.Genre(
                    id=row["id"],
                    name=row["name"]
                )
                for row in rows
            ]

            return pb2.SearchGenresResponse(genres=genres)

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pb2.SearchGenresResponse()



