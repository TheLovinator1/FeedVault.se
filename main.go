package main

import (
	"context"
	"log"
	"os"

	"net/http"

	"github.com/TheLovinator1/FeedVault/db"
	"github.com/jackc/pgx/v5/pgxpool"
	_ "github.com/joho/godotenv/autoload"
)

var (
	dbpool *pgxpool.Pool
	DB     *db.Queries
)

// Connect to our PostgreSQL database and store the connection pool in the DB variable that we can use throughout our application.
func init() {
	ctx := context.Background()

	// Open a database connection
	databaseURL := os.Getenv("DATABASE_URL")
	if databaseURL == "" {
		databaseURL = "postgresql://localhost/feedvault?user=feedvault&password=feedvault"
	}
	log.Printf("Connecting to database: %s", databaseURL)
	dbpool, err := pgxpool.New(ctx, databaseURL)
	if err != nil {
		log.Fatalf("pgxpool.New(): %v", err)
	}

	// Create a new DB object
	DB = db.New(dbpool)

	// Test the connection
	if err := dbpool.Ping(ctx); err != nil {
		log.Fatalf("dbpool.Ping(): %v", err)
	}
}

func main() {
	defer dbpool.Close()

	log.Print("Starting server")

	// Create a new ServeMux
	mux := http.NewServeMux()

	// Routes
	mux.HandleFunc("/", IndexHandler)
	mux.HandleFunc("/api", ApiHandler)
	mux.HandleFunc("/feeds", FeedsHandler)
	mux.HandleFunc("/feed/", FeedHandler)
	mux.HandleFunc("/add", AddFeedHandler)
	mux.HandleFunc("/upload_opml", UploadOpmlHandler)

	// Create server
	port := os.Getenv("PORT")
	if port == "" {
		port = "8000"
	}
	host := os.Getenv("HOST")
	if host == "" {
		host = "127.0.0.1"
	}
	server := &http.Server{
		Addr:    host + ":" + port,
		Handler: mux,
	}

	log.Print("Server started on http://" + host + ":" + port + " <Ctrl-C> to stop")
	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("ListenAndServe(): %v", err)
	}
}
