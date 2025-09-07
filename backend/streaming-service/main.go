package main

import (
	"fmt"
	"log"
	"net/http"
)

func helloHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Greetings from streaming-service!")
}

func main() {
	http.HandleFunc("/", helloHandler)
	fmt.Println("Server running on port 8003...")
	log.Fatal(http.ListenAndServe(":8003", nil))
}