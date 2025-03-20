"""
ReasonLoop - A modular AI agent system
"""

import argparse
import logging
import time
import os
import json
from datetime import datetime
import psutil
import threading
from typing import Dict, Any, Optional

from config.logging_config import setup_logging
from config.settings import get_setting, update_setting
from core.execution_loop import run_execution_loop
from abilities.ability_registry import list_abilities

# Global counters for metrics
metrics = {
    "start_time": time.time(),
    "ollama_requests": 0,
    "tokens_in": 0,
    "tokens_out": 0,
    "total_execution_time": 0,
    "ability_metrics": {},
    "task_count": 0,
    "completed_tasks": 0,
    "failed_tasks": 0,
    "retries": 0
}

# Create a lock for thread-safe metrics updates
metrics_lock = threading.Lock()

def update_metrics(metric_name: str, value: Any) -> None:
    """Update metrics in a thread-safe way"""
    with metrics_lock:
        if metric_name in metrics:
            if isinstance(metrics[metric_name], (int, float)):
                metrics[metric_name] += value
            else:
                metrics[metric_name] = value
        else:
            metrics[metric_name] = value

def update_ability_metrics(ability_name: str, execution_time: float, tokens_in: int = 0, tokens_out: int = 0) -> None:
    """Update ability-specific metrics"""
    with metrics_lock:
        if ability_name not in metrics["ability_metrics"]:
            metrics["ability_metrics"][ability_name] = {
                "count": 0,
                "total_time": 0,
                "tokens_in": 0,
                "tokens_out": 0
            }

        metrics["ability_metrics"][ability_name]["count"] += 1
        metrics["ability_metrics"][ability_name]["total_time"] += execution_time
        metrics["ability_metrics"][ability_name]["tokens_in"] += tokens_in
        metrics["ability_metrics"][ability_name]["tokens_out"] += tokens_out

def estimate_tokens(text: str) -> int:
    """Estimate token count based on text length"""
    # Rough estimate: ~4 characters per token for English text
    return len(text) // 4

def monitor_system_resources() -> Dict[str, Any]:
    """Monitor system resources"""
    process = psutil.Process(os.getpid())
    return {
        "memory_usage_mb": process.memory_info().rss / 1024 / 1024,
        "cpu_percent": process.cpu_percent(interval=0.1),
        "threads": len(process.threads()),
        "open_files": len(process.open_files())
    }

def patch_text_completion():
    """Patch the text_completion_ability to track metrics"""
    from abilities.text_completion import text_completion_ability

    original_function = text_completion_ability

    def patched_text_completion(prompt: str) -> str:
        start_time = time.time()

        # Track tokens in
        tokens_in = estimate_tokens(prompt)
        update_metrics("tokens_in", tokens_in)

        # Track Ollama requests
        update_metrics("ollama_requests", 1)

        # Call original function
        result = original_function(prompt)

        # Calculate execution time
        execution_time = time.time() - start_time

        # Track tokens out
        tokens_out = estimate_tokens(result)
        update_metrics("tokens_out", tokens_out)

        # Calculate tokens per second
        tokens_per_second = tokens_out / execution_time if execution_time > 0 else 0

        # Update ability metrics
        update_ability_metrics(
            "text-completion",
            execution_time,
            tokens_in,
            tokens_out
        )

        # Log performance metrics
        logging.debug(f"LLM Performance: {tokens_per_second:.2f} tokens/sec, {tokens_out} tokens in {execution_time:.2f}s")

        return result

    # Replace the original function with our patched version
    from abilities.ability_registry import ABILITY_REGISTRY
    ABILITY_REGISTRY["text-completion"] = patched_text_completion

def patch_task_manager():
    """Patch TaskManager to track task metrics"""
    from core.task_manager import TaskManager

    original_execute_task = TaskManager.execute_task
    original_execute_task_with_retry = TaskManager.execute_task_with_retry

    def patched_execute_task(self, task):
        update_metrics("task_count", 1)
        result = original_execute_task(self, task)
        if result.success:
            update_metrics("completed_tasks", 1)
        else:
            update_metrics("failed_tasks", 1)
        return result

    def patched_execute_task_with_retry(self, task):
        retry_count = 0

        # Store original function to avoid recursion
        original = original_execute_task_with_retry

        # Define a replacement that counts retries
        def counting_execute(*args, **kwargs):
            nonlocal retry_count
            retry_count += 1
            if retry_count > 1:
                update_metrics("retries", 1)
            return original(self, *args, **kwargs)

        # Temporarily replace the method
        TaskManager.execute_task_with_retry = counting_execute

        # Call the method
        result = counting_execute(task)

        # Restore the original method
        TaskManager.execute_task_with_retry = original_execute_task_with_retry

        return result

    # Apply the patches
    TaskManager.execute_task = patched_execute_task
    TaskManager.execute_task_with_retry = patched_execute_task_with_retry

