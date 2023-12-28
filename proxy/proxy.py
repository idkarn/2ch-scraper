import asyncio
from configparser import ConfigParser
import random

from aiohttp import ClientSession, ClientTimeout
from aiohttp_socks import ProxyType
from lib.psc.proxy_scraper_checker.proxy_scraper_checker import ProxyScraperChecker
from lib.psc.proxy_scraper_checker.constants import HEADERS
from lib.psc.proxy_scraper_checker.proxy import Proxy

TIMEOUT = 3
DEFAULT_CHECK_WEBSITE = "http://ifconfig.me/ip"


cfg = ConfigParser(interpolation=None)
cfg.read("./proxy/lib/psc/config.ini", encoding="utf-8")
psc = ProxyScraperChecker.from_configparser(cfg)


async def fetch_source(
    self, *, session: ClientSession, source: str, proto: ProxyType
) -> None:
    try:
        async with session.get(source, verify_ssl=False) as response:
            await response.read()
        text = await response.text()
    except asyncio.TimeoutError:
        print(f"{source} time's up")
    except Exception as e:
        print(e.with_traceback(e.__traceback__))
    else:
        proxies = self.regex.finditer(text)
        try:
            proxy = next(proxies)
        except StopIteration:
            ...
        else:
            proxies_set = self.proxies[proto]
            proxies_set.add(Proxy(host=proxy.group(1), port=int(proxy.group(2))))
            for proxy in proxies:
                proxies_set.add(Proxy(host=proxy.group(1), port=int(proxy.group(2))))


async def is_working(proto: str, addr: str) -> bool:
    try:
        await Proxy(*addr.split(":")).check(
            website=DEFAULT_CHECK_WEBSITE,
            sem=psc.sem,
            cookie_jar=psc.cookie_jar,
            proto=ProxyType[proto],
            timeout=psc.timeout,
            set_geolocation=False,
        )
    except Exception:
        return False
    return True


async def check_proxy(self, *, proxy: Proxy, proto: ProxyType) -> None:
    try:
        await proxy.check(
            website=DEFAULT_CHECK_WEBSITE,
            sem=self.sem,
            cookie_jar=self.cookie_jar,
            proto=proto,
            timeout=self.timeout,
            set_geolocation=False,
        )
    except Exception:
        self.proxies[proto].remove(proxy)


async def fetch_sources(psc: ProxyScraperChecker) -> list[str]:
    async with ClientSession(
        headers=HEADERS,
        cookie_jar=psc.cookie_jar,
        timeout=ClientTimeout(total=psc.source_timeout),
    ) as session:
        coroutines = (
            fetch_source(
                psc,
                session=session,
                source=source,
                proto=proto,
            )
            for proto, sources in psc.sources.items()
            for source in sources
        )
        await asyncio.gather(*coroutines)

    psc.proxies_count = {proto: len(proxies) for proto, proxies in psc.proxies.items()}


async def check_proxies(psc: ProxyScraperChecker) -> list[str]:
    coroutines = [
        check_proxy(psc, proxy=proxy, proto=proto)
        for proto, proxies in psc.proxies.items()
        for proxy in proxies
    ]
    random.shuffle(coroutines)
    await asyncio.gather(*coroutines)


async def get_proxies() -> dict[str, list[str]]:
    await fetch_sources(psc)
    await check_proxies(psc)

    sorted_proxies = psc.get_sorted_proxies()

    pl = {
        proto.name: [
            proxy.as_str(include_geolocation=False) for proxy in sorted_proxies[proto]
        ]
        for proto in sorted_proxies
    }

    return pl
