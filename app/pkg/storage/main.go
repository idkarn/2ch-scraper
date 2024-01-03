package storage

import (
	"encoding/binary"
	"log"
	"os"

	"github.com/gocolly/colly/v2"
)

var db *LinkDB
var storage *TextStorage

const DATA_PATH = "./app/data"
const LINE_PATH = DATA_PATH + "/.size"
const FILE_SIZE = 20000 // number of serialized texts for file

func SetupStorage() {
	storage = NewTextStorage()
	storage.Load()
	log.Println("Current storage size is", storage.size)
	if err := storage.openNewFile(); err != nil {
		log.Fatal("could not open data file")
	}
}

func ConfigureDB(c *colly.Collector) {
	db = newDB()
	c.SetStorage(db)
}

func SaveText(text string) {
	if storage.size >= FILE_SIZE {
		if err := storage.openNewFile(); err != nil {
			panic(err)
		}
	}
	if err := storage.AppendText(text); err != nil {
		log.Println("could not save text in storage")
	}
}

func CloseStorage() {
	if err := storage.file.Close(); err != nil {
		log.Println("could not close file with data")
	}

	f, err := os.OpenFile(LINE_PATH, os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Printf("could not open file to save storage size (%d)", storage.size)
	}
	if err = binary.Write(f, binary.NativeEndian, storage.size); err != nil {
		log.Printf("could not save storage size (%d) in file", storage.size)
	}

	log.Println("TextStorage successfuly closed")
}

func CloseDB() {
	db.conn.Close()
	log.Println("LinksDB successfuly closed")
}
