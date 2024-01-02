package main

import (
	"flag"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gocolly/colly/v2"
	"github.com/gocolly/colly/v2/proxy"
	"github.com/joho/godotenv"
)

const PMAPI_URL string = "http://localhost:8000/proxy?n="

func getProxies(proxyListSize int) []string {
	url := fmt.Sprintf("%s%d", PMAPI_URL, proxyListSize)
	res, err := http.Get(url)
	for err != nil {
		log.Println("could not get proxies")
		time.Sleep(2 * time.Second)
		res, err = http.Get(url)
	}

	defer res.Body.Close()
	addr, err := io.ReadAll(res.Body)
	if err != nil {
		panic(err)
	}

	fmt.Println(string(addr[:]))
	return []string{string(addr[:])}
}

func setupCollector(c *colly.Collector) error {
	err := godotenv.Load("app/.env")
	if err != nil {
		log.Fatal("Error loading .env file")
	}

	if ua := os.Getenv("USER_AGENT"); ua != "" {
		c.UserAgent = ua
	} else {
		log.Println("USER_AGENT is not provided, using default one")
	}

	c.Limit(&colly.LimitRule{
		// Parallelism: 2,
		RandomDelay: 2 * time.Second,
	})

	if cfCookie := os.Getenv("CF_COOKIE"); cfCookie != "" {
		c.SetCookies(BASE_URL, []*http.Cookie{
			{
				Name:  "cf_clearance",
				Value: cfCookie,
			},
		})
	} else {
		log.Println("CF_COOKIE is not provided, cookie won't be set")
	}

	doUseProxy := flag.Bool("no-proxy", true, "provide to disable proxy usage")
	flag.Parse()

	if *doUseProxy {
		rp, err := proxy.RoundRobinProxySwitcher("http://115.223.11.212:50000", "socks5://67.201.33.10:25283")
		if err != nil {
			panic(err)
		}
		c.SetProxyFunc(rp)
	}

	return nil
}
