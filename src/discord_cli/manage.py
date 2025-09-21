"""Discord webhook and thread management commands."""

import sys
from .config import (
    load_config, save_config, set_default_webhook as config_set_default_webhook,
    set_default_thread as config_set_default_thread, set_use_threads, show_config, migrate_from_env,
    get_username, set_username
)


def list_webhooks():
    """List all saved webhooks."""
    config = load_config()
    if not config["webhooks"]:
        print("=" * 60)
        print("           No Webhooks Found")
        print("=" * 60)
        print("Use 'dc manage add-webhook' to add")
        print("or 'dc setup' for quick setup")
        print("=" * 60)
        return

    default_webhook = config["settings"].get("default_webhook")
    webhook_count = len(config["webhooks"])

    print("=" * 80)
    print(f"  📡 Discord Webhooks ({webhook_count} configured)")
    print("=" * 80)

    for i, (name, url) in enumerate(config["webhooks"].items(), 1):
        is_default = name == default_webhook

        # Extract server info from webhook URL
        server_info = "Unknown Server"
        try:
            # Try to get the last part of URL for display
            if "/webhooks/" in url:
                webhook_id = url.split("/webhooks/")[1].split("/")[0]
                server_info = f"ID: {webhook_id}"
        except:
            pass

        # Status indicators
        status = "🟢 DEFAULT" if is_default else "⚪ Available"

        print(f" {i:2}. {status}")
        print(f"     Name: {name}")
        print(f"     Server: {server_info}")
        print(f"     URL: {url}")

        if i < webhook_count:
            print("-" * 80)

    print("=" * 80)

    if not default_webhook:
        print("⚠️  No default webhook set. Use 'dc manage set-default-webhook' to choose one.")


def add_webhook(name, url, set_default=False):
    """Add a new webhook."""
    config = load_config()
    config["webhooks"][name] = url
    if set_default:
        config["settings"]["default_webhook"] = name
    save_config(config)
    print(f"Added webhook '{name}' with URL: {url}")
    if set_default:
        print(f"Set default webhook to '{name}'")


def set_default_webhook_interactive():
    """Set a webhook as the default interactively."""
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
            if config_set_default_webhook(name):
                print(f"Set default webhook to '{name}'")
            else:
                print("Error setting default webhook.")
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
            # Clear default if removing the default webhook
            if config["settings"].get("default_webhook") == name:
                config["settings"]["default_webhook"] = None
            save_config(config)
            print(f"Removed webhook '{name}'")
        else:
            print("Invalid selection.")
    except ValueError:
        print("Invalid input.")


def list_threads():
    """List all saved threads."""
    config = load_config()
    if not config["threads"]:
        print("=" * 60)
        print("           No Threads Found")
        print("=" * 60)
        print("Use 'dc manage add-thread' to add")
        print("or 'dc setup' for quick setup")
        print("=" * 60)
        return

    default_thread = config["settings"].get("default_thread")
    thread_count = len(config["threads"])
    use_threads = config["settings"].get("use_threads", False)

    thread_status = "🟢 ENABLED" if use_threads else "🔴 DISABLED"

    print("=" * 80)
    print(f"  🧵 Discord Threads ({thread_count} configured) - {thread_status}")
    print("=" * 80)

    for i, (name, thread_id) in enumerate(config["threads"].items(), 1):
        is_default = name == default_thread

        # Status indicators
        status = "🟢 DEFAULT" if is_default else "⚪ Available"

        print(f" {i:2}. {status}")
        print(f"     Name: {name}")
        print(f"     Thread ID: {thread_id}")

        if i < thread_count:
            print("-" * 80)

    print("=" * 80)

    if not use_threads:
        print("⚠️  Thread usage is disabled. Use 'dc manage enable-thread' to enable.")
    elif not default_thread:
        print("⚠️  No default thread set. Use 'dc manage set-default-thread' to choose one.")


def add_thread(name, thread_id, force=False):
    """Add a new thread."""
    config = load_config()
    config["threads"][name] = thread_id
    if force:
        config["settings"]["default_thread"] = name
    save_config(config)
    print(f"Added thread '{name}' with ID: {thread_id}")
    if force:
        print(f"Set default thread to '{name}'")


def set_default_thread_interactive():
    """Set a thread as the default interactively."""
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
            if config_set_default_thread(name):
                print(f"Set default thread to '{name}'")
            else:
                print("Error setting default thread.")
        else:
            print("Invalid selection.")
    except ValueError:
        print("Invalid input.")


def enable_thread_ids():
    """Enable thread IDs for webhooks."""
    set_use_threads(True)
    print("Thread IDs are now enabled for webhooks.")


def disable_thread_ids():
    """Disable thread IDs for webhooks."""
    set_use_threads(False)
    print("Thread IDs are now disabled for webhooks.")


def show_username():
    """Show current username."""
    username = get_username()
    print(f"Current username: {username}")


def set_username_interactive():
    """Set username interactively."""
    current = get_username()
    print(f"Current username: {current}")
    new_username = input(f"Enter new username [{current}]: ").strip()

    if not new_username:
        print("Username unchanged.")
        return

    set_username(new_username)
    print(f"Username updated to: {new_username}")
    print("This will appear in Discord as '{username} - {suffix}' for different commands.")


def main():
    """Main entry point for dcmanage command."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  dcmanage list-webhooks")
        print("  dcmanage add-webhook <name> <url> [--default]")
        print("  dcmanage set-default-webhook")
        print("  dcmanage remove-webhook")
        print("  dcmanage list-threads")
        print("  dcmanage add-thread <name> <thread_id> [--force]")
        print("  dcmanage set-default-thread")
        print("  dcmanage enable-thread")
        print("  dcmanage disable-thread")
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
        sys.exit(1)