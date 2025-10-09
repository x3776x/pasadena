package main

import (
	"log"
	"net"

	pb "pasadena/backend/streaming-service/app/proto"
	"pasadena/backend/streaming-service/app/server"

	"google.golang.org/grpc"
)

func main() {
	listener, err := net.Listen("tcp", ":50052")
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	grpcServer := grpc.NewServer()
	pb.RegisterStreamingServiceServer(grpcServer, server.NewStreamingServer())

	log.Println("Streaming Service running on port 50052")
	if err := grpcServer.Serve(listener); err != nil {
		log.Fatalf("Failed to serve: %v", err)
	}
}