def print_metrics_report():
    """Print a detailed metrics report"""
    end_time = time.time()
    total_runtime = end_time - metrics["start_time"]

    # Get current system resources
    resources = monitor_system_resources()

    # Calculate tokens per second
    total_tokens_out = metrics["tokens_out"]
    avg_tokens_per_sec = total_tokens_out / total_runtime if total_runtime > 0 else 0

    # Build the report
    report = "\n" + "=" * 80 + "\n"
    report += "REASONLOOP EXECUTION METRICS\n"
    report += "=" * 80 + "\n\n"

    # Runtime metrics
    report += "RUNTIME METRICS:\n"
    report += f"- Total runtime: {total_runtime:.2f} seconds\n"
    report += f"- Tasks: {metrics['completed_tasks']}/{metrics['task_count']} completed ({metrics['failed_tasks']} failed)\n"
    report += f"- Retries: {metrics['retries']}\n\n"

    # LLM metrics
    report += "LLM METRICS:\n"
    report += f"- Ollama requests: {metrics['ollama_requests']}\n"
    report += f"- Total tokens in: {metrics['tokens_in']:,}\n"
    report += f"- Total tokens out: {metrics['tokens_out']:,}\n"
    report += f"- Average generation speed: {avg_tokens_per_sec:.2f} tokens/second\n\n"

    # Ability metrics
    report += "ABILITY METRICS:\n"
    for ability, stats in metrics["ability_metrics"].items():
        count = stats["count"]
        if count > 0:
            avg_time = stats["total_time"] / count
            report += f"- {ability}: {count} calls, avg {avg_time:.2f}s per call\n"

            if ability == "text-completion" and stats["total_time"] > 0:
                tokens_per_sec = stats["tokens_out"] / stats["total_time"]
                report += f"  * Tokens: {stats['tokens_in']:,} in, {stats['tokens_out']:,} out\n"
                report += f"  * Speed: {tokens_per_sec:.2f} tokens/second\n"

    # System resources
    report += "\nSYSTEM RESOURCES:\n"
    report += f"- Memory usage: {resources['memory_usage_mb']:.2f} MB\n"
    report += f"- CPU usage: {resources['cpu_percent']:.2f}%\n"
    report += f"- Threads: {resources['threads']}\n"
    report += f"- Open files: {resources['open_files']}\n"

    # Print the report
    print(report)

    # Save metrics to file
    metrics_dir = "logs/metrics"
    os.makedirs(metrics_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    metrics_file = os.path.join(metrics_dir, f"metrics_{timestamp}.json")

    with open(metrics_file, 'w') as f:
        json.dump({
            "runtime_seconds": total_runtime,
            "tasks": {
                "total": metrics["task_count"],
                "completed": metrics["completed_tasks"],
                "failed": metrics["failed_tasks"],
                "retries": metrics["retries"]
            },
            "llm": {
                "requests": metrics["ollama_requests"],
                "tokens_in": metrics["tokens_in"],
                "tokens_out": metrics["tokens_out"],
                "tokens_per_second": avg_tokens_per_sec
            },
            "abilities": metrics["ability_metrics"],
            "system": resources,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)

    print(f"Metrics saved to {metrics_file}")

def main():
    """Main entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="ReasonLoop - A modular AI agent system")
    parser.add_argument("--objective", "-o", type=str, help="The objective to achieve")
    parser.add_argument("--template", "-t", type=str, default="default_tasks",
                        help="Prompt template to use (default_tasks, marketing_insights, propensity_modeling)")
    parser.add_argument("--model", "-m", type=str, help="LLM model to use")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--list-abilities", "-l", action="store_true", help="List available abilities")

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)
    logger = logging.getLogger(__name__)

    # Apply patches for metrics tracking
    patch_text_completion()
    patch_task_manager()

    # Start resource monitoring
    initial_resources = monitor_system_resources()
    logger.debug(f"Initial memory usage: {initial_resources['memory_usage_mb']:.2f} MB")

    # Print banner
    print("\n" + "=" * 80)
    print(f"ReasonLoop v0.1.0 - Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80 + "\n")

    # List abilities if requested
    if args.list_abilities:
        abilities = list_abilities()
        print("Available abilities:")
        for name in abilities:
            print(f"- {name}")
        return

    # Update settings from command line
    if args.model:
        update_setting("LLM_MODEL", args.model)
        logger.info(f"Using model: {args.model}")

    # Set the prompt template
    if args.template:
        update_setting("PROMPT_TEMPLATE", args.template)
        logger.info(f"Using prompt template: {args.template}")

    # Get objective
    objective = args.objective or get_setting("DEFAULT_OBJECTIVE")
    logger.info(f"Starting with objective: {objective}")

    # Print configuration
    print(f"Model: {get_setting('LLM_MODEL')}")
    print(f"Template: {get_setting('PROMPT_TEMPLATE')}")
    print(f"Objective: {objective}")
    print("-" * 80 + "\n")

    # Run the execution loop
    try:
        start_time = time.time()
        success = run_execution_loop(objective)
        end_time = time.time()

        # Update total execution time
        metrics["total_execution_time"] = end_time - start_time

        # Print execution summary
        if success:
            print(f"\nExecution completed in {end_time - start_time:.2f} seconds")
        else:
            print("\nExecution failed")

        # Print detailed metrics report
        print_metrics_report()

    except KeyboardInterrupt:
        logger.info("Execution interrupted by user")
        print("\nExecution interrupted by user")
        print_metrics_report()
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}", exc_info=True)
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()