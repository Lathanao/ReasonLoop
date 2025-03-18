"""
Main execution loop for the application
"""

import logging
import time
from typing import Optional
from core.task_manager import TaskManager

logger = logging.getLogger(__name__)

def run_execution_loop(objective: str) -> bool:
    """Run the main execution loop"""
    logger.info(f"Starting execution loop with objective: {objective}")
    start_time = time.time()

    # Initialize task manager
    task_manager = TaskManager(objective)

    # Create initial tasks
    tasks = task_manager.create_initial_tasks()
    if not tasks:
        logger.error("Failed to create initial tasks")
        return False

    task_manager.print_task_list()

    # Execute tasks until none are left
    cycle_count = 0
    completed_tasks = 0
    total_tasks = len(tasks)

    while True:
        cycle_count += 1
        logger.info(f"CYCLE #{cycle_count} STARTING ({completed_tasks}/{total_tasks} tasks completed)")

        # Find next task
        next_task = task_manager.find_next_task()
        if not next_task:
            logger.info("No more tasks to execute")
            break

        # Execute task
        result = task_manager.execute_task_with_retry(next_task)
        if result.success:
            completed_tasks += 1
        else:
            logger.error(f"Task #{next_task.id} failed: {result.error}")

        task_manager.print_task_list()

        # Small delay to make logs readable
        time.sleep(0.5)

    # Calculate execution time
    execution_time = time.time() - start_time

    # Print final summary
    logger.info("===== EXECUTION COMPLETE =====")
    logger.info(f"Completed {completed_tasks}/{total_tasks} tasks in {execution_time:.2f} seconds")
    logger.info(f"Total cycles: {cycle_count}")
    logger.info("===== SESSION SUMMARY =====")
    logger.info(task_manager.get_session_summary())

    return True