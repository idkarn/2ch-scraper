from lib.psc.proxy_scraper_checker import proxy_scraper_checker as psc


async def main():
    await psc.ProxyScraperChecker.run()
