# ReasonLoop
The code is an AI-driven task automation system.
ReasonLoop is a lightweight, autonomous task execution system that breaks down complex objectives into manageable tasks and executes them sequentially. It leverages language models and specialized abilities to accomplish user-defined goals with minimal human intervention.

## Overview

ReasonLoop follows a cyclical reasoning process:

1. **Task Planning**: Analyzes the objective and creates a structured task list
2. **Task Execution**: Executes tasks in dependency order using specialized abilities
3. **Context Management**: Maintains context between tasks for coherent reasoning
4. **Result Synthesis**: Combines task outputs into a comprehensive summary

## Features

- **Modular Ability System**: Easily add, remove, or modify capabilities
- **Dependency Management**: Tasks can depend on outputs from previous tasks
- **Flexible Configuration**: Configure via environment variables or command line
- **Robust Error Handling**: Automatic retries and graceful fallbacks
- **Comprehensive Logging**: Detailed execution logs for debugging

## Abilities

ReasonLoop comes with several built-in abilities:

- **Text Completion**: Reasoning, analysis, and synthesis using LLMs
- **Web Search**: Finding information online via DuckDuckGo
- **Web Scraping**: Extracting content from specific URLs
- **Database Queries**: Exploring database schemas and executing SQL queries

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/reasonloop.git
cd reasonloop

# Install dependencies
pip install -r requirements.txt


## Usage

```bash
# Basic usage
python main.py --objective "Create a 3-day itinerary for Bangkok"

# With custom model and verbose logging
python main.py --objective "Analyze sales data" --model llama3 --verbose
```

## Configuration

```
# LLM configuration
export REASONLOOP_LLM_MODEL="llama3"
export REASONLOOP_LLM_TEMPERATURE="0.1"

# Database configuration
export REASONLOOP_DB_HOST="localhost"
export REASONLOOP_DB_USER="username"
export REASONLOOP_DB_PASSWORD="password"
export REASONLOOP_DB_NAME="database"

# Web search configuration
export REASONLOOP_WEB SEARCH_ENABLED="true"
export REASONLOOP_WEB SEARCH_RESULTS="5"
```

# Project Structure
reasonloop/
├── abilities/            # Individual capabilities
│   ├── ability_registry.py
│   ├── text_completion.py
│   ├── Web Search.py
│   ├── web_scrape.py
│   └── mysql_abilities.py
├── config/               # Configuration settings
│   ├── settings.py
│   └── logging_config.py
├── core/                 # Core execution logic
│   ├── execution_loop.py
│   └── task_manager.py
├── models/               # Data models
│   ├── task.py
│   └── result.py
├── utils/                # Utility functions
│   └── json_parser.py
├── logs/                 # Log files (created at runtime)
├── main.py               # Entry point
└── requirements.txt      # Dependencies

# Extending ReasonLoop
Adding a New Ability

    Create a new file in the abilities/ directory
    Implement your ability function
    Register it with the ability registry
    Update the task creation prompt in core/task_manager.py


    Claude Sonnet 3.7

markdown

Copy Code
# ReasonLoop

ReasonLoop is a lightweight, autonomous task execution system that breaks down complex objectives into manageable tasks and executes them sequentially. It leverages language models and specialized abilities to accomplish user-defined goals with minimal human intervention.

## Overview

ReasonLoop follows a cyclical reasoning process:

1. **Task Planning**: Analyzes the objective and creates a structured task list
2. **Task Execution**: Executes tasks in dependency order using specialized abilities
3. **Context Management**: Maintains context between tasks for coherent reasoning
4. **Result Synthesis**: Combines task outputs into a comprehensive summary

## Features

- **Modular Ability System**: Easily add, remove, or modify capabilities
- **Dependency Management**: Tasks can depend on outputs from previous tasks
- **Flexible Configuration**: Configure via environment variables or command line
- **Robust Error Handling**: Automatic retries and graceful fallbacks
- **Comprehensive Logging**: Detailed execution logs for debugging

## Abilities

ReasonLoop comes with several built-in abilities:

- **Text Completion**: Reasoning, analysis, and synthesis using LLMs
- **Web Search**: Finding information online via DuckDuckGo
- **Web Scraping**: Extracting content from specific URLs
- **Database Queries**: Exploring database schemas and executing SQL queries

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/reasonloop.git
cd reasonloop

# Install dependencies
pip install -r requirements.txt

Usage

bash

Copy Code
# Basic usage
python main.py --objective "Create a 3-day itinerary for Bangkok"

# With custom model and verbose logging
python main.py --objective "Analyze sales data" --model llama3 --verbose

Configuration

ReasonLoop can be configured via environment variables:

bash

Copy Code
# LLM configuration
export REASONLOOP_LLM_MODEL="llama3"
export REASONLOOP_LLM_TEMPERATURE="0.1"

# Database configuration
export REASONLOOP_DB_HOST="localhost"
export REASONLOOP_DB_USER="username"
export REASONLOOP_DB_PASSWORD="password"
export REASONLOOP_DB_NAME="database"

# Web search configuration
export REASONLOOP_WEB SEARCH_ENABLED="true"
export REASONLOOP_WEB SEARCH_RESULTS="5"

Project Structure

reasonloop/
├── abilities/            # Individual capabilities
│   ├── ability_registry.py
│   ├── text_completion.py
│   ├── Web Search.py
│   ├── web_scrape.py
│   └── mysql_abilities.py
├── config/               # Configuration settings
│   ├── settings.py
│   └── logging_config.py
├── core/                 # Core execution logic
│   ├── execution_loop.py
│   └── task_manager.py
├── models/               # Data models
│   ├── task.py
│   └── result.py
├── utils/                # Utility functions
│   └── json_parser.py
├── logs/                 # Log files (created at runtime)
├── main.py               # Entry point
└── requirements.txt      # Dependencies

Extending ReasonLoop
Adding a New Ability

    Create a new file in the abilities/ directory
    Implement your ability function
    Register it with the ability registry
    Update the task creation prompt in core/task_manager.py

Example:

python

Copy Code
# abilities/image_generation.py
def image_generation_ability(prompt: str) -> str:
    # Implementation here
    return "URL to generated image"

# Register this ability
from abilities.ability_registry import register_ability
register_ability("image-generation", image_generation_ability)

Use Cases

    Research Assistant: Gather and synthesize information on specific topics
    Data Analysis: Query databases and analyze results
    Content Creation: Generate structured content based on research
    Task Automation: Break down complex objectives into executable steps

Requirements

    Python 3.8+
    Required packages listed in requirements.txt
    Internet connection for web-based abilities
    MySQL database for database abilities (optional)

License

MIT License
Acknowledgements

ReasonLoop is inspired by BabyCatAGI (https://replit.com/@YoheiNakajima/BabyCatAGI#main.py), a fork form BabyAGI and other autonomous agent frameworks that leverage language models for task execution.

Note: ReasonLoop is designed for educational and research purposes. Always review the outputs and ensure they meet your requirements before using them in production environments.