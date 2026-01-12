import uuid
import grpc
from proto import metadata_pb2 as pb2
from proto import metadata_pb2_grpc as pb2_grpc
import sqlalchemy as sa
import traceback
from utils import normalize_all, normalize_one, compress_image
from models.mongo import save_audio, delete_audio
from models.song_model import Artist, Album, Song, Genre, UserStatistics
from utils import execute_db_query as postgres_db, safe_str, safe_float, safe_bytes_from_db, safe_int

class MetadataServiceServicer(pb2_grpc.MetadataServiceServicer):

        async def AddSong(self, request, context):
            try:
                song_table = Song.__table__
                artist_table = Artist.__table__
                album_table = Album.__table__
                genre_table = Genre.__table__

                while True:
                    song_id = str(uuid.uuid4())
                    exists = await postgres_db(
                        sa.select(song_table.c.song_id)
                        .where(song_table.c.song_id == song_id)
                    )
                    if not exists:
                        break

                q_artist = artist_table.select().where(artist_table.c.name == request.artist)
                artist_data = normalize_one(await postgres_db(q_artist))

                if artist_data:
                    artist_id = artist_data["id"]
                else:
                    res = normalize_one(await postgres_db(
                        artist_table.insert()
                        .values(name=request.artist)
                        .returning(artist_table.c.id)
                    ))
                    artist_id = res["id"]

                # ============================================================
                #                        GÉNERO
                # ============================================================
                q_genre = genre_table.select().where(genre_table.c.name == request.genre)
                genre_data = normalize_one(await postgres_db(q_genre))

                if genre_data:
                    genre_id = genre_data["id"]
                else:
                    res = normalize_one(await postgres_db(
                        genre_table.insert()
                        .values(name=request.genre)
                        .returning(genre_table.c.id)
                    ))
                    genre_id = res["id"]

                # ============================================================
                #                        ÁLBUM
                # ============================================================
                q_album = album_table.select().where(
                    sa.and_(
                        album_table.c.name == request.album,
                        album_table.c.artist_id == artist_id
                    )
                )
                album_data = normalize_one(await postgres_db(q_album))

                if album_data:
                    album_id = album_data["id"]
                else:
                    compressed_cover = compress_image(request.album_cover)
                    res = normalize_one(await postgres_db(
                        album_table.insert()
                        .values(
                            name=request.album,
                            release_date=request.year if request.year else None,
                            cover=compressed_cover,
                            artist_id=artist_id
                        )
                        .returning(album_table.c.id)
                    ))
                    album_id = res["id"]

                # ============================================================
                #                        CANCIÓN
                # ============================================================
                await postgres_db(
                    song_table.insert().values(
                        song_id=song_id,
                        title=request.title,
                        duration=request.duration,
                        album_id=album_id,
                        genre_id=genre_id,
                        artist_id=artist_id
                    )
                )

                # ============================================================
                #               AUDIO - LO MANDAMOS A MONGO
                # ============================================================
                save_audio(song_id, request.file_data)

                return pb2.SongResponse(
                    message="Created",
                    song=pb2.Song(
                        song_id=song_id,
                        title=request.title,
                        artist=request.artist,
                        album=request.album,
                        genre=request.genre,
                        year=request.year,
                        duration=request.duration,
                        album_cover=request.album_cover,
                        artist_id=artist_id,
                        album_id=album_id,
                        genre_id=genre_id
                    )
                )

            except Exception as e:
                traceback.print_exc()
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(str(e))
                return pb2.SongResponse()

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
                        genre_id=row["id"],
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
        async def UpdateSong(self, request, context):
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

        # -------------------------------------------------------------
        #                     GET ALBUM BY ID (FULL)
        # -------------------------------------------------------------
        async def GetAlbumById(self, request, context):
            """Retorna un álbum y todas sus canciones asociadas."""
            try:
                album_table = Album.__table__
                song_table = Song.__table__
                artist_table = Artist.__table__
                genre_table = Genre.__table__

                # ============================
                #   Obtener datos del álbum
                # ============================
                q_album = (
                    sa.select(
                        album_table.c.id,
                        album_table.c.name,
                        album_table.c.release_date,
                        album_table.c.cover,
                        artist_table.c.id.label("artist_id"),
                        artist_table.c.name.label("artist_name")
                    )
                    .select_from(album_table.join(artist_table, album_table.c.artist_id == artist_table.c.id))
                    .where(album_table.c.id == request.id)
                )

                album_raw = normalize_one(await postgres_db(q_album))
                if not album_raw:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details("Album not found")
                    return pb2.GetAlbumByIdResponse()

                # ============================
                #   Obtener canciones del álbum
                # ============================
                q_songs = (
                    sa.select(
                        song_table.c.song_id,
                        song_table.c.title,
                        song_table.c.duration,
                        artist_table.c.name.label("artist_name"),
                        genre_table.c.name.label("genre_name"),
                        song_table.c.artist_id,
                        song_table.c.album_id,
                        song_table.c.genre_id
                    )
                    .select_from(
                        song_table
                        .join(artist_table, song_table.c.artist_id == artist_table.c.id)
                        .join(genre_table, song_table.c.genre_id == genre_table.c.id)
                    )
                    .where(song_table.c.album_id == request.id)
                )

                raw_songs = normalize_all(await postgres_db(q_songs))

                songs = []
                for row in raw_songs:
                    songs.append(pb2.AlbumSong(
                        song_id=safe_str(row.get("song_id")),
                        title=safe_str(row.get("title")),
                        artist=safe_str(row.get("artist_name")),
                        genre=safe_str(row.get("genre_name")),
                        duration=safe_float(row.get("duration")),
                        artist_id=safe_int(row.get("artist_id")),
                        genre_id=safe_int(row.get("genre_id"))
                    ))

                # ============================
                #        Armar respuesta
                # ============================
                album_msg = pb2.AlbumFull(
                    id=album_raw["id"],
                    name=album_raw["name"],
                    artist_id=album_raw["artist_id"],
                    artist_name=album_raw["artist_name"],
                    cover=album_raw["cover"] if album_raw["cover"] else b"",
                    release_date=str(album_raw["release_date"]) if album_raw["release_date"] else "",
                    songs=songs
                )

                return pb2.GetAlbumByIdResponse(album=album_msg)

            except Exception as e:
                traceback.print_exc()
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(str(e))
                return pb2.GetAlbumByIdResponse()

        # -------------------------------------------------------------
        # REGISTER USER PLAY
        # -------------------------------------------------------------
        async def RegisterUserPlay(self, request, context):
            try:
                stats_table = UserStatistics.__table__  # tu tabla user_statistics
                song_table = Song.__table__

                # ============================================================
                #       VERIFICAR SI YA HAY REGISTRO DEL USUARIO + CANCIÓN
                # ============================================================
                q_check = stats_table.select().where(
                    sa.and_(
                        stats_table.c.user_id == request.user_id,
                        stats_table.c.song_id == request.song_id
                    )
                )
                existing = normalize_one(await postgres_db(q_check))

                if existing:
                    # ========================================================
                    #      ACTUALIZAR play_count y last_play
                    # ========================================================
                    await postgres_db(
                        stats_table.update()
                        .where(
                            sa.and_(
                                stats_table.c.user_id == request.user_id,
                                stats_table.c.song_id == request.song_id
                            )
                        )
                        .values(
                            play_count=stats_table.c.play_count + 1,
                            last_play=sa.func.now(),
                            total_time=stats_table.c.total_time + float(request.seconds)  # <-- aquí también
                        ).returning(stats_table.c.id)
                    )
                else:
                    # ========================================================
                    #      CREAR NUEVO REGISTRO
                    # ========================================================
                    await postgres_db(
                        stats_table.insert().values(
                            user_id=request.user_id,
                            song_id=request.song_id,
                            play_count=1,
                            total_time=float(request.seconds),
                            last_play=sa.func.now()
                        )
                    )
                # ============================================================
                #      RETORNAR RESPUESTA
                # ============================================================
                return pb2.UserPlayResponse(
                    success = True
                )

            except Exception as e:
                traceback.print_exc()
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(str(e))
                return pb2.UserPlayResponse()

        async def GetSongById(self, request, context):
            try:
                song_id = request.song_id
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
                    .where(song_table.c.song_id == song_id)
                )

                raw = await postgres_db(query)

                # Normalización para evitar errores
                if raw is None:
                    rows = []
                elif isinstance(raw, list):
                    rows = raw
                elif isinstance(raw, dict):
                    rows = [raw]
                else:
                    rows = []

                if not rows:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details("Song not found")
                    return pb2.GetSongByIdResponse(song=None)

                row = rows[0]

                song = pb2.Song(
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
                )

                return pb2.GetSongByIdResponse(song=song)

            except Exception as e:
                print("ERROR IN GetSongById:", e)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(str(e))
                return pb2.GetSongByIdResponse(song=None)

        # -------------------------------------------------------------
        # GET USER STATISTICS
        # -------------------------------------------------------------
        async def GetUserStatistics(self, request, context):
            try:
                user_id = request.user_id
                stats_table = UserStatistics.__table__
                song_table = Song.__table__
                artist_table = Artist.__table__
                genre_table = Genre.__table__

                # TOTAL DE CANCIONES REPRODUCIDAS
                total_songs_query = sa.select(sa.func.sum(stats_table.c.play_count).label("total_songs")).where(
                    stats_table.c.user_id == user_id
                )
                total_songs_res = await postgres_db(total_songs_query)
                total_songs = total_songs_res[0]["total_songs"] if total_songs_res and total_songs_res[0]["total_songs"] else 0

                # TIEMPO TOTAL ESCUCHADO
                total_time_query = sa.select(sa.func.sum(stats_table.c.total_time).label("total_time")).where(
                    stats_table.c.user_id == user_id
                )
                total_time_res = await postgres_db(total_time_query)
                total_time = total_time_res[0]["total_time"] if total_time_res and total_time_res[0]["total_time"] else 0

                # TOP 5 CANCIONES
                top_songs_query = (
                    sa.select(
                        stats_table.c.song_id,
                        song_table.c.title,
                        stats_table.c.play_count
                    )
                    .select_from(stats_table.join(song_table, stats_table.c.song_id == song_table.c.song_id))
                    .where(stats_table.c.user_id == user_id)
                    .order_by(stats_table.c.play_count.desc())
                    .limit(5)
                )
                top_songs_res = await postgres_db(top_songs_query)

                # TOP ARTISTAS
                top_artists_query = (
                    sa.select(
                        artist_table.c.name,
                        sa.func.sum(stats_table.c.play_count).label("plays")
                    )
                    .select_from(
                        stats_table
                        .join(song_table, stats_table.c.song_id == song_table.c.song_id)
                        .join(artist_table, song_table.c.artist_id == artist_table.c.id)
                    )
                    .where(stats_table.c.user_id == user_id)
                    .group_by(artist_table.c.name)
                    .order_by(sa.desc("plays"))
                    .limit(5)
                )
                top_artists_res = await postgres_db(top_artists_query)

                # TOP GÉNEROS
                top_genres_query = (
                    sa.select(
                        genre_table.c.name,
                        sa.func.sum(stats_table.c.play_count).label("plays")
                    )
                    .select_from(
                        stats_table
                        .join(song_table, stats_table.c.song_id == song_table.c.song_id)
                        .join(genre_table, song_table.c.genre_id == genre_table.c.id)
                    )
                    .where(stats_table.c.user_id == user_id)
                    .group_by(genre_table.c.name)
                    .order_by(sa.desc("plays"))
                    .limit(5)
                )
                top_genres_res = await postgres_db(top_genres_query)

                # ÚLTIMAS 5 CANCIONES ESCUCHADAS
                last_played_query = (
                    sa.select(
                        stats_table.c.song_id,
                        song_table.c.title,
                        stats_table.c.last_play
                    )
                    .select_from(stats_table.join(song_table, stats_table.c.song_id == song_table.c.song_id))
                    .where(stats_table.c.user_id == user_id)
                    .order_by(stats_table.c.last_play.desc())
                    .limit(5)
                )
                last_played_res = await postgres_db(last_played_query)

                return pb2.UserStatisticsResponse(
                    totalSongs=int(total_songs),
                    totalTime=float(total_time),
                    topSongs=[pb2.TopSong(song_id=row["song_id"], title=row["title"], play_count=row["play_count"]) for row in top_songs_res],
                    topArtists=[pb2.TopArtist(name=row["name"], play_count=row["plays"]) for row in top_artists_res],
                    topGenres=[pb2.TopGenre(name=row["name"], play_count=row["plays"]) for row in top_genres_res],
                    lastPlayed=[pb2.LastPlayed(song_id=row["song_id"], title=row["title"], last_play=str(row["last_play"])) for row in last_played_res]
                )

            except Exception as e:
                print(" Error GetUserStatistics:", e)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(str(e))
                return pb2.UserStatisticsResponse()
        # -------------------------------------------------------------
        #              GET LATEST ALBUMS (HOME)
        # -------------------------------------------------------------
        async def GetLatestAlbums(self, request, context):
            try:
                album_table = Album.__table__
                artist_table = Artist.__table__

                # ============================
                #   Normalizar límite
                # ============================
                requested_limit = request.limit
                limit = requested_limit if requested_limit and requested_limit > 0 else 10

                query = (
                    sa.select(
                        album_table.c.id,
                        album_table.c.name,
                        album_table.c.cover,
                        album_table.c.artist_id
                    )
                    .order_by(album_table.c.id.desc())
                    .limit(limit)
                )

                raw = await postgres_db(query)
                rows = normalize_all(raw)

                albums = [
                    pb2.Album(
                        id=safe_int(row.get("id")),
                        name=safe_str(row.get("name")),
                        artist_id=safe_int(row.get("artist_id")),
                        cover=row.get("cover") if row.get("cover") else b""
                    )
                    for row in rows
                ]
                return pb2.LatestAlbumsResponse(albums=albums)

            except Exception as e:
                traceback.print_exc()
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(str(e))
                return pb2.LatestAlbumsResponse()

        # -------------------------------------------------------------
        #              GET LATEST SONGS (HOME) – SIN MODIFICAR BD
        # -------------------------------------------------------------
        async def GetLatestSongs(self, request, context):
            try:
                song_table = Song.__table__
                artist_table = Artist.__table__
                album_table = Album.__table__
                genre_table = Genre.__table__

                limit = request.limit if request.limit and request.limit > 0 else 5

                query = (
                    sa.select(
                        song_table.c.song_id,
                        song_table.c.title,
                        song_table.c.duration,
                        song_table.c.artist_id,
                        song_table.c.album_id,
                        song_table.c.genre_id,
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
                    # 👇 truco clave SIN created_at
                    .order_by(
                        album_table.c.id.desc().nullslast(),
                        song_table.c.song_id.desc()
                    )
                    .limit(limit)
                )

                raw = await postgres_db(query)
                rows = normalize_all(raw)

                songs = [
                    pb2.Song(
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
                    )
                    for row in rows
                ]

                return pb2.LatestSongsResponse(songs=songs)

            except Exception as e:
                traceback.print_exc()
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(str(e))
                return pb2.LatestSongsResponse()

