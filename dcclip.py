#!/usr/bin/env python3

import os
import subprocess
import requests
import json
import tempfile
import sys

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


def get_clipboard_text():
    """Retrieve text content from the clipboard using xclip."""
    try:
        return subprocess.check_output(["xclip", "-selection", "clipboard", "-o"], text=True)
    except subprocess.CalledProcessError:
        return None


def get_clipboard_image():
    """Check if the clipboard contains an image and return it."""
    try:
        return subprocess.check_output(["xclip", "-selection", "clipboard", "-t", "image/png", "-o"], stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return None


def is_file_path(text):
    """Check if the text is a file path with the 'file://' prefix."""
    return text.startswith("file://")


def send_message_to_discord(content, thread_id=None):
    """Send a text message to Discord."""
    webhook_url, thread_id, needs_thread = load_webhook_config()
    data = {"username": "Yeeb - Clipboard", "content": content}

    # Always include the thread ID if WEBHOOK_NEEDS_THREAD is set to true
    params = {"thread_id": thread_id} if needs_thread and thread_id else {}

    response = requests.post(
        webhook_url,
        data=json.dumps(data),
        headers={"Content-Type": "application/json"},
        params=params
    )
    return response.status_code, response.text


def send_file_to_discord(file_path, thread_id=None, comment=None):
    """Send a file to Discord."""
    webhook_url, thread_id, needs_thread = load_webhook_config()
    
    data = {
        "username": "Yeeb - Clipboard",
        "content": comment if comment else "Sending clipboard content as a file."
    }

    # Always include the thread ID if WEBHOOK_NEEDS_THREAD is set to true
    params = {"thread_id": thread_id} if needs_thread and thread_id else {}

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
    """Main function to handle clipboard content retrieval and sending to Discord."""
    webhook_url, thread_id, needs_thread = load_webhook_config()

    # Step 1: Check if the clipboard contains an image
    image_data = get_clipboard_image()
    if image_data:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            temp_file.write(image_data)
            temp_file_path = temp_file.name
        
        status_code, response_text = send_file_to_discord(temp_file_path, thread_id, "Sending clipboard image")
        os.remove(temp_file_path)
        
        if status_code in [200, 204]:
            print("Image sent successfully.")
        else:
            print(f"Error sending image: {status_code} - {response_text}")
        return

    # Step 2: Check if the clipboard contains text
    clipboard_content = get_clipboard_text()
    if clipboard_content:
        # If it's a file path, send the file
        if is_file_path(clipboard_content):
            file_path = clipboard_content.replace("file://", "").strip()
            if os.path.exists(file_path):
                status_code, response_text = send_file_to_discord(file_path, thread_id)
                if status_code in [200, 204]:
                    print("File sent successfully.")
                else:
                    print(f"Error sending file: {status_code} - {response_text}")
            else:
                print(f"Error: File '{file_path}' does not exist.")
            return
        
        # If it's plain text, send it as a message or file
        if len(clipboard_content) <= DISCORD_CHAR_LIMIT:
            status_code, response_text = send_message_to_discord(clipboard_content, thread_id)
        else:
            with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt") as temp_file:
                temp_file.write(clipboard_content)
                temp_file_path = temp_file.name

            status_code, response_text = send_file_to_discord(temp_file_path, thread_id)
            os.remove(temp_file_path)
        
        if status_code in [200, 204]:
            print("Clipboard content sent successfully.")
        else:
            print(f"Error sending clipboard content: {status_code} - {response_text}")
    else:
        print("Clipboard is empty or contains unsupported content.")


if __name__ == "__main__":
    main()
