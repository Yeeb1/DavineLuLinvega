#!/usr/bin/env python3

import os
import subprocess
import requests
import sys
import json
import argparse
import tempfile

DISCORD_CHAR_LIMIT = 2000

def load_webhook_config():
    """Load environment variables for the webhook configuration."""
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    thread_id = os.environ.get("THREAD_ID")
    needs_thread = os.environ.get("WEBHOOK_NEEDS_THREAD", "false").lower() == "true"
    
    if not webhook_url:
        print("Error: DISCORD_WEBHOOK_URL not set in environment.")
        sys.exit(1)
    
    return webhook_url, thread_id, needs_thread


def send_message_to_discord(content, thread_id=None, needs_thread=False):
    """Send a simple message to Discord."""
    webhook_url, _, _ = load_webhook_config()
    data = {"username": "Yeeb - CLI", "content": content}

    # Set parameters if thread ID is required
    params = {"thread_id": thread_id} if needs_thread and thread_id else {}

    response = requests.post(
        webhook_url,
        data=json.dumps(data),
        headers={"Content-Type": "application/json"},
        params=params
    )
    return response.status_code, response.text


def send_file_to_discord(file_path, thread_id=None, needs_thread=False, comment=None):
    """Send a file to Discord."""
    webhook_url, _, _ = load_webhook_config()
    
    data = {
        "username": "Yeeb - CLI",
        "content": comment if comment else "Output exceeded 2000 characters, sending as file."
    }

    params = {"thread_id": thread_id} if needs_thread and thread_id else {}

    # Open the file in binary mode
    with open(file_path, 'rb') as file:
        files = {"file": (os.path.basename(file_path), file)}
        response = requests.post(
            webhook_url,
            data=data,
            files=files,
            params=params
        )
    return response.status_code, response.text


def main():
    """Main function to handle command-line arguments."""
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
    webhook_url, thread_id, needs_thread = load_webhook_config()

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
    message_content = f"{args.comment + '\n' if args.comment else ''}```\n{prompt}{output}\n```"

    # Check length and send as a message if <= 2000 characters, otherwise as a file
    if len(message_content) <= DISCORD_CHAR_LIMIT:
        status_code, response_text = send_message_to_discord(message_content, thread_id, needs_thread)
    else:
        with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt") as temp_file:
            temp_file.write(f"{prompt}\n{output}")
            temp_file_path = temp_file.name

        status_code, response_text = send_file_to_discord(temp_file_path, thread_id, needs_thread, args.comment)
        
        os.remove(temp_file_path)

    if status_code in [200, 204]:
        print("Message sent successfully.")
    else:
        print(f"Error sending message: {status_code} - {response_text}")


if __name__ == "__main__":
    main()
