from datetime import datetime, timedelta, timezone

import pytest

from app.db.base import TaskStatus
from app.performance.lab import (
    TaskSnapshot,
    build_status_index,
    is_sort_field_allowed,
    iter_due_task_ids,
    normalize_sort_order,
    profile_callable,
    retry_budget_ratio_loop,
    retry_budget_ratio_numpy,
)


class TestLookupOptimizations:
    def test_build_status_index_groups_task_ids_by_status(self) -> None:
        items = [(1, "pending"), (2, "completed"), (3, "pending")]

        result = build_status_index(items)

        assert result["pending"] == {1, 3}
        assert result["completed"] == {2}

    def test_is_sort_field_allowed_uses_valid_field_set(self) -> None:
        assert is_sort_field_allowed("created_at") is True
        assert is_sort_field_allowed("unknown") is False


class TestCachingHelpers:
    def test_normalize_sort_order_returns_desc_for_invalid_value(self) -> None:
        assert normalize_sort_order("invalid") == "desc"

    def test_normalize_sort_order_is_cached(self) -> None:
        normalize_sort_order.cache_clear()

        normalize_sort_order("asc")
        normalize_sort_order("asc")

        cache_info = normalize_sort_order.cache_info()
        assert cache_info.hits >= 1


class TestGenerators:
    def test_iter_due_task_ids_yields_only_due_pending_tasks(self) -> None:
        now = datetime.now(timezone.utc)
        tasks = [
            TaskSnapshot(
                task_id=1, run_at=now - timedelta(minutes=1), status=TaskStatus.PENDING
            ),
            TaskSnapshot(
                task_id=2, run_at=now + timedelta(minutes=1), status=TaskStatus.PENDING
            ),
            TaskSnapshot(
                task_id=3,
                run_at=now - timedelta(minutes=1),
                status=TaskStatus.COMPLETED,
            ),
        ]

        result = list(iter_due_task_ids(tasks, now=now))

        assert result == [1]


class TestProfilingHelpers:
    def test_profile_callable_returns_result_and_call_count(self) -> None:
        def square(number: int) -> int:
            return number * number

        profiled_result = profile_callable(square, 4)

        assert profiled_result.result == 16
        assert profiled_result.total_calls >= 1


class TestNumpyExercise:
    def test_retry_budget_ratio_loop_computes_expected_values(self) -> None:
        result = retry_budget_ratio_loop([0, 1, 2], [1, 2, 4])
        assert result == [0.0, 0.5, 0.5]

    def test_retry_budget_ratio_numpy_matches_loop_when_numpy_is_available(
        self,
    ) -> None:
        pytest.importorskip("numpy")

        loop_result = retry_budget_ratio_loop([0, 1, 2], [1, 2, 4])
        numpy_result = retry_budget_ratio_numpy([0, 1, 2], [1, 2, 4])

        assert numpy_result == loop_result
