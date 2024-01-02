package storage

import (
	"log"
	"net/url"

	"github.com/akrylysov/pogreb"
)

type LinkDB struct {
	conn *pogreb.DB
}

func newDB() *LinkDB {
	db, err := pogreb.Open("links.db", nil)
	if err != nil {
		log.Fatal(err)
	}
	return &LinkDB{db}
}

func (db *LinkDB) Init() error {
	return nil
}

func (db *LinkDB) Visited(requestID uint64) error {
	return nil
}

func (db *LinkDB) IsVisited(requestID uint64) (bool, error) {
	return false, nil
}

func (db *LinkDB) Cookies(u *url.URL) string {
	return ""
}

func (db *LinkDB) SetCookies(u *url.URL, cookie string) {

}
