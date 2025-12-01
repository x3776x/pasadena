// streaming-service/main.go
package main

import (
	"context"
	"log"
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"

	"app/app/proto"
	"app/app/server"

	"google.golang.org/grpc"
)

func main() {
	mongoURI := os.Getenv("MONGO_URI")
	if mongoURI == "" {
		// ejemplo para correr en docker-compose: mongodb://papu:Kavinsky@pasadena_mongo:27017/?authSource=admin
		mongoURI = "mongodb://papu:Kavinsky@pasadena_mongo:27017/?authSource=admin"
	}
	dbName := os.Getenv("MONGO_DB")
	if dbName == "" {
		dbName = "pasadena_db"
	}
	bucketName := os.Getenv("GRIDFS_BUCKET")
	if bucketName == "" {
		bucketName = "fs"
	}

	serv, err := server.NewStreamingServer(mongoURI, dbName, bucketName)
	if err != nil {
		log.Fatalf("failed to create streaming server: %v", err)
	}

	grpcServer := grpc.NewServer()
	proto.RegisterStreamingServiceServer(grpcServer, serv)

	lis, err := net.Listen("tcp", ":50052")
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	// graceful shutdown
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)

	go func() {
		log.Printf("🎵 streaming service listening on :50052")
		if err := grpcServer.Serve(lis); err != nil {
			log.Fatalf("grpc serve error: %v", err)
		}
	}()

	<-stop
	log.Printf("🛑 shutting down...")

	grpcServer.GracefulStop()
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := serv.Close(ctx); err != nil {
		log.Printf("error closing server: %v", err)
	}
}
