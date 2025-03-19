"""
ReasonLoop - A modular AI agent system
"""

import argparse
import logging
import time
from datetime import datetime
import os

from config.logging_config import setup_logging
from config.settings import get_setting, update_setting
from core.execution_loop import run_execution_loop
from abilities.ability_registry import list_abilities
from utils.metrics import MetricsManager
from utils.llm_utils import test_llm_service

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

    # Initialize metrics
    metrics = MetricsManager()
    session_id = metrics.start_session()
    logger.info(f"Started metrics session: {session_id}")

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

    # Test LLM service before running
    llm_success, llm_message = test_llm_service()
    if not llm_success:
        logger.error(f"LLM service test failed: {llm_message}")
        print(f"\nError: LLM service is not available. {llm_message}")
        return

    # Run the execution loop
    try:
        start_time = time.time()
        success = run_execution_loop(objective)
        end_time = time.time()

        # Print execution summary
        if success:
            print(f"\nExecution completed in {end_time - start_time:.2f} seconds")
        else:
            print("\nExecution failed")

        # Save metrics
        metrics.save_session()
        print(f"Metrics saved to {metrics._metrics_dir} directory")

    except KeyboardInterrupt:
        logger.info("Execution interrupted by user")
        print("\nExecution interrupted by user")
        metrics.save_session()
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}", exc_info=True)
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()