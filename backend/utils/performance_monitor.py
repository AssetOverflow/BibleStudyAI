import time
import asyncio
from typing import Dict, Any, Optional
from loguru import logger
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class PerformanceMetrics:
    """
    Tracks performance metrics for various operations.
    """

    operation_count: int = 0
    total_time: float = 0.0
    min_time: float = float("inf")
    max_time: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    errors: int = 0
    last_operation_time: Optional[float] = None

    @property
    def average_time(self) -> float:
        """Calculate average operation time."""
        return (
            self.total_time / self.operation_count if self.operation_count > 0 else 0.0
        )

    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total_cache_ops = self.cache_hits + self.cache_misses
        return self.cache_hits / total_cache_ops if total_cache_ops > 0 else 0.0


class PerformanceMonitor:
    """
    Monitors and tracks performance metrics for the RAG system.
    """

    def __init__(self):
        self.metrics: Dict[str, PerformanceMetrics] = defaultdict(PerformanceMetrics)
        self.start_time = time.time()

    @asynccontextmanager
    async def measure_operation(self, operation_name: str):
        """
        Context manager to measure the performance of an operation.

        Usage:
            async with monitor.measure_operation("vector_search"):
                result = await vector_search(query)
        """
        start_time = time.time()
        error_occurred = False

        try:
            yield
        except Exception as e:
            error_occurred = True
            self.metrics[operation_name].errors += 1
            logger.error(f"Error in {operation_name}: {e}")
            raise
        finally:
            end_time = time.time()
            operation_time = end_time - start_time

            # Update metrics
            metric = self.metrics[operation_name]
            metric.operation_count += 1
            metric.total_time += operation_time
            metric.min_time = min(metric.min_time, operation_time)
            metric.max_time = max(metric.max_time, operation_time)
            metric.last_operation_time = operation_time

            logger.debug(f"{operation_name} completed in {operation_time:.4f}s")

    def record_cache_hit(self, operation_name: str):
        """Record a cache hit for an operation."""
        self.metrics[operation_name].cache_hits += 1
        logger.debug(f"Cache hit for {operation_name}")

    def record_cache_miss(self, operation_name: str):
        """Record a cache miss for an operation."""
        self.metrics[operation_name].cache_misses += 1
        logger.debug(f"Cache miss for {operation_name}")

    def get_metrics(self, operation_name: str) -> PerformanceMetrics:
        """Get metrics for a specific operation."""
        return self.metrics[operation_name]

    def get_all_metrics(self) -> Dict[str, PerformanceMetrics]:
        """Get all tracked metrics."""
        return dict(self.metrics)

    def generate_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive performance report.
        """
        total_runtime = time.time() - self.start_time

        report = {"total_runtime_seconds": total_runtime, "operations": {}}

        for operation_name, metrics in self.metrics.items():
            report["operations"][operation_name] = {
                "operation_count": metrics.operation_count,
                "total_time_seconds": metrics.total_time,
                "average_time_seconds": metrics.average_time,
                "min_time_seconds": (
                    metrics.min_time if metrics.min_time != float("inf") else 0
                ),
                "max_time_seconds": metrics.max_time,
                "cache_hit_rate": metrics.cache_hit_rate,
                "cache_hits": metrics.cache_hits,
                "cache_misses": metrics.cache_misses,
                "error_count": metrics.errors,
                "operations_per_second": (
                    metrics.operation_count / total_runtime if total_runtime > 0 else 0
                ),
                "percentage_of_total_time": (
                    (metrics.total_time / total_runtime * 100)
                    if total_runtime > 0
                    else 0
                ),
            }

        return report

    def log_performance_summary(self):
        """
        Log a summary of performance metrics.
        """
        report = self.generate_report()

        logger.info("=== Performance Summary ===")
        logger.info(f"Total Runtime: {report['total_runtime_seconds']:.2f} seconds")

        for operation_name, metrics in report["operations"].items():
            logger.info(f"\n{operation_name.upper()}:")
            logger.info(f"  Operations: {metrics['operation_count']}")
            logger.info(f"  Avg Time: {metrics['average_time_seconds']:.4f}s")
            logger.info(f"  Cache Hit Rate: {metrics['cache_hit_rate']:.2%}")
            logger.info(f"  Errors: {metrics['error_count']}")
            logger.info(f"  Ops/sec: {metrics['operations_per_second']:.2f}")

    def reset_metrics(self):
        """Reset all metrics."""
        self.metrics.clear()
        self.start_time = time.time()
        logger.info("Performance metrics reset")


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    return performance_monitor


# Decorator for automatic performance monitoring
def monitor_performance(operation_name: str):
    """
    Decorator to automatically monitor the performance of async functions.

    Usage:
        @monitor_performance("vector_search")
        async def vector_search(query: str):
            # function implementation
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            async with performance_monitor.measure_operation(operation_name):
                return await func(*args, **kwargs)

        return wrapper

    return decorator


# Example usage and testing
async def example_usage():
    """Example of how to use the performance monitor."""
    monitor = get_performance_monitor()

    # Method 1: Using context manager
    async with monitor.measure_operation("example_operation"):
        await asyncio.sleep(0.1)  # Simulate work

    # Method 2: Using decorator
    @monitor_performance("decorated_operation")
    async def example_function():
        await asyncio.sleep(0.05)
        return "result"

    await example_function()

    # Record cache operations
    monitor.record_cache_hit("example_operation")
    monitor.record_cache_miss("example_operation")

    # Generate and log report
    monitor.log_performance_summary()

    # Get specific metrics
    metrics = monitor.get_metrics("example_operation")
    print(f"Example operation average time: {metrics.average_time:.4f}s")


if __name__ == "__main__":
    asyncio.run(example_usage())
