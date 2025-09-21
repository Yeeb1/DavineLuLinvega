"""Quick setup wizard for Discord CLI."""

import re
from typing import Optional

from .config import load_config, save_config
from .discord_discovery import validate_webhook_url, discover_threads_from_webhook


def is_valid_webhook_url(url: str) -> bool:
    """Check if URL matches Discord webhook pattern."""
    pattern = r'https://discord\.com/api/webhooks/\d+/[a-zA-Z0-9_-]+'
    return bool(re.match(pattern, url))


def get_webhook_input() -> Optional[str]:
    """Get webhook URL from user with validation."""
    print("Discord Webhook Setup")
    print("=" * 50)
    print()
    print("To get your Discord webhook URL:")
    print("1. Go to your Discord server")
    print("2. Right-click on the channel you want to use")
    print("3. Select 'Edit Channel'")
    print("4. Go to 'Integrations' tab")
    print("5. Click 'Create Webhook'")
    print("6. Copy the webhook URL")
    print()

    while True:
        webhook_url = input("Enter your Discord webhook URL (or 'quit' to exit): ").strip()

        if webhook_url.lower() == 'quit':
            return None

        if not webhook_url:
            print("Please enter a webhook URL.")
            continue

        if not is_valid_webhook_url(webhook_url):
            print("Invalid webhook URL format. Please enter a valid Discord webhook URL.")
            continue

        print("Validating webhook...")
        if validate_webhook_url(webhook_url):
            print("✓ Webhook validated successfully!")
            return webhook_url
        else:
            print("✗ Could not validate webhook. Please check the URL and try again.")
            print("Make sure the webhook is active and accessible.")


def get_webhook_name(webhook_url: str) -> str:
    """Get a name for the webhook from user."""
    # Try to discover info about the webhook
    channel_info, _ = discover_threads_from_webhook(webhook_url)

    if channel_info:
        print(f"\nDetected: {channel_info}")
        suggested_name = channel_info.lower().replace(' - ', '-').replace(' ', '-')
        suggested_name = re.sub(r'[^a-zA-Z0-9-_]', '', suggested_name)
        print(f"Suggested name: {suggested_name}")
    else:
        suggested_name = "main"

    while True:
        name = input(f"Enter a name for this webhook [{suggested_name}]: ").strip()
        if not name:
            name = suggested_name

        # Validate name (alphanumeric, hyphens, underscores only)
        if re.match(r'^[a-zA-Z0-9_-]+$', name):
            return name
        else:
            print("Name can only contain letters, numbers, hyphens, and underscores.")


def setup_threads(webhook_url: str) -> Optional[str]:
    """Setup thread configuration."""
    print("\nThread Configuration")
    print("=" * 50)

    print("Threads allow you to send messages to specific discussion topics within a channel.")
    print()

    # Try to discover threads
    channel_info, threads = discover_threads_from_webhook(webhook_url)

    if threads:
        print("Available threads found:")
        for i, thread in enumerate(threads, 1):
            print(f"  {i}. {thread.get('name', 'Unnamed Thread')} (ID: {thread.get('id')})")
        print(f"  {len(threads) + 1}. Enter custom thread ID")
        print(f"  {len(threads) + 2}. Skip thread setup")

        while True:
            try:
                choice = input(f"Select a thread [1-{len(threads) + 2}]: ").strip()
                if not choice:
                    continue

                choice_num = int(choice)
                if 1 <= choice_num <= len(threads):
                    selected_thread = threads[choice_num - 1]
                    return selected_thread.get('id')
                elif choice_num == len(threads) + 1:
                    break  # Fall through to manual entry
                elif choice_num == len(threads) + 2:
                    return None  # Skip threads
                else:
                    print(f"Please enter a number between 1 and {len(threads) + 2}")
            except ValueError:
                print("Please enter a valid number")
    else:
        print("No threads were automatically discovered.")
        print("You can:")
        print("  1. Enter a thread ID manually")
        print("  2. Skip thread setup (send to main channel)")

        while True:
            choice = input("Choose an option [1-2]: ").strip()
            if choice == "1":
                break
            elif choice == "2":
                return None
            else:
                print("Please enter 1 or 2")

    # Manual thread ID entry
    print()
    print("To get a thread ID:")
    print("1. Right-click on the thread in Discord")
    print("2. Select 'Copy Thread ID' (you may need to enable Developer Mode)")
    print()

    while True:
        thread_id = input("Enter thread ID (or press Enter to skip): ").strip()
        if not thread_id:
            return None

        if thread_id.isdigit() and len(thread_id) >= 17:  # Discord IDs are typically 17-19 digits
            return thread_id
        else:
            print("Invalid thread ID. Discord thread IDs are long numbers (17+ digits).")


def get_thread_name(thread_id: str) -> str:
    """Get a name for the thread."""
    suggested_name = "main"

    while True:
        name = input(f"Enter a name for this thread [{suggested_name}]: ").strip()
        if not name:
            name = suggested_name

        if re.match(r'^[a-zA-Z0-9_-]+$', name):
            return name
        else:
            print("Name can only contain letters, numbers, hyphens, and underscores.")


def quick_setup():
    """Run the quick setup wizard."""
    print("🚀 Discord CLI Quick Setup")
    print("=" * 50)
    print()
    print("This wizard will help you set up your first Discord webhook and thread.")
    print()

    # Get webhook
    webhook_url = get_webhook_input()
    if not webhook_url:
        print("Setup cancelled.")
        return

    # Get webhook name
    webhook_name = get_webhook_name(webhook_url)

    # Setup threads
    thread_id = setup_threads(webhook_url)
    thread_name = None
    if thread_id:
        thread_name = get_thread_name(thread_id)

    # Save configuration
    config = load_config()

    # Add webhook
    config["webhooks"][webhook_name] = webhook_url
    config["settings"]["default_webhook"] = webhook_name

    # Add thread if provided
    if thread_id and thread_name:
        config["threads"][thread_name] = thread_id
        config["settings"]["default_thread"] = thread_name
        config["settings"]["use_threads"] = True
    else:
        config["settings"]["use_threads"] = False

    save_config(config)

    print()
    print("✅ Setup Complete!")
    print("=" * 50)
    print(f"Webhook '{webhook_name}' has been configured as your default.")
    if thread_id:
        print(f"Thread '{thread_name}' has been configured as your default.")
        print("Thread usage is enabled.")
    else:
        print("No thread configured - messages will be sent to the main channel.")
    print()
    print("You can now use:")
    print(f"  dc log -c 'Hello from setup!' echo 'Setup successful!'")
    print(f"  dc send somefile.txt")
    print(f"  dc clip")
    print()
    print("Use 'dc manage show-config' to view your configuration.")
    print("Use 'dc manage' to see all management options.")