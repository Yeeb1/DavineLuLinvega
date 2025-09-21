"""Send command output to Discord."""

import argparse
import os
import subprocess
import sys
import tempfile

from .config import load_webhook_config
from .discord_api import send_message_to_discord, send_file_to_discord

DISCORD_CHAR_LIMIT = 2000


def handle_log_command(command_args, comment=None):
    """Handle log command from CLI."""
    if not command_args:
        print("Error: No command provided.")
        sys.exit(1)

    command = " ".join(command_args)

    try:
        webhook_url, thread_id, needs_thread = load_webhook_config()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Execute the command and capture the output
    try:
        result = subprocess.run(command_args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout + result.stderr
    except subprocess.CalledProcessError as e:
        output = e.stdout + e.stderr

    user = os.getenv("USER", "user")
    hostname = os.uname().nodename
    cwd = os.getcwd()
    prompt = f"┌──({user}@{hostname})-[{cwd}]\n└─$ {command}\n"
    comment_part = f"{comment}\n" if comment else ""
    message_content = f"{comment_part}```\n{prompt}{output}\n```"

    # Check length and send as a message if <= 2000 characters, otherwise as a file
    if len(message_content) <= DISCORD_CHAR_LIMIT:
        status_code, response_text = send_message_to_discord(
            message_content, webhook_url, thread_id, needs_thread, "CLI"
        )
    else:
        with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt") as temp_file:
            temp_file.write(f"{prompt}\n{output}")
            temp_file_path = temp_file.name

        status_code, response_text = send_file_to_discord(
            temp_file_path, webhook_url, thread_id, needs_thread, comment, "CLI"
        )

        os.remove(temp_file_path)

    if status_code in [200, 204]:
        print("Message sent successfully.")
    else:
        print(f"Error sending message: {status_code} - {response_text}")


def main():
    """Main entry point for dclog command."""
    parser = argparse.ArgumentParser(
        description="Send terminal command output to Discord using a webhook."
    )
    parser.add_argument("-c", "--comment", help="Optional comment to include", default=None)
    parser.add_argument("command", nargs=argparse.REMAINDER, help="The command to execute")

    args = parser.parse_args()

    if not args.command:
        print("Error: No command provided.")
        sys.exit(1)

    command = " ".join(args.command)

    try:
        webhook_url, thread_id, needs_thread = load_webhook_config()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Execute the command and capture the output
    try:
        result = subprocess.run(args.command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout + result.stderr
    except subprocess.CalledProcessError as e:
        output = e.stdout + e.stderr

    user = os.getenv("USER", "user")
    hostname = os.uname().nodename
    cwd = os.getcwd()
    prompt = f"┌──({user}@{hostname})-[{cwd}]\n└─$ {command}\n"
    comment_part = f"{args.comment}\n" if args.comment else ""
    message_content = f"{comment_part}```\n{prompt}{output}\n```"

    # Check length and send as a message if <= 2000 characters, otherwise as a file
    if len(message_content) <= DISCORD_CHAR_LIMIT:
        status_code, response_text = send_message_to_discord(
            message_content, webhook_url, thread_id, needs_thread, "CLI"
        )
    else:
        with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt") as temp_file:
            temp_file.write(f"{prompt}\n{output}")
            temp_file_path = temp_file.name

        status_code, response_text = send_file_to_discord(
            temp_file_path, webhook_url, thread_id, needs_thread, args.comment, "Yeeb - CLI"
        )

        os.remove(temp_file_path)

    if status_code in [200, 204]:
        print("Message sent successfully.")
    else:
        print(f"Error sending message: {status_code} - {response_text}")