"""
File operation abilities for saving agent definitions
"""

import os
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

def write_file_ability(content: str, filename: Optional[str] = None, directory: str = "templates/created") -> str:
    """
    Write content to a file in the specified directory

    Args:
        content: The content to write to the file
        filename: Optional filename (if None, will generate based on content)
        directory: Directory to save the file (default: templates/created)

    Returns:
        Path to the created file or error message
    """
    # Create directory if it doesn't exist
    if not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
        except Exception as e:
            logger.error(f"Failed to create directory {directory}: {str(e)}")
            return f"Error: Failed to create directory {directory}: {str(e)}"

    # Generate filename if not provided
    if not filename:
        # Try to extract name from YAML frontmatter
        try:
            if "---" in content:
                frontmatter = content.split("---")[1]
                for line in frontmatter.split("\n"):
                    if line.strip().startswith("name:"):
                        name = line.split("name:")[1].strip()
                        filename = f"{name}.md"
                        break
        except Exception:
            pass

        # If still no filename, generate a generic one
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"agent_definition_{timestamp}.md"

    # Ensure filename has .md extension
    if not filename.endswith(".md"):
        filename += ".md"

    # Write content to file
    filepath = os.path.join(directory, filename)
    try:
        with open(filepath, 'w') as f:
            f.write(content)
        logger.info(f"Successfully wrote file: {filepath}")
        return f"Successfully wrote agent definition to {filepath}"
    except Exception as e:
        logger.error(f"Failed to write file {filepath}: {str(e)}")
        return f"Error: Failed to write file {filepath}: {str(e)}"

# Register the ability
if __name__ != "__main__":
    from abilities.ability_registry import register_ability
    register_ability("write-file", write_file_ability)