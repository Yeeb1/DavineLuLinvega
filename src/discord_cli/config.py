"""Configuration management for Discord CLI tools."""

import json
import os
from typing import Dict, Optional, Tuple


CONFIG_PATH = os.path.expanduser("~/.config/discord-cli/config.json")


def ensure_config_dir():
    """Ensure the configuration directory exists."""
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)


def load_config():
    """Load the JSON configuration file with all settings."""
    if not os.path.exists(CONFIG_PATH):
        return {
            "webhooks": {},
            "threads": {},
            "settings": {
                "default_webhook": None,
                "default_thread": None,
                "use_threads": False,
                "username": "Yeeb"
            }
        }

    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)

    # Ensure all required keys exist
    if "webhooks" not in config:
        config["webhooks"] = {}
    if "threads" not in config:
        config["threads"] = {}
    if "settings" not in config:
        config["settings"] = {
            "default_webhook": None,
            "default_thread": None,
            "use_threads": False,
            "username": "Yeeb"
        }

    # Ensure username setting exists for existing configs
    if "username" not in config["settings"]:
        config["settings"]["username"] = "Yeeb"

    return config


def save_config(config):
    """Save configuration to JSON file."""
    ensure_config_dir()
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)


def get_default_webhook() -> Optional[str]:
    """Get the default webhook URL."""
    config = load_config()
    default_name = config["settings"].get("default_webhook")
    if default_name and default_name in config["webhooks"]:
        return config["webhooks"][default_name]
    return None


def get_default_thread() -> Optional[str]:
    """Get the default thread ID."""
    config = load_config()
    default_name = config["settings"].get("default_thread")
    if default_name and default_name in config["threads"]:
        return config["threads"][default_name]
    return None


def get_use_threads() -> bool:
    """Check if threads are enabled."""
    config = load_config()
    return config["settings"].get("use_threads", False)


def set_default_webhook(webhook_name: str):
    """Set the default webhook."""
    config = load_config()
    if webhook_name in config["webhooks"]:
        config["settings"]["default_webhook"] = webhook_name
        save_config(config)
        return True
    return False


def set_default_thread(thread_name: str):
    """Set the default thread."""
    config = load_config()
    if thread_name in config["threads"]:
        config["settings"]["default_thread"] = thread_name
        save_config(config)
        return True
    return False


def set_use_threads(enabled: bool):
    """Enable or disable thread usage."""
    config = load_config()
    config["settings"]["use_threads"] = enabled
    save_config(config)


def get_username() -> str:
    """Get the configured username."""
    config = load_config()
    return config["settings"].get("username", "Yeeb")


def set_username(username: str):
    """Set the username."""
    config = load_config()
    config["settings"]["username"] = username
    save_config(config)


def load_webhook_config() -> Tuple[str, Optional[str], bool]:
    """Load webhook configuration from config file."""
    webhook_url = get_default_webhook()
    thread_id = get_default_thread()
    needs_thread = get_use_threads()

    if not webhook_url:
        config = load_config()
        if not config["webhooks"]:
            # No webhooks configured at all - suggest setup
            raise ValueError(
                "No webhooks configured. Run 'dc setup' for quick configuration, "
                "or use 'dc manage add-webhook' to add one manually."
            )
        else:
            # Webhooks exist but no default set
            raise ValueError(
                "No default webhook set. Use 'dc manage set-default-webhook' to choose one."
            )

    return webhook_url, thread_id, needs_thread


def migrate_from_env():
    """Migrate settings from .env file to new config system."""
    env_path = os.path.expanduser("~/.env")
    if not os.path.exists(env_path):
        return

    config = load_config()
    migrated = False

    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith("export DISCORD_WEBHOOK_URL="):
                    webhook_url = line.split("=", 1)[1].strip("'\"")
                    if webhook_url and "migrated" not in config["webhooks"]:
                        config["webhooks"]["migrated"] = webhook_url
                        config["settings"]["default_webhook"] = "migrated"
                        migrated = True

                elif line.startswith("export THREAD_ID="):
                    thread_id = line.split("=", 1)[1].strip("'\"")
                    if thread_id and "migrated" not in config["threads"]:
                        config["threads"]["migrated"] = thread_id
                        config["settings"]["default_thread"] = "migrated"
                        migrated = True

                elif line.startswith("export WEBHOOK_NEEDS_THREAD="):
                    use_threads = line.split("=", 1)[1].strip("'\"").lower() == "true"
                    config["settings"]["use_threads"] = use_threads
                    migrated = True

        if migrated:
            save_config(config)
            print("Migrated configuration from .env file to ~/.config/discord-cli/config.json")
            print("You can now remove the Discord-related entries from ~/.env")

    except Exception as e:
        print(f"Warning: Could not migrate from .env file: {e}")


def show_config():
    """Show current configuration."""
    config = load_config()

    webhook_count = len(config["webhooks"])
    thread_count = len(config["threads"])
    use_threads = config["settings"].get("use_threads", False)
    default_webhook = config["settings"].get("default_webhook")
    default_thread = config["settings"].get("default_thread")
    username = config["settings"].get("username", "Yeeb")

    print("=" * 80)
    print("                🔧 Discord CLI Config")
    print("=" * 80)
    print(f"Config file: {CONFIG_PATH}")
    print("=" * 80)

    # Webhooks section
    print(f"📡 Webhooks: {webhook_count} configured")
    if config["webhooks"]:
        for name, url in config["webhooks"].items():
            is_default = name == default_webhook
            status = "🟢" if is_default else "⚪"
            print(f"  {status} {name}: {url}")
    else:
        print("  ❌ None configured")

    print("-" * 80)

    # Threads section
    thread_status = "🟢 ENABLED" if use_threads else "🔴 DISABLED"
    print(f"🧵 Threads: {thread_count} configured - {thread_status}")
    if config["threads"]:
        for name, thread_id in config["threads"].items():
            is_default = name == default_thread
            status = "🟢" if is_default else "⚪"
            print(f"  {status} {name}: {thread_id}")
    else:
        print("  ❌ None configured")

    print("-" * 80)

    # Settings section
    print("⚙️  Settings:")
    print(f"  👤 Username: {username}")
    print(f"  📡 Default webhook: {default_webhook or 'None'}")
    print(f"  🧵 Default thread: {default_thread or 'None'}")
    print(f"  🔧 Thread usage: {'Enabled' if use_threads else 'Disabled'}")

    print("=" * 80)

    # Status warnings
    warnings = []
    if not config["webhooks"]:
        warnings.append("⚠️  No webhooks configured - use 'dc setup' or 'dc manage add-webhook'")
    elif not default_webhook:
        warnings.append("⚠️  No default webhook set - use 'dc manage set-default-webhook'")

    if use_threads and not config["threads"]:
        warnings.append("⚠️  Thread usage enabled but no threads configured")
    elif use_threads and not default_thread:
        warnings.append("⚠️  Thread usage enabled but no default thread set")

    for warning in warnings:
        print(warning)