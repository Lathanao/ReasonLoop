"""
Task manager for creating, validating, and executing tasks
"""

import logging
import json
import re
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from models.task import Task
from models.result import Result
from abilities.ability_registry import execute_ability
from config.settings import get_setting
from utils.json_parser import extract_json_from_text
from utils.prompt_templates import get_prompt_template
from config.settings import get_setting

logger = logging.getLogger(__name__)

class TaskManager:
    """Manages tasks in the system"""

    def __init__(self, objective: str):
        self.tasks: List[Task] = []
        self.next_task_id = 1
        self.session_summary = ""
        self.objective = objective  # Store the objective as an instance attribute"

    def create_initial_tasks(self) -> List[Task]:
        """Create the initial task list using AI"""
        from utils.prompt_logger import log_prompt

        logger.info("Creating initial task list")

        # Get the selected prompt template
        template_name = get_setting("PROMPT_TEMPLATE", "default_tasks")
        prompt = get_prompt_template(template_name, objective=self.objective)

        logger.debug(f"Using prompt template: {template_name}")
        logger.debug(f"Sending task creation prompt: {prompt[:100]}...")

        # Execute the ability
        response = execute_ability("text-completion", prompt, task_id=0)  # task_id 0 for initial tasks

        # Log the template usage
        log_prompt(
            prompt=prompt,
            response=response,
            template_name=template_name,
            ability="text-completion",
            task_id=0,
            metadata={"objective": self.objective}
        )

         # Rest of the function remains the same

        try:
            # Try to extract JSON from the response
            logger.debug(f"Raw response: {response}")
            json_data = extract_json_from_text(response)

            if json_data:
                # Convert to Task objects
                tasks = [Task.from_dict(item) for item in json_data]
                logger.info(f"Created {len(tasks)} initial tasks")
                self.tasks = tasks
                return tasks
            else:
                raise ValueError("No valid JSON found in response")
        except Exception as e:
            logger.error(f"Error parsing task list: {str(e)}")
            logger.error(f"Raw response: {response}")
            return self._generate_fallback_tasks(response)

    def _generate_fallback_tasks(self, original_response: str) -> List[Task]:
        """Generate fallback tasks when parsing fails"""
        logger.info("Generating fallback tasks")

        try:
            # Try to extract task ideas from the original response
            prompt = f"""
            I need to convert this text into a properly formatted task list:

            {original_response}

            Extract the main tasks mentioned in the text and format them as a JSON array with these fields:
            - id: sequential number starting at 1
            - task: detailed description of what to do
            - ability: assign the most appropriate ability from: 'text-completion', 'web-search', 'web-scrape', 'mysql-schema', or 'mysql-query'
            - dependent_task_ids: empty array for now
            - status: 'incomplete' for all tasks

            Return ONLY the JSON array without any explanation.
            """

            logger.debug("Attempting to generate structured tasks from unstructured response")
            structured_response = execute_ability("text-completion", prompt)

            # Try to extract JSON again
            json_data = extract_json_from_text(structured_response)

            if json_data:
                tasks = [Task.from_dict(item) for item in json_data]
                logger.info(f"Successfully created {len(tasks)} tasks from unstructured response")
                self.tasks = tasks
                return tasks

            # If still failing, create a minimal task list
            logger.warning("Could not extract structured tasks, creating minimal task list")
            return self._create_minimal_task_list()
        except Exception as e:
            logger.error(f"Error in fallback task generation: {str(e)}")
            return self._create_minimal_task_list()

    def _create_minimal_task_list(self) -> List[Task]:
        """Create a minimal task list based on the objective"""
        logger.info("Creating minimal task list")

        # Create a simple two-task list
        tasks = [
            Task(
                id=1,
                task=f"Research information related to: {self.objective}",
                ability="web-search",
                dependent_task_ids=[],
                status="incomplete"
            ),
            Task(
                id=2,
                task=f"Create a final summary report for the objective: {self.objective}",
                ability="text-completion",
                dependent_task_ids=[1],
                status="incomplete"
            )
        ]

        logger.info(f"Created minimal task list with {len(tasks)} tasks")
        # self.tasks = tasks
        return tasks

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Find a task by its ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def find_next_task(self) -> Optional[Task]:
        """Find the next executable task"""
        logger.debug("Finding next task to execute")

        for task in self.tasks:
            if task.status == "incomplete":
                # Check if all dependencies are complete
                can_execute = True
                for dep_id in task.dependent_task_ids:
                    dependent_task = self.get_task_by_id(dep_id)
                    if not dependent_task or dependent_task.status != "complete":
                        can_execute = False
                        logger.debug(f"Task #{task.id} has incomplete dependency #{dep_id}")
                        break

                if can_execute:
                    logger.debug(f"Selected task #{task.id} to execute next")
                    return task

        logger.debug("No executable tasks found")
        return None

    def execute_task(self, task: Task) -> Result:
        """Execute a task and return the result"""
        from utils.prompt_logger import log_prompt

        # Get task description based on template type
        task_description = getattr(task, "task",
                        getattr(task, "insight",
                        getattr(task, "action_item", str(task.id))))

        logger.info(f"Executing task #{task.id}: {task_description}")
        start_time = time.time()

        # Prepare context from dependent tasks
        dependent_outputs = ""
        if task.dependent_task_ids:
            logger.debug(f"Task has dependencies: {task.dependent_task_ids}")

            for dep_id in task.dependent_task_ids:
                dependent_task = self.get_task_by_id(dep_id)
                if dependent_task and dependent_task.output:
                    logger.debug(f"Adding output from dependency #{dep_id}")
                    dependent_outputs += f"\n\nOutput from task #{dep_id}:\n{dependent_task.output[:500]}..."

        # Prepare prompt for text-completion
        task_prompt = f"Complete this task: {task_description}\nObjective: {self.objective}"

        if dependent_outputs:
            task_prompt += f"\n\nUse this information from previous tasks:{dependent_outputs}"

        try:
            # Execute the ability
            if task.ability == "text-completion":
                output = execute_ability(task.ability, task_prompt, task_id=task.id)
            else:
                # For other abilities, extract parameters from the task description
                ability_input = task_description
                output = execute_ability(task.ability, ability_input, task_id=task.id)

            # Log the task execution
            log_prompt(
                prompt=task_prompt,
                response=output,
                ability=task.ability,
                task_id=task.id,
                metadata={
                    "task_description": task_description,
                    "dependent_task_ids": task.dependent_task_ids,
                    "execution_time": time.time() - start_time
                }
            )

            # Update task status
            task.mark_complete(output)

            # Add to session summary
            self.session_summary += f"\n\nTask {task.id} - {task.task}:\n{output}"

            # Create result
            execution_time = time.time() - start_time
            result = Result(
                task_id=task.id,
                content=output,
                success=True,
                execution_time=execution_time
            )

            logger.info(f"Task #{task.id} completed in {execution_time:.2f}s")
            return result

        except Exception as e:
            logger.error(f"Error executing task #{task.id}: {str(e)}")
            return Result.error_result(task.id, str(e))

    def execute_task_with_retry(self, task: Task) -> Result:
        """Execute a task with retry logic"""
        max_retries = get_setting("MAX_RETRIES", 2)
        retry_delay = get_setting("RETRY_DELAY", 2.0)

        for attempt in range(max_retries + 1):
            try:
                result = self.execute_task(task)
                if result.success:
                    return result

                # If execution failed but didn't raise an exception
                if attempt < max_retries:
                    logger.warning(f"Task #{task.id} failed, retrying ({attempt+1}/{max_retries}): {result.error}")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"Task #{task.id} failed after {max_retries} retries: {result.error}")
                    return result

            except Exception as e:
                if attempt < max_retries:
                    logger.warning(f"Task #{task.id} failed with exception, retrying ({attempt+1}/{max_retries}): {str(e)}")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"Task #{task.id} failed after {max_retries} retries: {str(e)}")
                    return Result.error_result(task.id, str(e))

        # Should never reach here, but just in case
        return Result.error_result(task.id, "Maximum retries exceeded")

    def print_task_list(self) -> None:
        """Print the current task list"""
        logger.info("===== CURRENT TASK LIST =====")
        for task in self.tasks:
            logger.info(str(task))
        logger.info("=============================")

    def get_session_summary(self) -> str:
        """Get the current session summary"""
        return self.session_summary