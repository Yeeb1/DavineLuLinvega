"""Send files to Discord."""

import argparse
import os
import sys

from .config import load_webhook_config
from .discord_api import send_file_to_discord


def handle_send_command(file_path, comment=None):
    """Handle send command from CLI."""
    try:
        webhook_url, thread_id, needs_thread = load_webhook_config()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        sys.exit(1)

    status_code, response_text = send_file_to_discord(
        file_path, webhook_url, thread_id, needs_thread, comment, "File"
    )

    if status_code in [200, 204]:
        print(f"File '{file_path}' sent successfully.")
    else:
        print(f"Error sending file: {status_code} - {response_text}")


def main():
    """Main entry point for dcsend command."""
    parser = argparse.ArgumentParser(
        description="Send files to Discord using a webhook."
    )
    parser.add_argument("file", help="The file to upload")
    parser.add_argument("-c", "--comment", help="Optional comment to include", default=None)
    args = parser.parse_args()

    try:
        webhook_url, thread_id, needs_thread = load_webhook_config()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' does not exist.")
        sys.exit(1)

    status_code, response_text = send_file_to_discord(
        args.file, webhook_url, thread_id, needs_thread, args.comment, "File"
    )

    if status_code in [200, 204]:
        print(f"File '{args.file}' sent successfully.")
    else:
        print(f"Error sending file: {status_code} - {response_text}")