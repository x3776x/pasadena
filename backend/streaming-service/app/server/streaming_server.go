// streaming-service/server/streaming_server.go
package server

import (
	"context"
	"fmt"
	"io"
	"log"
	"time"

	"app/app/proto" // ajusta el module path según tu proyecto
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/gridfs"
	"go.mongodb.org/mongo-driver/mongo/options"
	"go.mongodb.org/mongo-driver/mongo/readpref"
)

type StreamingServer struct {
	proto.UnimplementedStreamingServiceServer
	mongoClient *mongo.Client
	db          *mongo.Database
	bucket      *gridfs.Bucket
	bucketName  string
}

func NewStreamingServer(mongoURI, dbName, bucketName string) (*StreamingServer, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	clientOpts := options.Client().ApplyURI(mongoURI)
	client, err := mongo.Connect(ctx, clientOpts)
	if err != nil {
		return nil, fmt.Errorf("mongo connect: %w", err)
	}

	if err := client.Ping(ctx, readpref.Primary()); err != nil {
		return nil, fmt.Errorf("mongo ping: %w", err)
	}

	db := client.Database(dbName)
	bktOpts := options.GridFSBucket().SetName(bucketName)
	bucket, err := gridfs.NewBucket(db, bktOpts)
	if err != nil {
		return nil, fmt.Errorf("gridfs.NewBucket: %w", err)
	}

	return &StreamingServer{
		mongoClient: client,
		db:          db,
		bucket:      bucket,
		bucketName:  bucketName,
	}, nil
}

// StreamSong: streaming desde GridFS
func (s *StreamingServer) StreamSong(req *proto.StreamRequest, stream proto.StreamingService_StreamSongServer) error {
	songID := req.SongId
	log.Printf("🔄 StreamSong request: %s", songID)

	// Intentar abrir por filename == songID
	downloadStream, err := s.bucket.OpenDownloadStreamByName(songID)
	if err != nil {
		// Si no existe exactamente por nombre, buscar por prefijo en fs.files
		log.Printf("⚠️  OpenDownloadStreamByName failed for '%s': %v — buscando por prefijo", songID, err)
		fileDoc := s.db.Collection(s.bucketName + ".files")

		ctxFind, cancel := context.WithTimeout(stream.Context(), 5*time.Second)
		defer cancel()

		filter := bson.M{"filename": bson.M{"$regex": fmt.Sprintf("^%s", primitive.Regex{Pattern: songID, Options: ""})}}
		var doc bson.M
		errFind := fileDoc.FindOne(ctxFind, filter).Decode(&doc)
		if errFind != nil {
			log.Printf("❌ no encontrado en fs.files para %s: %v", songID, errFind)
			return fmt.Errorf("audio not found for songID: %s", songID)
		}

		// abrir por ObjectID encontrado
		idVal, ok := doc["_id"]
		if !ok {
			return fmt.Errorf("no _id in fs.files doc for %s", songID)
		}
		objID, ok := idVal.(primitive.ObjectID)
		if !ok {
			// si _id es string intenta convertir
			switch v := idVal.(type) {
			case string:
				oid, e2 := primitive.ObjectIDFromHex(v)
				if e2 != nil {
					return fmt.Errorf("invalid file id type for %s", songID)
				}
				objID = oid
			default:
				return fmt.Errorf("unsupported _id type for file: %T", idVal)
			}
		}

		downloadStream, err = s.bucket.OpenDownloadStream(objID)
		if err != nil {
			return fmt.Errorf("OpenDownloadStream by id failed: %w", err)
		}
	}
	defer func() {
		_ = downloadStream.Close()
	}()

	// Streaming por chunks
	const chunkSize = 64 * 1024 // 64KB (ajustable)
	buf := make([]byte, chunkSize)

	totalSent := 0
	for {
		// Si el cliente cancela, salir
		if stream.Context().Err() != nil {
			log.Printf("⛔ cliente canceló el stream para %s: %v", songID, stream.Context().Err())
			return stream.Context().Err()
		}

		n, err := downloadStream.Read(buf)
		if err != nil && err != io.EOF {
			return fmt.Errorf("error reading gridfs stream: %w", err)
		}
		if n > 0 {
			chunk := buf[:n]
			resp := &proto.StreamResponse{Chunk: chunk}
			if err := stream.Send(resp); err != nil {
				return fmt.Errorf("error sending chunk: %w", err)
			}
			totalSent += n
		}
		if err == io.EOF {
			break
		}
	}

	log.Printf("✅ Stream completed for %s. bytes sent=%d", songID, totalSent)
	return nil
}

// Close disconnects mongo client
func (s *StreamingServer) Close(ctx context.Context) error {
	if s.mongoClient == nil {
		return nil
	}
	return s.mongoClient.Disconnect(ctx)
}
