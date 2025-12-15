# Imagen base con Go 1.25 y Alpine
FROM golang:1.25-alpine

# Instalar protoc, git y bash
RUN apk add --no-cache protobuf git bash

# Crear carpeta de trabajo
WORKDIR /app

# Copiar dependencias primero (para cachear)
COPY go.mod go.sum ./
RUN go mod download

# Instalar plugins gRPC Go
RUN go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.32 \
    && go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@v1.3

# Asegurar que el PATH tenga los plugins
ENV PATH="$PATH:$(go env GOPATH)/bin"

# Copiar todo el código del servicio
COPY . .

# Generar los archivos .pb.go - CORREGIDO
RUN protoc --go_out=. --go_opt=paths=source_relative \
           --go-grpc_out=. --go-grpc_opt=paths=source_relative \
           app/proto/streaming.proto

RUN mkdir -p /data/music

# Exponer el puerto del servicio
EXPOSE 50052

# Comando por defecto
CMD ["go", "run", "main.go"]