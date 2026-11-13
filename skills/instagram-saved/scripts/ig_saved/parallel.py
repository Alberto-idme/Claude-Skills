"""Run the network-bound stages concurrently.

Extraction, place-finding, enrichment and description are all the same shape:
one API call per row, nothing shared between rows, and almost all the elapsed
time spent waiting on a response. Run serially they take as long as the sum of
their round trips; the work itself is negligible.

The rule this module exists to enforce: **API calls run in threads, database
writes do not.** A `sqlite3.Connection` belongs to the thread that made it, and
the stages all write results as they arrive, so the worker returns a value and
the caller writes it on the main thread. That is the pattern `media.py` already
uses for downloads.
"""

from __future__ import annotations

import sys
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from typing import Any, Callable, Iterable, Iterator

# Enough to hide the latency, low enough to stay well inside per-minute
# request limits on a personal account.
DEFAULT_WORKERS = 6


def imap(
    fn: Callable[[Any], Any],
    items: Iterable[Any],
    *,
    workers: int = DEFAULT_WORKERS,
    keep_going: Callable[[], bool] | None = None,
) -> Iterator[tuple[Any, Any, BaseException | None]]:
    """Yield ``(item, result, error)`` as each call finishes.

    Results arrive in completion order, not input order — callers that care
    must sort, and the ones here do not: each row is written on its own.

    An exception from ``fn`` is returned rather than raised, so one failed row
    cannot abandon the rest of a long, part-paid run.

    ``keep_going`` is checked before each submission and stops the run when it
    returns False. Work already in flight still completes, so a budget enforced
    this way can overshoot by up to ``workers`` calls — bounded and reported,
    rather than cancelled mid-request and billed anyway.
    """
    items = list(items)
    if not items:
        return

    workers = max(1, workers)
    pending: dict = {}
    nxt = 0

    with ThreadPoolExecutor(max_workers=workers) as pool:
        while nxt < len(items) or pending:
            while (len(pending) < workers and nxt < len(items)
                   and (keep_going is None or keep_going())):
                pending[pool.submit(fn, items[nxt])] = items[nxt]
                nxt += 1

            if not pending:
                break  # budget spent and nothing left in flight

            done, _ = wait(list(pending), return_when=FIRST_COMPLETED)
            for future in done:
                item = pending.pop(future)
                try:
                    yield item, future.result(), None
                except BaseException as exc:  # noqa: BLE001 - handed to caller
                    yield item, None, exc


def progress(n: int, total: int, label: str, every: int = 10) -> None:
    if n == total or n % every == 0:
        print(f"  {n}/{total} {label}", file=sys.stderr)
