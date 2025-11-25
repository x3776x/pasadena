package server

import (
	"context"
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"

	"app/proto"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/gridfs"
)

type Server struct {
	proto.UnimplementedStreamingServiceServer
	DB *mongo.Database
}

// Constructor
func NewStreamingServer(db *mongo.Database) *Server {
	return &Server{DB: db}
}

func (s *Server) StreamSong(req *proto.StreamRequest, stream proto.StreamingService_StreamSongServer) error {
	if s.DB == nil {
		return stream.Send(&proto.StreamResponse{
			Chunk: []byte("MongoDB no conectado"),
		})
	}

	bucket, err := gridfs.NewBucket(s.DB)
	if err != nil {
		return err
	}

	var fileID interface{}
	cursor, err := s.DB.Collection("fs.files").Find(context.Background(), bson.M{"filename": req.SongId})
	if err != nil {
		return err
	}
	defer cursor.Close(context.Background())

	found := false
	for cursor.Next(context.Background()) {
		doc := make(map[string]interface{})
		if err := cursor.Decode(&doc); err != nil {
			return err
		}
		fileID = doc["_id"]
		found = true
		break
	}

	if !found {
		return stream.Send(&proto.StreamResponse{
			Chunk: []byte("Archivo no encontrado"),
		})
	}

	downloadStream, err := bucket.OpenDownloadStream(fileID)
	if err != nil {
		return err
	}
	defer downloadStream.Close()

	const chunkSize = 64 * 1024
	buf := make([]byte, chunkSize)

	for {
		n, err := downloadStream.Read(buf)
		if err != nil && err != io.EOF {
			return err
		}
		if n == 0 {
			break
		}

		if err := stream.Send(&proto.StreamResponse{Chunk: buf[:n]}); err != nil {
			return err
		}
	}

	log.Println("Streaming completado para song_id:", req.SongId)
	return nil
}
