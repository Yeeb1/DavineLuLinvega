"""Send clipboard content to Discord."""

import os
import subprocess
import sys
import tempfile

from .config import load_webhook_config
from .discord_api import send_message_to_discord, send_file_to_discord

DISCORD_CHAR_LIMIT = 2000


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


def handle_clip_command():
    """Handle clip command from CLI."""
    try:
        webhook_url, thread_id, needs_thread = load_webhook_config()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Step 1: Check if the clipboard contains an image
    image_data = get_clipboard_image()
    if image_data:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            temp_file.write(image_data)
            temp_file_path = temp_file.name

        status_code, response_text = send_file_to_discord(
            temp_file_path, webhook_url, thread_id, needs_thread, "Sending clipboard image", "Clipboard"
        )
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
                status_code, response_text = send_file_to_discord(
                    file_path, webhook_url, thread_id, needs_thread, None, "Clipboard"
                )
                if status_code in [200, 204]:
                    print("File sent successfully.")
                else:
                    print(f"Error sending file: {status_code} - {response_text}")
            else:
                print(f"Error: File '{file_path}' does not exist.")
            return

        # If it's plain text, send it as a message or file
        if len(clipboard_content) <= DISCORD_CHAR_LIMIT:
            status_code, response_text = send_message_to_discord(
                clipboard_content, webhook_url, thread_id, needs_thread, "Clipboard"
            )
        else:
            with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt") as temp_file:
                temp_file.write(clipboard_content)
                temp_file_path = temp_file.name

            status_code, response_text = send_file_to_discord(
                temp_file_path, webhook_url, thread_id, needs_thread, None, "Clipboard"
            )
            os.remove(temp_file_path)

        if status_code in [200, 204]:
            print("Clipboard content sent successfully.")
        else:
            print(f"Error sending clipboard content: {status_code} - {response_text}")
    else:
        print("Clipboard is empty or contains unsupported content.")


def main():
    """Main entry point for dcclip command."""
    try:
        webhook_url, thread_id, needs_thread = load_webhook_config()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Step 1: Check if the clipboard contains an image
    image_data = get_clipboard_image()
    if image_data:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            temp_file.write(image_data)
            temp_file_path = temp_file.name

        status_code, response_text = send_file_to_discord(
            temp_file_path, webhook_url, thread_id, needs_thread, "Sending clipboard image", "Clipboard"
        )
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
                status_code, response_text = send_file_to_discord(
                    file_path, webhook_url, thread_id, needs_thread, None, "Clipboard"
                )
                if status_code in [200, 204]:
                    print("File sent successfully.")
                else:
                    print(f"Error sending file: {status_code} - {response_text}")
            else:
                print(f"Error: File '{file_path}' does not exist.")
            return

        # If it's plain text, send it as a message or file
        if len(clipboard_content) <= DISCORD_CHAR_LIMIT:
            status_code, response_text = send_message_to_discord(
                clipboard_content, webhook_url, thread_id, needs_thread, "Clipboard"
            )
        else:
            with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt") as temp_file:
                temp_file.write(clipboard_content)
                temp_file_path = temp_file.name

            status_code, response_text = send_file_to_discord(
                temp_file_path, webhook_url, thread_id, needs_thread, None, "Clipboard"
            )
            os.remove(temp_file_path)

        if status_code in [200, 204]:
            print("Clipboard content sent successfully.")
        else:
            print(f"Error sending clipboard content: {status_code} - {response_text}")
    else:
        print("Clipboard is empty or contains unsupported content.")