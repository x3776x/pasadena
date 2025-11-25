package server

import (
	"context"
	"log"
	"time"

	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

var DB *mongo.Database

func ConnectMongo() {
	// URI usando usuario, contraseña, host del contenedor y authSource
	uri := "mongodb://papu:Kavinsky@pasadena_mongo:27017/?authSource=admin"
	dbName := "pasadena_db"

	// Configurar opciones del cliente
	clientOpts := options.Client().ApplyURI(uri)

	// Contexto con timeout para la conexión
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	client, err := mongo.Connect(ctx, clientOpts)
	if err != nil {
		log.Fatal("Error conectando a MongoDB:", err)
	}

	// Verificar la conexión
	if err := client.Ping(ctx, nil); err != nil {
		log.Fatal("No se pudo hacer ping a MongoDB:", err)
	}

	log.Println("Conectado a MongoDB correctamente!")
	DB = client.Database(dbName)
}
