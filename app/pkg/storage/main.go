package storage

import "github.com/gocolly/colly/v2"

var db *LinkDB
var storage *TextStorage

func SetupStorage() {
	storage = NewTextStorage()
}

func ConfigureDB(c *colly.Collector) {
	db = newDB()
	c.SetStorage(db)
}

func CloseDB() {
	db.conn.Close()
}
