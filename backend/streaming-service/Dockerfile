FROM golang:1.25-alpine

RUN apk add --no-cache protobuf git bash

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

# Instalar plugins gRPC Go
RUN go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.32 \
    && go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@v1.3

ENV PATH="$PATH:$(go env GOPATH)/bin"

# Copiar todo el contenido del servicio
COPY . .

# Generar stubs gRPC
RUN protoc --go_out=. --go-grpc_out=. app/proto/streaming.proto

# Ejecutable final
CMD ["go", "run", "main.go"]
