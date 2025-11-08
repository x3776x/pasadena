// streaming-service/app/server/streaming_server.go
package server

import (
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"

	"app/app/proto"
)

type StreamingServer struct {
	proto.UnimplementedStreamingServiceServer
	musicDirectory string
}

func NewStreamingServer(musicDir string) *StreamingServer {
	return &StreamingServer{
		musicDirectory: musicDir,
	}
}

func (s *StreamingServer) StreamSong(req *proto.StreamRequest, stream proto.StreamingService_StreamSongServer) error {
	songID := req.SongId
	log.Printf("🔄 Iniciando streaming para canción: %s", songID)

	// 1. Buscar el archivo de audio
	audioPath, err := s.findAudioFile(songID)
	if err != nil {
		return fmt.Errorf("❌ error buscando archivo de audio: %v", err)
	}

	log.Printf("📁 Archivo encontrado: %s", audioPath)

	// 2. Abrir el archivo
	file, err := os.Open(audioPath)
	if err != nil {
		return fmt.Errorf("❌ error abriendo archivo: %v", err)
	}
	defer file.Close()

	// 3. Obtener información del archivo para logging
	fileInfo, err := file.Stat()
	if err != nil {
		return fmt.Errorf("❌ error obteniendo info del archivo: %v", err)
	}

	log.Printf("📊 Tamaño del archivo: %d bytes", fileInfo.Size())

	// 4. Stream por chunks
	chunkSize := 64 * 1024 // 64KB
	buffer := make([]byte, chunkSize)
	totalSent := 0

	for {
		// Leer chunk del archivo
		n, err := file.Read(buffer)
		if err == io.EOF {
			log.Printf("✅ Streaming completado para %s. Total enviado: %d bytes", songID, totalSent)
			break
		}
		if err != nil {
			return fmt.Errorf("❌ error leyendo archivo: %v", err)
		}

		// Crear respuesta
		response := &proto.StreamResponse{
			Chunk: buffer[:n],
		}

		// Enviar chunk al cliente
		if err := stream.Send(response); err != nil {
			return fmt.Errorf("❌ error enviando chunk: %v", err)
		}

		totalSent += n

		// Log cada 10 chunks para no saturar los logs
		if (totalSent/chunkSize)%10 == 0 {
			log.Printf("📤 Enviado %d bytes para %s", totalSent, songID)
		}
	}

	log.Printf("🎉 Streaming finalizado exitosamente para %s", songID)
	return nil
}

// findAudioFile busca el archivo de audio por songID
func (s *StreamingServer) findAudioFile(songID string) (string, error) {
	// Posibles extensiones de audio
	extensions := []string{".mp3", ".wav", ".flac", ".m4a", ".ogg"}

	for _, ext := range extensions {
		audioPath := filepath.Join(s.musicDirectory, songID+ext)
		if _, err := os.Stat(audioPath); err == nil {
			return audioPath, nil
		}
	}

	// Si no encuentra con extensiones, buscar cualquier archivo que comience con el songID
	files, err := os.ReadDir(s.musicDirectory)
	if err != nil {
		return "", fmt.Errorf("error leyendo directorio de música: %v", err)
	}

	for _, file := range files {
		if !file.IsDir() {
			filename := file.Name()
			// Verificar si el archivo comienza con el songID
			if len(filename) >= len(songID) && filename[:len(songID)] == songID {
				return filepath.Join(s.musicDirectory, filename), nil
			}
		}
	}

	return "", fmt.Errorf("archivo de audio no encontrado para songID: %s en directorio: %s", songID, s.musicDirectory)
}
