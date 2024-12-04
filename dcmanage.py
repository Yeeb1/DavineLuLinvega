#!/usr/bin/env python3

import json
import os
import sys

CONFIG_PATH = os.path.expanduser("~/.config/dc_webhooks.json")
ENV_PATH = os.path.expanduser("~/.env")


def load_config():
    """Load the JSON configuration file, ensuring 'webhooks' and 'threads' keys exist."""
    if not os.path.exists(CONFIG_PATH):
        return {"webhooks": {}, "threads": {}}

    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)

    if "webhooks" not in config:
        config["webhooks"] = {}
    if "threads" not in config:
        config["threads"] = {}

    return config


def save_config(config):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)


def update_env_variable(key, value):
    """Update or add an environment variable in ~/.env and notify user to source it."""
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, 'r') as f:
            lines = f.readlines()
    else:
        lines = []
    with open(ENV_PATH, 'w') as f:
        found = False
        for line in lines:
            if line.startswith(f"export {key}"):
                f.write(f"export {key}='{value}'\n")
                found = True
            else:
                f.write(line)
        if not found:
            f.write(f"export {key}='{value}'\n")
    print(f"Updated {key} in {ENV_PATH}. Please run 'source ~/.env' to apply changes.")


def list_webhooks():
    """List all saved webhooks."""
    config = load_config()
    if not config["webhooks"]:
        print("No webhooks saved.")
        return
    print("Saved Webhooks:")
    for name, url in config["webhooks"].items():
        print(f"- {name}: {url}")


def add_webhook(name, url, set_default=False):
    """Add a new webhook."""
    config = load_config()
    config["webhooks"][name] = url
    save_config(config)
    print(f"Added webhook '{name}' with URL: {url}")
    if set_default:
        update_env_variable("DISCORD_WEBHOOK_URL", url)
        print(f"Set default webhook to '{name}'")


def set_default_webhook():
    """Set a webhook as the default by updating the ~/.env file."""
    config = load_config()
    if not config["webhooks"]:
        print("No webhooks available to set as default.")
        return
    print("Available Webhooks:")
    webhook_names = list(config["webhooks"].keys())
    for idx, name in enumerate(webhook_names):
        print(f"{idx + 1}) {name}: {config['webhooks'][name]}")
    try:
        selection = int(input("Select a webhook to set as default: "))
        if 1 <= selection <= len(webhook_names):
            name = webhook_names[selection - 1]
            update_env_variable("DISCORD_WEBHOOK_URL", config["webhooks"][name])
            print(f"Set default webhook to '{name}'")
        else:
            print("Invalid selection.")
    except ValueError:
        print("Invalid input.")


def remove_webhook():
    """Remove a saved webhook."""
    config = load_config()
    if not config["webhooks"]:
        print("No webhooks to remove.")
        return
    print("Available Webhooks:")
    webhook_names = list(config["webhooks"].keys())
    for idx, name in enumerate(webhook_names):
        print(f"{idx + 1}) {name}: {config['webhooks'][name]}")
    try:
        selection = int(input("Select a webhook to remove: "))
        if 1 <= selection <= len(webhook_names):
            name = webhook_names[selection - 1]
            del config["webhooks"][name]
            save_config(config)
            print(f"Removed webhook '{name}'")
        else:
            print("Invalid selection.")
    except ValueError:
        print("Invalid input.")


def list_threads():
    config = load_config()
    if not config["threads"]:
        print("No threads saved.")
        return
    print("Saved Threads:")
    for name, thread_id in config["threads"].items():
        print(f"- {name}: {thread_id}")


def add_thread(name, thread_id, force=False):
    config = load_config()
    config["threads"][name] = thread_id
    save_config(config)
    print(f"Added thread '{name}' with ID: {thread_id}")
    if force:
        update_env_variable("THREAD_ID", thread_id)
        print(f"Set default thread to '{name}'")


def set_default_thread():
    """Set a thread as the default by updating the ~/.env file."""
    config = load_config()
    if not config["threads"]:
        print("No threads available to set as default.")
        return
    print("Available Threads:")
    thread_names = list(config["threads"].keys())
    for idx, name in enumerate(thread_names):
        print(f"{idx + 1}) {name}: {config['threads'][name]}")
    try:
        selection = int(input("Select a thread to set as default: "))
        if 1 <= selection <= len(thread_names):
            name = thread_names[selection - 1]
            update_env_variable("THREAD_ID", config["threads"][name])
            print(f"Set default thread to '{name}'")
        else:
            print("Invalid selection.")
    except ValueError:
        print("Invalid input.")


def enable_thread_ids():
    update_env_variable("WEBHOOK_NEEDS_THREAD", "true")
    print("Thread IDs are now enabled for webhooks.")


def disable_thread_ids():
    update_env_variable("WEBHOOK_NEEDS_THREAD", "false")
    print("Thread IDs are now disabled for webhooks.")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  dcmanage.py list-webhooks")
        print("  dcmanage.py add-webhook <name> <url> [--default]")
        print("  dcmanage.py set-default-webhook")
        print("  dcmanage.py remove-webhook")
        print("  dcmanage.py list-threads")
        print("  dcmanage.py add-thread <name> <thread_id> [--force]")
        print("  dcmanage.py set-default-thread")
        print("  dcmanage.py enable-thread")
        print("  dcmanage.py disable-thread")
        sys.exit(1)

    command = sys.argv[1]

    if command == "list-webhooks":
        list_webhooks()
    elif command == "add-webhook" and len(sys.argv) >= 4:
        name = sys.argv[2]
        url = sys.argv[3]
        set_default = "--default" in sys.argv
        add_webhook(name, url, set_default)
    elif command == "set-default-webhook":
        set_default_webhook()
    elif command == "remove-webhook":
        remove_webhook()
    elif command == "list-threads":
        list_threads()
    elif command == "add-thread" and len(sys.argv) >= 4:
        name = sys.argv[2]
        thread_id = sys.argv[3]
        force = "--force" in sys.argv
        add_thread(name, thread_id, force)
    elif command == "set-default-thread":
        set_default_thread()
    elif command == "enable-thread":
        enable_thread_ids()
    elif command == "disable-thread":
        disable_thread_ids()
    else:
        print("Invalid command or arguments.")
        print("Usage:")
        print("  dcmanage.py list-webhooks")
        print("  dcmanage.py add-webhook <name> <url> [--default]")
        print("  dcmanage.py set-default-webhook")
        print("  dcmanage.py remove-webhook")
        print("  dcmanage.py list-threads")
        print("  dcmanage.py add-thread <name> <thread_id> [--force]")
        print("  dcmanage.py set-default-thread")
        print("  dcmanage.py enable-thread")
        print("  dcmanage.py disable-thread")
        sys.exit(1)


if __name__ == "__main__":
    main()
