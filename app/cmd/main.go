package main

import (
	"log"
	"time"

	"github.com/gocolly/colly/v2"
	"github.com/gocolly/colly/v2/debug"
	"github.com/idkarn/2ch-scraper/pkg/storage"
)

const BASE_URL string = "https://2ch.hk"

var DOMAINS = []string{"2ch.hk", "2ch.life"}

func main() {
	c := colly.NewCollector(
		colly.Debugger(&debug.LogDebugger{}),
		colly.Async(true),
		colly.AllowedDomains(DOMAINS...),
	)

	setupCollector(c)
	storage.ConfigureDB(c)
	defer storage.CloseDB()

	c.OnRequest(func(r *colly.Request) {
		log.Println("Visiting", r.URL)
	})

	c.OnError(func(r *colly.Response, err error) {
		body := string(r.Body)
		log.Println("Request URL:", r.Request.URL, "failed with response:", body, "\nError:", err)
	})

	c.OnResponse(func(r *colly.Response) {
		log.Println(r.StatusCode)
	})

	c.OnHTML("a[href]", func(e *colly.HTMLElement) {
		time.Sleep(2 * time.Second)
		e.Request.Visit(e.Attr("href"))
	})

	c.Visit(BASE_URL)
	c.Wait()
}
