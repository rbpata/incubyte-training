from datetime import datetime, timedelta, timezone

import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.db.base import TaskStatus
from app.performance.lab import (
    TaskSnapshot,
    iter_due_task_ids,
    normalize_sort_order,
    retry_budget_ratio_loop,
)


@given(st.text())
def test_normalize_sort_order_is_always_valid(raw_sort_order: str) -> None:
    result = normalize_sort_order(raw_sort_order)
    assert result in {"asc", "desc"}


@given(
    st.lists(
        st.tuples(
            st.integers(min_value=0, max_value=20),
            st.integers(min_value=0, max_value=20),
        ),
        min_size=1,
        max_size=30,
    )
)
def test_retry_budget_ratio_loop_respects_bounds_for_valid_pairs(
    retry_pairs: list[tuple[int, int]],
) -> None:
    retry_counts = [count for count, _ in retry_pairs]
    max_retries = [limit for _, limit in retry_pairs]

    ratios = retry_budget_ratio_loop(retry_counts, max_retries)

    assert len(ratios) == len(retry_pairs)
    for ratio, (retry_count, max_retry) in zip(ratios, retry_pairs, strict=True):
        if max_retry == 0:
            assert ratio == 0.0
        else:
            assert ratio == pytest.approx(retry_count / max_retry)
            assert ratio >= 0.0


@given(
    st.lists(
        st.tuples(
            st.integers(min_value=1, max_value=5_000),
            st.integers(min_value=-120, max_value=120),
            st.sampled_from(
                [
                    TaskStatus.PENDING,
                    TaskStatus.RUNNING,
                    TaskStatus.COMPLETED,
                    TaskStatus.FAILED,
                ]
            ),
        ),
        min_size=1,
        max_size=50,
    )
)
def test_iter_due_task_ids_matches_expected_filter(
    generated_tasks: list[tuple[int, int, TaskStatus]],
) -> None:
    now = datetime.now(timezone.utc)
    tasks = [
        TaskSnapshot(
            task_id=task_id,
            run_at=now + timedelta(minutes=offset_minutes),
            status=status,
        )
        for task_id, offset_minutes, status in generated_tasks
    ]

    yielded_ids = list(iter_due_task_ids(tasks, now=now))
    expected_ids = [
        task.task_id
        for task in tasks
        if task.status == TaskStatus.PENDING and task.run_at <= now
    ]

    assert yielded_ids == expected_ids
