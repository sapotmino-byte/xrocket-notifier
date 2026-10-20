import os

from aiohttp import web

_runner = None


async def handle_root(request):
    return web.Response(text="xrocket-notifier OK")


async def start_health_server():
    """Мини-HTTP сервер. Нужен на передплатных платформах (Render),
    которые требуют отвечать на запросы на переменную окружения PORT.
    Локально не работает (PORT не задан)."""
    global _runner
    port = int(os.getenv("PORT") or "0")
    if not port:
        return False

    app = web.Application()
    app.router.add_get("/", handle_root)
    _runner = web.AppRunner(app)
    await _runner.setup()
    site = web.TCPSite(_runner, "0.0.0.0", port)
    await site.start()
    return True


async def stop_health_server():
    if _runner:
        await _runner.cleanup()
