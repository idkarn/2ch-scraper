import asyncio
import json
import random

from aiohttp_socks import ProxyType

from .extract import fetch_from_list
from .proxy import Proxy

MAX_CONNECTIONS = 512


class Grabber:
    sources: dict[ProxyType, frozenset[str]]
    proxies: dict[ProxyType, set[Proxy]]
    sem: asyncio.Semaphore

    def __init__(self, sources_file_path: str) -> None:
        with open(sources_file_path) as f:
            self.sources = {
                ProxyType[proto]: frozenset(filter(None, sources))
                for proto, sources in json.load(f).items()
                if sources
            }
        self.proxies = {proto: set() for proto in ProxyType}
        self.sem = asyncio.Semaphore(MAX_CONNECTIONS)

    async def fetch_all_sources(self) -> None:
        self.proxies = await fetch_from_list(self.sources)

    async def check_all_proxies(self) -> None:
        async def f(proxy: Proxy, proto: ProxyType):
            if not await proxy.is_working(proto, self.sem):
                self.proxies[proto].remove(proxy)

        coroutines = [
            f(proxy, proto)
            for proto, proxies in self.proxies.items()
            for proxy in proxies
        ]
        random.shuffle(coroutines)
        await asyncio.gather(*coroutines)

    def clean_source_list(self) -> None:  # TODO
        "Remove all bad sources, which are timed out or unreachable"


async def get_proxies() -> dict[str, list[str]]:
    # set_event_loop_policy()
    grabber = Grabber("./proxy/lib/proxy_grabber/sources.json")
    await grabber.fetch_all_sources()
    await grabber.check_all_proxies()

    # save_proxies_to_file()
    proxies = {
        proto.name.lower(): [proxy.addr for proxy in proxies]
        for proto, proxies in grabber.proxies.items()
    }
    return proxies
