package storage

import (
	"encoding/binary"
	"log"
	"net/http/cookiejar"
	"net/url"

	"github.com/akrylysov/pogreb"
	cs "github.com/gocolly/colly/v2/storage"
)

const DB_PATH = "./app/links.db"

type LinkDB struct {
	conn *pogreb.DB
	jar  *cookiejar.Jar
}

func newDB() *LinkDB {
	db, err := pogreb.Open(DATA_PATH, nil)
	if err != nil {
		log.Fatal(err)
	}
	jar, err := cookiejar.New(nil)
	if err != nil {
		log.Fatal(err)
	}
	return &LinkDB{db, jar}
}

func uint64ToBytes(val uint64) []byte {
	key := make([]byte, 8)
	binary.NativeEndian.PutUint64(key, val)
	return key
}

func (db *LinkDB) Init() error {
	var err error
	if db.conn == nil {
		db.conn, err = pogreb.Open(DB_PATH, nil)
	}
	if err != nil {
		return err
	}
	if db.jar == nil {
		db.jar, err = cookiejar.New(nil)
	}
	return err
}

func (db *LinkDB) Visited(requestID uint64) error {
	return db.conn.Put(uint64ToBytes(requestID), nil)
}

func (db *LinkDB) IsVisited(requestID uint64) (bool, error) {
	return db.conn.Has(uint64ToBytes(requestID))
}

func (db *LinkDB) Cookies(u *url.URL) string {
	return cs.StringifyCookies(db.jar.Cookies(u))
}

func (db *LinkDB) SetCookies(u *url.URL, cookie string) {
	db.jar.SetCookies(u, cs.UnstringifyCookies(cookie))
}
