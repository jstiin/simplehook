import json
import httpx
import os
from typing import Optional
from aiofiles import open


class SimpleHookAsync:

    """
    A minimalistic asynchronous class to send messages, files, and images using Discord Webhooks.
    """

    webhook_url: str

    def __init__(self, webhook_url: str) -> None:
        """
        Initialize the webhook client.

        Args:
            webhook_url (str): The Discord webhook URL to send messages to.
        """

        self.webhook_url = webhook_url

    async def post(self, **kwargs) -> None:
        """
        Helper method to send a POST request.

        Args:
            **kwargs: Arbitrary keyword arguments passed to the underlying HTTP request (e.g., json, headers).

        Raises:
            HTTPError: If the HTTP request returns an unsuccessful status code.
        """

        async with httpx.AsyncClient() as client:
           r = await client.post(url=self.webhook_url, **kwargs)
           r.raise_for_status()

    def validate(self, color: int) -> int:
        """
        Validate the color value to ensure it is within the allowed range.

        Args:
            color (int): The color value to validate. Must be between 0 and 65280 inclusive.

        Returns:
            int: The validated color value if it is within the valid range.

        Raises:
            ValueError: If the color value is outside the range 0 to 65280.
        """
        if color < 0 or color > 65280:
            raise ValueError("Value of color must be between 0 and 65280!")
        else:
            return color

    async def send_message(self, message: str) -> None:
        """
        Send a basic text message to the Discord webhook.

        Args:
            message (str): The plain text message to send.
        """

        body = {
            "content": message
        }

        await self.post(json=body)

    async def send_customized_message(
        self,
        message: str,
        username: Optional[str] = None,
        avatar_url: Optional[str] = None,
        mention: Optional[str] = None,
        tts: Optional[bool] = None
    ) -> None:
        """
        Send a customized message with optional username, avatar, and a user mention.

        Args:
            message (str): The message content.
            username (Optional[str]): A custom username to display instead of the webhook default.
            avatar_url (Optional[str]): A URL to a custom avatar image.
            mention (Optional[str]): The ID of the user to mention in the message.
            tts (Optional[bool]): If True, the message will be read aloud using text-to-speech.
        """

        body: dict = {
            "content": message,
        }

        if username:
            body['username'] = username

        if avatar_url:
            body['avatar_url'] = avatar_url

        if mention:
            body['content'] = f"<@{mention}> {message}"

            if mention == "everyone" or mention == "here":
                body['content'] = f"@{mention} {message}"

        if tts:
            body["tts"] = tts

        await self.post(json=body)

    async def send_file(self, file_path: str) -> None:
        """
        Send a single file via the Discord webhook.

        Args:
            file_path (str): The local path to the file.
        """

        async with open(file_path, "rb") as f:
            file = await f.read()
            filename = os.path.basename(file_path)

        file_body: dict = {
            "file": (filename, file)
        }

        await self.post(files=file_body)

    async def send_embedded_files(self, paths: list[str], message: Optional[str] = None, color: Optional[int] = None) -> None:
        """
        Send multiple files as embedded content in a Discord message.

        Args:
            paths (list[str]): List of local file paths to send (maximum 10 files).
            message (Optional[str]): Optional text content to include with the embeds.
            color (Optional[int], optional): Decimal integer color value between 0 and 65280. Defaults to None.

        Raises:
            ValueError: If more than 10 files are provided.
        """

        if len(paths) > 10:
            raise ValueError("Cannot send more than 10 images")

        embeds: list = []
        files: list = []

        for index, path in enumerate(paths):
            async with open(path, "rb") as f:
                file = await f.read()
                filename = os.path.basename(path)
                files.append((f"files[{index}]", (filename, file)))
                embeds.append({
                    "image": {"url": f"attachment://"+filename}
                })
            if color is not None:
                color = self.validate(color)
                embeds[index]["color"] = color

        payload = {
            "content": message or "",
            "embeds": embeds
        }

        await self.post(data={"payload_json": json.dumps(payload)}, files=files)

    async def create_poll(
        self,
        question: str,
        answers: list,
        emojis: Optional[list] = None,
        duration: Optional[int] = None,
        allow_multiselect: Optional[bool] = None
    ) -> None:
        """
        Create and send a poll message.

        Args:
            question (str): The poll question, maximum 300 characters.
            answers (list[str]): List of answer options, each up to 55 characters.
            emojis (Optional[list]): Optional list of emojis corresponding to each answer.
                For custom emojis, provide the emoji ID as an integer.
            duration (Optional[int]): Optional poll duration in hours, from 1 up to 768.
            allow_multiselect (Optional[bool]): If True, allows selecting multiple answers.

        Raises:
            ValueError: If question exceeds 300 characters.
            ValueError: If any answer exceeds 55 characters.
            ValueError: If duration is outside the range 1 to 768.
            ValueError: If length of emojis list does not match length of answers.
        """

        if len(question) > 300:
            raise ValueError("Question length cannot exceed 300 characters")

        if duration is not None and (duration > 768 or duration < 1):
            raise ValueError("Duration must be between 1 and 768")

        body = {
            "poll": {
                "question": {
                    "text": question
                },
                "answers": [
                ]
            }
        }

        for answer in answers:
            if len(answer) > 55:
                raise ValueError("Answer length cannot exceed 55 characters")

            body["poll"]["answers"].append({"poll_media": {"text": answer}})

        if allow_multiselect:
            body["poll"]["allow_multiselect"] = allow_multiselect

        if duration:
            body["poll"]["duration"] = duration

        if emojis:
            if len(answers) == len(emojis):
                for i, emoji in enumerate(emojis):
                    if isinstance(emoji, str):
                        body["poll"]["answers"][i]["poll_media"]["emoji"] = {
                            "name": emoji}
                    else:
                        body["poll"]["answers"][i]["poll_media"]["emoji"] = {
                            "id": str(emoji)}
            else:
                raise ValueError(
                    "Length of emojis must match length of answers")

        await self.post(json=body)

    async def send_embedded_message(self, title: str, color: Optional[int] = None) -> None:
        """Send an embedded message.

        Args:
            title (str): Content of the embed.
            color (Optional[int], optional): Decimal integer color value between 0 and 65280. Defaults to None.
        """

        body = {
            "embeds": []
        }

        body["embeds"].append({"title": title})

        if color is not None:
            color = self.validate(color)
            body["embeds"][0]["color"] = color

        await self.post(json=body)

    async def send_embedded_author(self, name: str, avatar_url: str, url: Optional[str] = None,  description: Optional[str] = None, color: Optional[int] = None) -> None:
        """Send an embedded author message.

        Args:
            name (str): Name of the author.
            url (str): URL for the hyperlink.
            avatar_url (str): Image URL for the author's avatar.
            description (Optional[str], optional): Description content of the message. Defaults to None.
            color (Optional[int], optional): Decimal integer color value between 0 and 65280. Defaults to None.
        """

        author = {"name": name, "icon_url": avatar_url}
        body = {
            "embeds": []
        }
        body["embeds"].append({"author": author})

        if url is not None:
            body["embeds"][0]["author"]["url"] = url

        if description is not None:
            body["embeds"][0]["description"] = description

        if color is not None:
            color = self.validate(color)
            body["embeds"][0]["color"] = color

        await self.post(json=body)

    async def send_embedded_url(self, title: str, url: str, color: Optional[int] = None) -> None:
        """Send an embedded message with a hyperlink.

        Args:
            title (str): Content of the embed.
            url (str): URL for the hyperlink.
            color (Optional[int], optional): Decimal integer color value between 0 and 65280. Defaults to None.
        """

        body = {
            "embeds": []
        }

        body["embeds"].append({"title": title, "url": url})

        if color is not None:
            color = self.validate(color)
            body["embeds"][0]["color"] = color

        await self.post(json=body)

    async def send_embedded_url_image(self, url: str, message: Optional[str] = None, color: Optional[int] = None) -> None:
        """Send an embedded image via URL.

        Args:
            url (str): URL of the image.
            color (Optional[int], optional): Decimal integer color value between 0 and 65280. Defaults to None.
        """

        body = {
            "embeds": [],
            "content": message or ""
        }

        body["embeds"].append({"image": {"url": url}})

        if color is not None:
            color = self.validate(color)
            body["embeds"][0]["color"] = color

        await self.post(json=body)

    async def send_embedded_field(self, names: list[str], values: list[str], inline: list[bool], color: Optional[int] = None) -> None:
        """
        Sends an embed message with multiple fields.

        Args:
            names (list[str]): List of field names (titles) for the embed.
            values (list[str]): List of field values corresponding to each name.
            inline (list[bool]): List indicating if each field should be displayed inline.
            color (Optional[int], optional): Decimal integer color value between 0 and 65280. Defaults to None.

        Raises:
            ValueError: If the lengths of the `names`, `values`, and `inline` lists do not match.
            ValueError: If any of the lists are empty.
        """

        body = {
            "embeds": [{
                "fields": [],
                "color": None
            }]
        }

        if len(names) == len(values) == len(inline):
            if names:
                for i, name in enumerate(names):
                    body["embeds"][0]["fields"].append(
                        {"name": name, "value": values[i], "inline": inline[i]})
            else:
                raise ValueError(
                    "Lists must contain at least one element each!")
        else:
            raise ValueError("Lengths of all lists must match!")

        if color is not None:
            color = self.validate(color)
            body["embeds"][0]["color"] = color

        await self.post(json=body)