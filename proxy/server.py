import asyncio
from json import load, dump
import random

from sanic import Sanic, text
from proxy import get_proxies, is_working

app = Sanic("proxy-manager", configure_logging=False)
proxy_list: dict[str, list[str]] = {}


@app.route("/proxy")
async def proxy(req):
    proto = "HTTP" if random.random() < 0.5 else "SOCKS5"
    addr = random.choice(proxy_list[proto])

    while not await is_working(proto, addr):
        proxy_list[proto].remove(addr)

        proto = "HTTP" if random.random() < 0.5 else "SOCKS5"
        addr = random.choice(proxy_list[proto])

    return text(f"{proto.lower()}://{addr}")


def load_proxy_list() -> dict[str, list[str]] | None:
    try:
        with open("./proxy/proxies.json") as f:
            data = load(f)
    except Exception:
        return None
    return data


def dump_proxy_list(data: dict) -> None:
    with open("./proxy/proxies.json", "w") as f:
        dump(data, f)


@app.before_server_start
def setup(app, loop) -> None:
    if (pl := load_proxy_list()) is None:
        pl = asyncio.get_event_loop().run_until_complete(get_proxies())
        dump_proxy_list(pl)
    proxy_list.update(pl)

    print("[OK] proxy list loaded")
