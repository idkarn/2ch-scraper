package main

import (
	"fmt"
	"io"
	"log"
	"net/http"
	"time"

	"github.com/gocolly/colly/v2"
	"github.com/gocolly/colly/v2/debug"
	"github.com/gocolly/colly/v2/proxy"
)

const BASE_URL string = "http://2ch.hk/"
const PMAPI_URL string = "http://localhost:8000/proxy"

var DOMAINS = []string{"2ch.hk", "2ch.life"}

func getProxies() []string {
	res, err := http.Get(PMAPI_URL)
	for err != nil {
		log.Println("could not get proxies")
		time.Sleep(2 * time.Second)
		res, err = http.Get(PMAPI_URL)
	}

	defer res.Body.Close()
	addr, err := io.ReadAll(res.Body)
	if err != nil {
		panic(err)
	}

	fmt.Println(string(addr[:]))
	return []string{string(addr[:])}
}

func main() {
	c := colly.NewCollector(
		colly.Debugger(&debug.LogDebugger{}),
		colly.Async(true),
		colly.AllowedDomains(DOMAINS...),
	)

	c.Limit(&colly.LimitRule{
		// Parallelism: 2,
		RandomDelay: 2 * time.Second,
	})

	rp, err := proxy.RoundRobinProxySwitcher(getProxies()...)
	if err != nil {
		panic(err)
	}
	c.SetProxyFunc(rp)

	c.OnRequest(func(r *colly.Request) {
		fmt.Println("Visiting", r.URL)
		time.Sleep(2 * time.Second)
	})

	c.OnError(func(r *colly.Response, err error) {
		body := string(r.Body)
		// if readErr != nil {
		// 	fmt.Println("Request URL:", r.Request.URL, "failed to read response", "\nRead Error:", readErr, "\nResponse Error:", err)
		// } else {
		fmt.Println("Request URL:", r.Request.URL, "failed with response:", body, "\nError:", err)
		// }
	})

	c.OnHTML("a[href]", func(e *colly.HTMLElement) {
		time.Sleep(2 * time.Second)
		e.Request.Visit(e.Attr("href"))
	})

	c.Visit(BASE_URL)

	c.Wait()
}
