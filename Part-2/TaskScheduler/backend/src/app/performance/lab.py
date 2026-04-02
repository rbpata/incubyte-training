from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
import cProfile
from io import StringIO
import pstats
from typing import Any, Callable, Iterable, Iterator

from app.db.base import TaskStatus

VALID_SORT_FIELDS = {"created_at", "run_at", "status", "priority"}
DEFAULT_SORT_ORDER = "desc"


@dataclass(frozen=True)
class TaskSnapshot:
    task_id: int
    run_at: datetime
    status: TaskStatus


@dataclass(frozen=True)
class ProfiledExecution:
    result: Any
    total_calls: int
    primitive_calls: int
    summary: str


def build_status_index(
    task_status_pairs: Iterable[tuple[int, str]],
) -> dict[str, set[int]]:
    """Build a status to task ids index for O(1) membership checks."""
    status_index: defaultdict[str, set[int]] = defaultdict(set)
    for task_id, status_name in task_status_pairs:
        status_index[status_name].add(task_id)
    return dict(status_index)


@lru_cache(maxsize=16)
def is_sort_field_allowed(field_name: str) -> bool:
    return field_name in VALID_SORT_FIELDS


@lru_cache(maxsize=4)
def normalize_sort_order(sort_order: str) -> str:
    lowered = sort_order.lower()
    if lowered in {"asc", "desc"}:
        return lowered
    return DEFAULT_SORT_ORDER


def iter_due_task_ids(tasks: Iterable[TaskSnapshot], now: datetime) -> Iterator[int]:
    for task in tasks:
        if task.status == TaskStatus.PENDING and task.run_at <= now:
            yield task.task_id


def profile_callable(
    function: Callable[..., Any], *args: Any, **kwargs: Any
) -> ProfiledExecution:
    profiler = cProfile.Profile()
    profiler.enable()
    result = function(*args, **kwargs)
    profiler.disable()

    stream = StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.strip_dirs().sort_stats("cumulative").print_stats(5)

    return ProfiledExecution(
        result=result,
        total_calls=stats.total_calls,
        primitive_calls=stats.prim_calls,
        summary=stream.getvalue(),
    )


def profile_memory_usage(
    function: Callable[..., Any], *args: Any, **kwargs: Any
) -> tuple[Any, float]:
    """Return function result and memory delta in MiB (requires memory_profiler)."""
    try:
        from memory_profiler import memory_usage
    except ModuleNotFoundError as error:
        raise RuntimeError("memory_profiler is not installed") from error

    memory_samples, result = memory_usage((function, args, kwargs), retval=True)
    memory_delta = max(memory_samples) - min(memory_samples)
    return result, float(memory_delta)


def retry_budget_ratio_loop(
    retry_counts: list[int], max_retries: list[int]
) -> list[float]:
    ratios: list[float] = []
    for retry_count, max_retry in zip(retry_counts, max_retries, strict=True):
        if max_retry == 0:
            ratios.append(0.0)
            continue
        ratios.append(retry_count / max_retry)
    return ratios


def retry_budget_ratio_numpy(
    retry_counts: list[int], max_retries: list[int]
) -> list[float]:
    try:
        import numpy as np
    except ModuleNotFoundError as error:
        raise RuntimeError("numpy is not installed") from error

    retry_array = np.array(retry_counts, dtype=float)
    max_retry_array = np.array(max_retries, dtype=float)

    with np.errstate(divide="ignore", invalid="ignore"):
        ratios = np.divide(
            retry_array,
            max_retry_array,
            out=np.zeros_like(retry_array),
            where=max_retry_array != 0,
        )

    return ratios.tolist()
