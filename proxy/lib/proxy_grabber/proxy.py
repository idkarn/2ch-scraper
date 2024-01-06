from re import Match

from aiohttp import ClientSession, ClientTimeout
from aiohttp_socks import ProxyConnector, ProxyType

from .utils import HEADERS, logger

TEST_TIMEOUT = 3
TEST_URL = "https://ifconfig.me/ip"


class Proxy:
    addr: str
    host: str
    port: int

    def __init__(self, url: Match[str]) -> None:
        self.host = url.group(1)
        self.port = url.group(2)

    @property
    def addr(self) -> str:
        return f"{self.host}:{self.port}"

    async def is_working(self, proto: ProxyType, sem) -> bool:
        try:
            async with sem:
                connector = ProxyConnector(
                    proxy_type=proto, host=self.host, port=self.port
                )
                async with ClientSession(
                    connector=connector,
                    timeout=ClientTimeout(total=TEST_TIMEOUT),
                    headers=HEADERS,
                ) as session, session.get(TEST_URL, raise_for_status=True) as response:
                    await response.read()
            data = await response.text()
            if self.host != data:
                return False
        except Exception:
            return False
        return True
