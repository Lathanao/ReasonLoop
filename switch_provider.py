# switch_provider.py
#
# python switch_provider.py ollama --model llama2
#
# python switch_provider.py anthropic --key "your-anthropic-api-key" --model "claude-instant-1.2"
#
# python switch_provider.py openai --key "your-openai-api-key" --model "gpt-4"
#


import os
import argparse
import json
from config.settings import update_setting, get_setting, save_settings

def main():
    parser = argparse.ArgumentParser(description="Switch between LLM providers")
    parser.add_argument("provider", choices=["ollama", "anthropic", "openai"],
                        help="LLM provider to use")
    parser.add_argument("--key", help="API key for the provider (if needed)")
    parser.add_argument("--model", help="Model to use")

    args = parser.parse_args()

    # Update provider
    update_setting("LLM_PROVIDER", args.provider)
    print(f"Switched to {args.provider} provider")

    # Update API key if provided
    if args.key and args.provider in ["anthropic", "openai"]:
        key_setting = f"{args.provider.upper()}_API_KEY"
        update_setting(key_setting, args.key)
        print(f"Updated {args.provider} API key")

    # Update model if provided
    if args.model:
        model_setting = f"{args.provider.upper()}_MODEL"
        update_setting(model_setting, args.model)
        print(f"Set model to {args.model}")

    # Update LLM_API_URL and LLM_MODEL for compatibility
    provider_url = get_setting(f"{args.provider.upper()}_API_URL")
    provider_model = get_setting(f"{args.provider.upper()}_MODEL")

    update_setting("LLM_API_URL", provider_url)
    update_setting("LLM_MODEL", provider_model)

    # Save settings
    save_settings()

    # Show current configuration
    print("\nCurrent configuration:")
    print(f"Provider: {get_setting('LLM_PROVIDER')}")
    print(f"API URL: {get_setting('LLM_API_URL')}")
    print(f"Model: {get_setting('LLM_MODEL')}")

    if args.provider == "ollama":
        print("\nTo use Ollama, make sure it's running with:")
        print("  ollama run " + get_setting("OLLAMA_MODEL"))
    elif args.provider == "anthropic":
        key = get_setting("ANTHROPIC_API_KEY")
        print("\nAnthropic API Key:", "*" * (len(key) - 4) + key[-4:] if key else "Not set")
    elif args.provider == "openai":
        key = get_setting("OPENAI_API_KEY")
        print("\nOpenAI API Key:", "*" * (len(key) - 4) + key[-4:] if key else "Not set")

if __name__ == "__main__":
    main()