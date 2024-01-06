import asyncio
from re import Match

from aiohttp import ClientSession, ClientTimeout
from aiohttp_socks import ProxyType

from .utils import HEADERS, URI_REGEX, logger
from .proxy import Proxy

SOURCE_TIMEOUT = 15


class BadStatusCodeError(Exception):
    "Session got response with non-200 status code."

    def __init__(self, code: int, *args: object) -> None:
        super().__init__(*args)
        self.code = code


async def fetch_source(
    session: ClientSession, source: str, proxy_list: set[Proxy]
) -> None:
    new_proxies: list[Proxy] = []
    async with session.get(source) as response:
        if response.status != 200:
            raise BadStatusCodeError(response.status)
        await response.read()
    text = await response.text()

    proxies = URI_REGEX.finditer(text)
    proxy: Match[str] = next(proxies)

    new_proxies.append(Proxy(proxy))
    for proxy in proxies:
        new_proxies.append(Proxy(proxy))

    proxy_list.update(new_proxies)


async def fetch_from_list(
    source_list: dict[ProxyType, list[str]],
) -> dict[ProxyType, set[Proxy]]:
    proxies: dict[ProxyType, set[Proxy]] = {proto: set() for proto in source_list}
    async with ClientSession(
        headers=HEADERS, timeout=ClientTimeout(total=SOURCE_TIMEOUT)
    ) as session:

        async def f(proto: ProxyType, source: str):
            try:
                await fetch_source(session, source, proxies[proto])
            except asyncio.TimeoutError:
                logger.warning("%s | Timed out", source)
            except StopIteration:
                logger.warning("%s | No proxies found", source)
            except BadStatusCodeError as e:
                logger.warning("%s | HTTP status code %d", source, e.code)
            except Exception as e:
                e_str = str(e)
                logger.error(
                    f"{source} | {e.__class__.__module__}.{e.__class__.__qualname__}{f' {e_str}' if e_str else ''}"
                )

        coroutines = (
            f(proto, source)
            for proto, sources in source_list.items()
            for source in sources
        )
        logger.info(coroutines)
        await asyncio.gather(*coroutines)
    return proxies
