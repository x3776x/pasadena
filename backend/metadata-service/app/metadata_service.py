import uuid
import grpc
from proto import metadata_pb2 as pb2
from proto import metadata_pb2_grpc as pb2_grpc
import sqlalchemy as sa
from PIL import Image
import io
import traceback

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
            try:
                song_table = Song.__table__
                while True:
                    song_id = str(uuid.uuid4())

                    query_check_song = (
                        sa.select(song_table.c.song_id)
                        .where(song_table.c.song_id == song_id)
                    )

                    existing_song = await postgres_db(query_check_song)

                    if not existing_song:
                        break  # song_id es único, continuar

                # ============================================================
                #                       ARTISTA
                # ============================================================
                artist_table = Artist.__table__
                query_artist = artist_table.select().where(artist_table.c.name == request.artist)
                artist_data = await postgres_db(query_artist)

                if artist_data:
                    # Puede ser dict o lista -> normalizamos
                    if isinstance(artist_data, list):
                        artist_id = artist_data[0]["id"]
                    else:
                        artist_id = artist_data["id"]
                else:
                    insert_artist = (
                        artist_table.insert()
                        .values(name=request.artist)
                        .returning(artist_table.c.id)
                    )
                    result = await postgres_db(insert_artist)
                    artist_id = result["id"] if isinstance(result, dict) else result


                # ============================================================
                #                       GÉNERO
                # ============================================================
                genre_table = Genre.__table__
                query_genre = genre_table.select().where(genre_table.c.name == request.genre)
                genre_data = await postgres_db(query_genre)

                if genre_data:
                    if isinstance(genre_data, list):
                        genre_id = genre_data[0]["id"]
                    else:
                        genre_id = genre_data["id"]
                else:
                    insert_genre = (
                        genre_table.insert()
                        .values(name=request.genre)
                        .returning(genre_table.c.id)
                    )
                    result = await postgres_db(insert_genre)
                    genre_id = result["id"] if isinstance(result, dict) else result


                # ============================================================
                #                       ÁLBUM
                # ============================================================
                album_table = Album.__table__

                # Buscar álbum con el mismo nombre Y EL MISMO ARTISTA (importante)
                query_album = album_table.select().where(
                    sa.and_(
                        album_table.c.name == request.album,
                        album_table.c.artist_id == artist_id
                    )
                )

                album_data = await postgres_db(query_album)

                if album_data:
                    # Normalizar resultado
                    if isinstance(album_data, list):
                        album_id = album_data[0]["id"]
                    else:
                        album_id = album_data["id"]
                else:
                    # Comprimir portada
                    compressed_cover = compress_image(request.album_cover)

                    insert_album = (
                        album_table.insert()
                        .values(
                            name=request.album,
                            release_date=request.year if request.year else None,
                            cover=compressed_cover,
                            artist_id=artist_id,
                        )
                        .returning(album_table.c.id)
                    )

                    result = await postgres_db(insert_album)

                    # Normalizar
                    if isinstance(result, list):
                        album_id = result[0]["id"]
                    elif isinstance(result, dict):
                        album_id = result["id"]
                    else:
                        album_id = result

        # ============================================================
                #                       CANCIÓN
                # ============================================================
                song_table = Song.__table__
                insert_song = (
                    song_table.insert()
                    .values(
                        song_id=song_id,
                        title=request.title,
                        duration=request.duration,
                        album_id=album_id,
                        genre_id=genre_id,
                        artist_id=artist_id,
                    )
                )
                await postgres_db(insert_song)


                # ============================================================
                #                       AUDIO (MONGO)
                # ============================================================
                save_audio(song_id, request.file_data)


                # ============================================================
                #                       RESPUESTA
                # ============================================================
                song_msg = pb2.Song(
                    song_id=song_id,
                    title=safe_str(request.title),
                    artist=safe_str(request.artist),
                    album=safe_str(request.album),
                    year=safe_str(request.year),
                    genre=safe_str(request.genre),
                    duration=safe_float(request.duration),
                    album_cover=safe_bytes_from_db(request.album_cover),
                    artist_id=artist_id,
                    album_id=album_id,
                    genre_id=genre_id,
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
                        genre_table.c.name.label("genre_name")
                    )
                    .select_from(
                        song_table
                        .outerjoin(artist_table, song_table.c.artist_id == artist_table.c.id)
                        .outerjoin(album_table, song_table.c.album_id == album_table.c.id)
                        .outerjoin(genre_table, song_table.c.genre_id == genre_table.c.id)
                    )
                    .where(
                        (song_table.c.title.ilike(q)) |
                        (artist_table.c.name.ilike(q)) |
                        (album_table.c.name.ilike(q)) |
                        (genre_table.c.name.ilike(q))
                    )
                )

                raw = await postgres_db(query)

                # normalizar
                if raw is None:
                    rows = []
                elif isinstance(raw, list):
                    rows = raw
                elif isinstance(raw, dict):
                    rows = [raw]
                else:
                    rows = []

                songs = []
                for row in rows:
                    songs.append(pb2.Song(
                        song_id=safe_str(row.get("song_id")),
                        title=safe_str(row.get("title")),
                        artist=safe_str(row.get("artist_name")),
                        album=safe_str(row.get("album_name")),
                        genre=safe_str(row.get("genre_name")),
                        duration=safe_float(row.get("duration")),
                        album_cover=b"",
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
                raw = await postgres_db(query)

                if raw is None:
                    rows = []
                elif isinstance(raw, list):
                    rows = raw
                elif isinstance(raw, dict):
                    rows = [raw]
                else:
                    rows = []

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

                raw = await postgres_db(query)

                if raw is None:
                    rows = []
                elif isinstance(raw, list):
                    rows = raw
                elif isinstance(raw, dict):
                    rows = [raw]
                else:
                    rows = []

                albums = []
                for row in rows:
                    albums.append(pb2.Album(
                        id=row["id"],
                        name=row["name"],
                        artist_id=row["artist_id"],
                        cover= b""
                        #row["cover"] if row["cover"] else
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
                raw = await postgres_db(query)

                if raw is None:
                    rows = []
                elif isinstance(raw, list):
                    rows = raw
                elif isinstance(raw, dict):
                    rows = [raw]
                else:
                    rows = []

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


        # -------------------------------------------------------------
        #                     UPDATE SONG
        # -------------------------------------------------------------
        # -------------------------------------------------------------
        #                     UPDATE SONG
        # -------------------------------------------------------------
        async def UpdateSong(self, request, context):
            """Modifica metadatos de una canción, incluyendo artista, álbum, portada y archivo de audio."""
            try:
                song_table = Song.__table__
                artist_table = Artist.__table__
                album_table = Album.__table__
                genre_table = Genre.__table__

                # ============================================================
                #               VALIDAR EXISTENCIA DE LA CANCIÓN
                # ============================================================
                query_song = song_table.select().where(song_table.c.song_id == request.song_id)
                song_data = await postgres_db(query_song)

                if not song_data:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details("Song not found")
                    return pb2.SongResponse()

                if isinstance(song_data, list):
                    song_data = song_data[0]

                # IDs actuales
                current_artist_id = song_data["artist_id"]
                current_album_id = song_data["album_id"]
                current_genre_id = song_data["genre_id"]

                final_artist_id = current_artist_id
                final_album_id = current_album_id
                final_genre_id = current_genre_id

                # ============================================================
                #                       ARTISTA
                # ============================================================
                if request.artist:
                    q_artist = artist_table.select().where(artist_table.c.name == request.artist)
                    artist_data = await postgres_db(q_artist)

                    if artist_data:
                        final_artist_id = artist_data[0]["id"] if isinstance(artist_data, list) else artist_data["id"]
                    else:
                        insert_artist = (
                            artist_table.insert()
                            .values(name=request.artist)
                            .returning(artist_table.c.id)
                        )
                        res = await postgres_db(insert_artist)
                        final_artist_id = res[0]["id"] if isinstance(res, list) else (res["id"] if isinstance(res, dict) else res)

                # ============================================================
                #                       GÉNERO
                # ============================================================
                if request.genre:
                    q_genre = genre_table.select().where(genre_table.c.name == request.genre)
                    genre_data = await postgres_db(q_genre)

                    if genre_data:
                        final_genre_id = genre_data[0]["id"] if isinstance(genre_data, list) else genre_data["id"]
                    else:
                        insert_genre = (
                            genre_table.insert()
                            .values(name=request.genre)
                            .returning(genre_table.c.id)
                        )
                        res = await postgres_db(insert_genre)
                        final_genre_id = res[0]["id"] if isinstance(res, list) else (res["id"] if isinstance(res, dict) else res)

                # ============================================================
                #                       ÁLBUM
                # ============================================================
                if request.album:
                    q_album = album_table.select().where(
                        sa.and_(
                            album_table.c.name == request.album,
                            album_table.c.artist_id == final_artist_id
                        )
                    )
                    album_data = await postgres_db(q_album)

                    if album_data:
                        final_album_id = album_data[0]["id"] if isinstance(album_data, list) else album_data["id"]
                    else:
                        compressed_cover = compress_image(request.album_cover) if request.album_cover else None
                        insert_album = (
                            album_table.insert()
                            .values(
                                name=request.album,
                                release_date=request.year if request.year else None,
                                cover=compressed_cover,
                                artist_id=final_artist_id
                            )
                            .returning(album_table.c.id)
                        )
                        res = await postgres_db(insert_album)
                        final_album_id = res[0]["id"] if isinstance(res, list) else (res["id"] if isinstance(res, dict) else res)

                # ============================================================
                #                       ACTUALIZAR CANCIÓN
                # ============================================================
                update_values = {}

                if request.title is not None:
                    update_values["title"] = request.title
                if request.duration is not None:
                    update_values["duration"] = request.duration

                # IDs actualizados
                update_values["artist_id"] = final_artist_id
                update_values["album_id"] = final_album_id
                update_values["genre_id"] = final_genre_id

                upd_song = song_table.update().values(**update_values).where(song_table.c.song_id == request.song_id)
                await postgres_db(upd_song)

                # ============================================================
                #              ACTUALIZAR ÁLBUM (AÑO Y PORTADA)
                # ============================================================
                if request.year:
                    upd_year = album_table.update().values(release_date=request.year).where(album_table.c.id == final_album_id)
                    await postgres_db(upd_year)

                if request.album_cover:
                    compressed_cover = compress_image(request.album_cover)
                    upd_cover = album_table.update().values(cover=compressed_cover).where(album_table.c.id == final_album_id)
                    await postgres_db(upd_cover)

                # ============================================================
                #                       ACTUALIZAR AUDIO
                # ============================================================
               # if request.file_data:
                #    delete_audio(request.song_id)
                   # save_audio(request.song_id, request.file_data)

                # ============================================================
                #                       RESPUESTA
                # ============================================================
                return pb2.SongResponse(
                    song=pb2.Song(
                        song_id=request.song_id,
                        title=request.title or song_data["title"],
                        artist=request.artist or "",
                        album=request.album or "",
                        year=request.year or "",
                        genre=request.genre or "",
                        duration=request.duration or song_data["duration"],
                        album_cover=b"",
                        artist_id=final_artist_id,
                        album_id=final_album_id,
                        genre_id=final_genre_id,
                    ),
                    message="Updated"
                )

            except Exception as e:
                traceback.print_exc()
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(str(e))
                return pb2.SongResponse()


def compress_image(image_bytes, max_size_kb=500):
            """Reduce el tamaño de una imagen sin perder mucha calidad."""
            if not image_bytes:
                return image_bytes

            try:
                img = Image.open(io.BytesIO(image_bytes))
                img = img.convert("RGB")  # quitar canales raros

                # Redimensionar si es muy grande (opcional pero recomendado)
                img.thumbnail((800, 800))

                quality = 85
                buffer = io.BytesIO()

                while True:
                    buffer.seek(0)
                    buffer = io.BytesIO()
                    img.save(buffer, format="JPEG", quality=quality, optimize=True)
                    size_kb = len(buffer.getvalue()) / 1024

                    if size_kb <= max_size_kb or quality <= 20:
                        break

                    quality -= 5

                return buffer.getvalue()

            except Exception:
                return image_bytes  # fallback
