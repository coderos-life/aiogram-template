import contextlib
import html
import platform
import sys
import time
from datetime import timedelta
from typing import Any

import aiogram
import psutil

from bot.database import get_repo

time_st = time.perf_counter()


def bytes_to_megabytes(b: float) -> float:
    return round(b / 1024 / 1024, 1)


def uptime() -> int:
    """
    Returns bot uptime in seconds
    :return: Uptime in seconds
    """
    return round(time.perf_counter() - time_st)


def formatted_uptime() -> str:
    """
    Returns formatted uptime
    :return: Formatted uptime
    """
    return str(timedelta(seconds=uptime()))


async def bot_info_dict() -> dict[str, Any]:
    """Returns bot and server diagnostics."""
    inf = {
        "cpu": "n/a",
        "cpu_load": "n/a",
        "ram": "n/a",
        "ram_load_mb": "n/a",
        "ram_load": "n/a",
        "arch_emoji": "n/a",
        "arch": "n/a",
        "os": "n/a",
        "python": "n/a",
        "aiogram": aiogram.__version__,
        "process_ram": "n/a",
        "process_ram_percent": "n/a",
        "process_cpu_percent": "n/a",
        "bot_working": formatted_uptime(),
        "users_in_db": 0,
    }

    with contextlib.suppress(Exception):
        inf["cpu"] = psutil.cpu_count(logical=True)

    with contextlib.suppress(Exception):
        inf["cpu_load"] = psutil.cpu_percent()

    with contextlib.suppress(Exception):
        inf["ram"] = bytes_to_megabytes(psutil.virtual_memory().total - psutil.virtual_memory().available)

    with contextlib.suppress(Exception):
        inf["ram_load_mb"] = bytes_to_megabytes(psutil.virtual_memory().total)

    with contextlib.suppress(Exception):
        inf["ram_load"] = psutil.virtual_memory().percent

    with contextlib.suppress(Exception):
        inf["arch"] = html.escape(platform.architecture()[0])

    arch = str(inf.get("arch", ""))
    inf["arch_emoji"] = (
        "<emoji document_id=5172881503478088537>💻</emoji>"
        if "64" in arch
        else "<emoji document_id=5174703196676817427>💻</emoji>"
    )

    with contextlib.suppress(Exception):
        os_release = platform.freedesktop_os_release()
        inf["os"] = html.escape(os_release.get("PRETTY_NAME", platform.platform()))

    with contextlib.suppress(Exception):
        inf["python"] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    # process
    process = psutil.Process()

    with contextlib.suppress(Exception):
        inf["process_ram"] = bytes_to_megabytes(process.memory_info().rss)

    with contextlib.suppress(Exception):
        inf["process_ram_percent"] = round(process.memory_percent(), 1)

    with contextlib.suppress(Exception):
        inf["process_cpu_percent"] = round(process.cpu_percent(), 1)

    async with get_repo() as repo:
        inf["users_in_db"] = await repo.users.get_all(count=True)

    return inf
