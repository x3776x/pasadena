// streaming-service/main.go
package main

import (
	"log"
	"net"
	"os"

	"app/app/proto"
	"app/app/server"

	"google.golang.org/grpc"
)

func main() {
	// Configuración desde variables de entorno
	musicDir := os.Getenv("MUSIC_DIR")
	if musicDir == "" {
		musicDir = "/data/music"
	}

	// Crear el servidor de streaming
	streamingServer := server.NewStreamingServer(musicDir)

	// Crear servidor gRPC
	grpcServer := grpc.NewServer()

	// Registrar el servicio
	proto.RegisterStreamingServiceServer(grpcServer, streamingServer)

	// Puerto del servicio
	port := ":50052"

	// Escuchar en el puerto
	listener, err := net.Listen("tcp", port)
	if err != nil {
		log.Fatalf("❌ Error al escuchar en el puerto %s: %v", port, err)
	}

	log.Printf("🎵 Servicio de streaming iniciado en el puerto %s", port)
	log.Printf("📁 Directorio de música: %s", musicDir)

	// Verificar contenido del directorio de música
	files, err := os.ReadDir(musicDir)
	if err != nil {
		log.Printf("⚠️  No se pudo leer el directorio de música: %v", err)
	} else {
		log.Printf("📚 Archivos de música disponibles: %d", len(files))
		for i, file := range files {
			if i < 10 { // Mostrar solo los primeros 10
				log.Printf("   - %s", file.Name())
			}
		}
		if len(files) > 10 {
			log.Printf("   ... y %d más", len(files)-10)
		}
	}

	// Iniciar el servidor
	log.Printf("🚀 Iniciando servidor gRPC...")
	if err := grpcServer.Serve(listener); err != nil {
		log.Fatalf("❌ Error al iniciar el servidor: %v", err)
	}
}
