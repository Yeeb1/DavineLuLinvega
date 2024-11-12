#!/usr/bin/env python3

import os
import requests
import sys
import argparse

def load_webhook_config():
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    thread_id = os.environ.get("THREAD_ID")
    needs_thread = os.environ.get("WEBHOOK_NEEDS_THREAD", "false").lower() == "true"
    
    if not webhook_url:
        print("Error: DISCORD_WEBHOOK_URL not set in environment.")
        sys.exit(1)
    
    return webhook_url, thread_id, needs_thread


def send_file_to_discord(file_path, comment=None):
    webhook_url, thread_id, needs_thread = load_webhook_config()

    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        sys.exit(1)

    data = {
        "username": "Yeeb - File",
        "content": comment if comment else "Uploaded a file"
    }

    params = {"thread_id": thread_id} if needs_thread and thread_id else {}

    with open(file_path, 'rb') as file:
        files = {"file": (os.path.basename(file_path), file)}
        response = requests.post(webhook_url, data=data, files=files, params=params)

        if response.status_code in [200, 204]:
            print(f"File '{file_path}' sent successfully.")
        else:
            print(f"Error sending file: {response.status_code} - {response.text}")


def main():
    parser = argparse.ArgumentParser(
        description="Send files to Discord using a webhook."
    )
    parser.add_argument("file", help="The file to upload")
    parser.add_argument("-c", "--comment", help="Optional comment to include", default=None)
    args = parser.parse_args()

    send_file_to_discord(args.file, args.comment)


if __name__ == "__main__":
    main()
