package main

import (
	"context"
	"log"

	"net/http"

	"github.com/TheLovinator1/FeedVault/db"
	"github.com/jackc/pgx/v5"
)

var (
	conn *pgx.Conn
	DB   *db.Queries
)

func init() { log.SetFlags(log.LstdFlags | log.Lshortfile) }

func init() {
	ctx := context.Background()

	// Open a database connection
	conn, err := pgx.Connect(ctx, "postgresql://localhost/feedvault?user=feedvault&password=feedvault")
	if err != nil {
		log.Fatalf("pgx.Connect(): %v", err)
	}

	DB = db.New(conn)
}

func main() {
	defer conn.Close(context.Background())

	log.Print("Starting server")

	// Create a new ServeMux
	mux := http.NewServeMux()

	// Routes
	mux.HandleFunc("/", IndexHandler)
	mux.HandleFunc("/api", ApiHandler)
	mux.HandleFunc("/feeds", FeedsHandler)
	mux.HandleFunc("/add", AddFeedHandler)
	mux.HandleFunc("/upload_opml", UploadOpmlHandler)

	// Create server
	server := &http.Server{
		Addr:    "127.0.0.1:8000",
		Handler: mux,
	}

	log.Print("Server started on http://localhost:8000/ <Ctrl-C> to stop")
	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("ListenAndServe(): %v", err)
	}
}
