#!/usr/bin/env python3
"""
ReasonLoop - An autonomous task execution system
Entry point for the application
"""

import argparse
import logging
import sys
from config.settings import DEFAULT_OBJECTIVE
from config.logging_config import setup_logging
from core.execution_loop import run_execution_loop

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="ReasonLoop - Autonomous task execution system")
    parser.add_argument("--objective", "-o", type=str, default=DEFAULT_OBJECTIVE,
                        help="The objective to accomplish")
    parser.add_argument("--model", "-m", type=str, default=None,
                        help="Override the default LLM model")
    parser.add_argument("--template", "-t", type=str, default=None,
                        help="Prompt template to use (default_tasks, marketing_insights, propensity_modeling)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable verbose logging")
    parser.add_argument("--config", "-c", type=str, default=None,
                        help="Path to custom config file")
    return parser.parse_args()

def main():
    """Main entry point"""
    args = parse_arguments()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)

    logger = logging.getLogger(__name__)
    logger.info("Starting ReasonLoop")
    logger.info(f"Objective: {args.objective}")

    # Override settings if needed
    if args.model:
        from config.settings import update_setting
        update_setting("LLM_MODEL", args.model)
        logger.info(f"Using model: {args.model}")

    if args.template:
        from config.settings import update_setting
        update_setting("PROMPT_TEMPLATE", args.template)
        logger.info(f"Using prompt template: {args.template}")

    # Run the main execution loop
    try:
        run_execution_loop(args.objective)
        logger.info("Execution completed successfully")
        return 0
    except KeyboardInterrupt:
        logger.info("Execution interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Execution failed: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())