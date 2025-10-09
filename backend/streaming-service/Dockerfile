FROM golang:1.25-alpine

# Instalar protoc, git y bash
RUN apk add --no-cache protobuf git bash

WORKDIR /app

# Copiar módulos de Go y descargar dependencias
COPY go.mod .
COPY go.sum .
RUN go mod download

# Instalar plugins gRPC Go
RUN go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.32 \
    && go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@v1.3

# Asegurar que $GOPATH/bin esté en PATH
ENV PATH="$PATH:$(go env GOPATH)/bin"

# Copiar app (incluyendo proto)
COPY ./app ./app

WORKDIR /app/app

# Generación de stubs gRPC Go desde proto
RUN protoc --go_out=. --go-grpc_out=. proto/streaming.proto

# Ejecutable final
CMD ["go", "run", "main.go"]
