import asyncio
from json import load, dump
import random

from sanic import Sanic, json, Request
from proxy import get_proxies, is_working

app = Sanic("proxy-manager", configure_logging=False)
proxy_list: dict[str, list[str]] = {}


async def get_working_proxy(p: str) -> str:
    def get_proto():
        return p.upper() or ("HTTP" if random.random() < 0.5 else "SOCKS5")

    proto = get_proto()
    addr = random.choice(proxy_list[proto])

    while not await is_working(proto, addr):
        proxy_list[proto].remove(addr)

        proto = get_proto()
        addr = random.choice(proxy_list[proto])

    return f"{proto.lower()}://{addr}"


@app.route("/proxy")
async def handle_proxy(req: Request):
    n = int(req.args["n"][0]) if "n" in req.args else 1
    proxy_list = [
        await get_working_proxy(req.args["p"][0] if "p" in req.args else "")
        for _ in range(n)
    ]
    return json(proxy_list)


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
