"""
Utility to view and analyze prompt logs
"""

import os
import json
import argparse
from typing import List, Dict, Any, Optional
from datetime import datetime

def list_prompt_logs(log_dir: str = "logs/prompts", limit: int = 10) -> List[str]:
    """List the most recent prompt log files"""
    if not os.path.exists(log_dir):
        print(f"Log directory {log_dir} does not exist")
        return []

    files = [f for f in os.listdir(log_dir) if f.endswith('.json')]
    files.sort(reverse=True)  # Most recent first
    return files[:limit]

def view_prompt_log(filename: str, log_dir: str = "logs/prompts") -> Optional[Dict[str, Any]]:
    """View a specific prompt log"""
    filepath = os.path.join(log_dir, filename)
    if not os.path.exists(filepath):
        print(f"Log file {filepath} does not exist")
        return None

    with open(filepath, 'r') as f:
        return json.load(f)

def search_prompt_logs(
    search_term: str,
    log_dir: str = "logs/prompts",
    search_prompts: bool = True,
    search_responses: bool = True
) -> List[str]:
    """Search prompt logs for a specific term"""
    if not os.path.exists(log_dir):
        print(f"Log directory {log_dir} does not exist")
        return []

    matching_files = []

    for filename in os.listdir(log_dir):
        if not filename.endswith('.json'):
            continue

        filepath = os.path.join(log_dir, filename)
        try:
            with open(filepath, 'r') as f:
                log_data = json.load(f)

            # Search in prompt and/or response
            if (search_prompts and search_term.lower() in log_data.get("prompt", "").lower()) or \
               (search_responses and search_term.lower() in log_data.get("response", "").lower()):
                matching_files.append(filename)
        except Exception as e:
            print(f"Error reading {filepath}: {str(e)}")

    return matching_files

def main():
    """Command line interface for prompt viewer"""
    parser = argparse.ArgumentParser(description="ReasonLoop Prompt Viewer")
    parser.add_argument("--list", "-l", action="store_true", help="List recent prompt logs")
    parser.add_argument("--view", "-v", type=str, help="View a specific prompt log file")
    parser.add_argument("--search", "-s", type=str, help="Search prompt logs for a term")
    parser.add_argument("--limit", type=int, default=10, help="Limit the number of results")
    parser.add_argument("--dir", "-d", type=str, default="logs/prompts", help="Prompt log directory")

    args = parser.parse_args()

    if args.list:
        files = list_prompt_logs(args.dir, args.limit)
        print(f"Recent prompt logs ({len(files)}):")
        for i, file in enumerate(files, 1):
            print(f"{i}. {file}")

    elif args.view:
        log_data = view_prompt_log(args.view, args.dir)
        if log_data:
            print(f"Timestamp: {log_data.get('timestamp')}")
            print(f"Template: {log_data.get('template_name')}")
            print(f"Ability: {log_data.get('ability')}")
            print(f"Task ID: {log_data.get('task_id')}")
            print("\nPROMPT:")
            print("=" * 80)
            print(log_data.get('prompt', ''))
            print("\nRESPONSE:")
            print("=" * 80)
            print(log_data.get('response', ''))

    elif args.search:
        files = search_prompt_logs(args.search, args.dir)
        print(f"Found {len(files)} logs containing '{args.search}':")
        for i, file in enumerate(files[:args.limit], 1):
            print(f"{i}. {file}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()