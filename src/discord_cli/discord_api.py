"""Discord API interaction utilities."""

import json
import os
import requests
from .config import get_username


def get_username_with_suffix(suffix: str = None) -> str:
    """Get username with optional suffix."""
    base_username = get_username()
    if suffix:
        return f"{base_username} - {suffix}"
    return base_username


def send_message_to_discord(content, webhook_url, thread_id=None, needs_thread=False, suffix=None):
    """Send a text message to Discord."""
    username = get_username_with_suffix(suffix)
    data = {"username": username, "content": content}
    params = {"thread_id": thread_id} if needs_thread and thread_id else {}

    response = requests.post(
        webhook_url,
        data=json.dumps(data),
        headers={"Content-Type": "application/json"},
        params=params
    )
    return response.status_code, response.text


def send_file_to_discord(file_path, webhook_url, thread_id=None, needs_thread=False,
                        comment=None, suffix=None):
    """Send a file to Discord."""
    username = get_username_with_suffix(suffix)
    data = {
        "username": username,
        "content": comment if comment else "File upload"
    }
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


def send_embed_to_discord(embed_data, webhook_url, thread_id=None, needs_thread=False, suffix=None):
    """Send a rich embed to Discord."""
    username = get_username_with_suffix(suffix)
    data = {"username": username, "embeds": [embed_data]}
    params = {"thread_id": thread_id} if needs_thread and thread_id else {}

    response = requests.post(
        webhook_url,
        data=json.dumps(data),
        headers={"Content-Type": "application/json"},
        params=params
    )
    return response.status_code, response.text