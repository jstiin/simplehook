# SimpleHook

**SimpleHook** is a minimalistic Python wrapper for Discord webhooks. It allows you to easily send messages, files, and embedded content to a Discord channel using just a few lines of code.

![PyPI](https://img.shields.io/pypi/v/simplehook) ![Python](https://img.shields.io/pypi/pyversions/simplehook) ![License](https://img.shields.io/badge/license-AGPL--3.0-3b3b3b?style=flat)

## 🔧 Features

- Send plain text messages
- Customize username and avatar
- Mention users or everyone/here
- Use text-to-speech
- Use embeds
- Upload files and images
- Create and send polls

## 🚀 Usage

### Import and setup
```python
from simplehook import SimpleHook # or from simplehook import SimpleHookAsync

# Initialize with your webhook URL
hook = SimpleHook("https://discord.com/api/webhooks/your_webhook_url")
# or
hook = SimpleHookAsync("https://discord.com/api/webhooks/your_webhook_url")
````
### Core functions
```python
# Send a simple message
hook.send_message("Hello, world!")

# Send a file
hook.send_file("example.txt")

# Send a message with a custom username, avatar, and text-to-speech
hook.send_customized_message(
    message="I'm a bot!",
    username="CoolBot",
    avatar_url="https://i.imgur.com/your_avatar.png",
    tts=True
)

# Mention a user by ID or everyone/here
hook.send_customized_message(message="Look here!", mention="123456789012345678")  # user mention
hook.send_customized_message(message="Attention!", mention="everyone")  # @everyone
```
### Embed functions
```python
# Send embedded files (max 10)
hook.send_embedded_files(paths=["img1.png", "img2.jpg"], message="Check these out!", color=53231)

# Send embedded message
hook.send_embedded_message(title="Hello!", color=321)

# Send embedded author message
hook.send_embedded_author(name="Paul", avatar_url="https://i.imgur.com/your_avatar.png")

# Send embedded URL with a custom title
hook.send_embedded_url(title="Google!", url="https://www.google.com")

# Send embedded image from the web
hook.send_embedded_url_image(url="https://i.imgur.com/your_image.png")

# Send embed message with multiple fields
hook.send_embedded_field(names=["Username", "Score"], values=["Player", "150"], inline=[True, True])
```
### Poll function
```python
# Create and send a poll
hook.create_poll(
    question="What's your favorite color?",
    answers=["Blue", "Red", "Green"],
    emojis=["🔵", "🔴", "🟢"],
    duration=48,
    allow_multiselect=True
)
```
## 📦 Installation
```bash
pip install simplehook
```

