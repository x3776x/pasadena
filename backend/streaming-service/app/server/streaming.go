package service

import (
	"io/ioutil"
	"log"

	pb "pasadena/backend/streaming-service/app/proto"
)

type StreamingServer struct {
	pb.UnimplementedStreamingServiceServer
}

func NewStreamingServer() *StreamingServer {
	return &StreamingServer{}
}

func (s *StreamingServer) StreamSong(req *pb.SongRequest, stream pb.StreamingService_StreamSongServer) error {
	filePath := "/data/music/" + req.SongId + ".mp3"
	data, err := ioutil.ReadFile(filePath)
	if err != nil {
		log.Println("Error leyendo archivo:", err)
		return err
	}

	chunkSize := 64 * 1024
	for start := 0; start < len(data); start += chunkSize {
		end := start + chunkSize
		if end > len(data) {
			end = len(data)
		}
		stream.Send(&pb.AudioChunk{Data: data[start:end]})
	}
	return nil
}
