import pytest
import httpx
from simplehook import SimpleHookAsync
from unittest.mock import patch, mock_open, AsyncMock

hook = SimpleHookAsync("")


@pytest.mark.parametrize("num", [0, 1, 36012, 65280])
@pytest.mark.asyncio
async def test_is_valid(num):
    assert hook.validate(color=num) == num


@pytest.mark.parametrize("num", [-1, -65280, 65281, 99999])
@pytest.mark.asyncio
async def test_is_invalid(num):
    with pytest.raises(ValueError, match="Value of color must be between 0 and 65280!"):
        hook.validate(num)


@pytest.mark.asyncio
async def test_send_message(mocker):
    mocker_post = mocker.patch.object(hook, "post", new_callable=AsyncMock)

    await hook.send_message(message="Test")

    mocker_post.assert_called_once_with(
        json={"content": "Test"})


@pytest.mark.asyncio
async def test_send_message_empty(mocker):
    response = httpx.Response(400, request=httpx.Request(
        method="POST", url="https://test.test"))
    mocker_post = mocker.patch.object(hook, "post", side_effect=httpx.HTTPStatusError(
        message="Error!", request=response.request, response=response))

    with pytest.raises(expected_exception=httpx.HTTPStatusError):
        await hook.send_message("")

    mocker_post.assert_called_once()


@pytest.mark.asyncio
async def test_post(mocker):
    mocker_post = mocker.patch(
        "httpx.AsyncClient.post", new_callable=AsyncMock)

    mock_response = mocker_post.return_value
    mock_response.raise_for_status = mocker.AsyncMock()

    mocker_post.return_value = mock_response

    await hook.post(json={"content": "test"})

    mocker_post.assert_awaited_once_with(
        url=hook.webhook_url, json={"content": "test"}
    )

    mock_response.raise_for_status.assert_called_once_with()


@pytest.mark.asyncio
async def test_post_error(mocker):
    mocker_post = mocker.patch(
        "httpx.AsyncClient.post", new_callable=AsyncMock)
    mock_response = mocker_post.return_value
    mock_response.raise_for_status = mocker.Mock(
        side_effect=httpx.HTTPError("Error!"))

    with pytest.raises(httpx.HTTPError):
        await hook.post(json={"content": "test"})


@pytest.mark.asyncio
async def test_send_customized_message_full(mocker):
    mocker_post = mocker.patch.object(hook, "post")
    message = "test"
    username = "test"
    avatar_url = "test"
    mention = "here"
    tts = True

    expected_body: dict[str, str | bool] = {
        "content": "",
        "username": username,
        "avatar_url": avatar_url,
    }

    await hook.send_customized_message(
        message=message, username=username, avatar_url=avatar_url, mention=mention, tts=tts)

    if mention == "everyone" or mention == "here":
        expected_body["content"] = f"@{mention} {message}"

    else:
        expected_body["content"] = f"<@{mention}> {message}"

    if tts:
        expected_body["tts"] = tts

    mocker_post.assert_called_once_with(json=expected_body)


@pytest.mark.asyncio
async def test_send_customized_message_empty_message(mocker):
    mocker_post = mocker.patch.object(
        hook, "post", side_effect=httpx.HTTPError("Error!"))

    with pytest.raises(expected_exception=httpx.HTTPError):
        await hook.send_customized_message(message="")

    mocker_post.assert_called_once()


@pytest.mark.asyncio
async def test_send_file_error(mocker):
    mocker_post = mocker.patch.object(hook, "post", new_callable=AsyncMock)

    with pytest.raises(expected_exception=FileNotFoundError):
        await hook.send_file(file_path="")

    mocker_post.assert_not_called()

# FAILED TEST


@pytest.mark.asyncio
async def test_send_file(mocker):
    file = mock_open(read_data="Data")
    with patch("aiofiles.open", file):
        mocker_post = mocker.patch.object(hook, "post", new_callable=AsyncMock)
        await hook.send_file("path.png")

        mocker_post.assert_called_once()

# FAILED TEST


@pytest.mark.asyncio
async def test_send_embedded_files(mocker):
    files = mock_open()
    files.side_effect = [mock_open(read_data="Data").return_value, mock_open(
        read_data="DATA").return_value]
    with patch("builtins.open", files):
        mocker_post = mocker.patch.object(hook, "post", new_callable=AsyncMock)
        await hook.send_embedded_files(paths=["path1,jpg", "path2.png"], color=241)

        mocker_post.assert_called_once()


@pytest.mark.asyncio
async def test_send_embedded_files_over_10(mocker):
    mocker_post = mocker.patch.object(hook, "post", new_callable=AsyncMock)

    with pytest.raises(expected_exception=ValueError, match="Cannot send more than 10 images"):
        await hook.send_embedded_files(paths=["path1.png", "path1.png", "path1.png", "path1.png", "path1.png", "path1.png",
                                              "path1.png", "path1.png", "path1.png", "path1.png" "path1.png", "path1.png", "path1.png"])

    mocker_post.assert_not_called()


@pytest.mark.asyncio
async def test_send_embedded_files_empty(mocker):
    mocker_post = mocker.patch.object(hook, "post", new_callable=AsyncMock)

    with pytest.raises(expected_exception=FileNotFoundError):
        await hook.send_embedded_files(paths=[""])

    mocker_post.assert_not_called()

# FAILED TEST


@pytest.mark.asyncio
async def test_send_embedded_files_color_error(mocker):
    file = mock_open(read_data="Data")
    with patch("builtins.open", file):
        mocker_post = mocker.patch.object(hook, "post", new_callable=AsyncMock)

        with pytest.raises(expected_exception=ValueError, match="Value of color must be between 0 and 65280!"):
            await hook.send_embedded_files(paths=["path.png"], color=-1)

        mocker_post.assert_not_called()


@pytest.mark.parametrize("num", [1, 352, 768, 42])
@pytest.mark.asyncio
async def test_create_poll_full(mocker, num):
    mock_post = mocker.patch.object(hook, "post", new_callable=AsyncMock)
    allow_multiselect = True

    await hook.create_poll(question="Test", answers=["Test"], emojis=[
        "😊"], allow_multiselect=allow_multiselect, duration=num)

    expected_body = {
        "poll": {
            "question": {
                "text": "Test"
            },
            "answers":
                [{
                    "poll_media": {
                        "text": "Test",
                        "emoji": {
                            "name": "😊"
                        }
                    },
                }
            ],
            "duration": num
        }
    }

    if allow_multiselect:
        expected_body["poll"]["allow_multiselect"] = True

    mock_post.assert_called_once_with(json=expected_body)


@pytest.mark.parametrize("num", [0, -1, 769, 1000, 99999, -142])
@pytest.mark.asyncio
async def test_create_poll_duration_error(mocker, num):
    mock_post = mocker.patch.object(hook, "post", new_callable=AsyncMock)

    with pytest.raises(expected_exception=ValueError, match="Duration must be between 1 and 768"):
        await hook.create_poll(question="test", answers=["test"], duration=num)

    mock_post.assert_not_called()


@pytest.mark.asyncio
async def test_create_poll_len_error(mocker):
    mocker_post = mocker.patch.object(hook, "post", new_callable=AsyncMock)

    with pytest.raises(expected_exception=ValueError, match="Length of emojis must match length of answers"):
        await hook.create_poll(question="test", answers=[
            "test", "test"], emojis=["😊"])

    mocker_post.assert_not_called()


@pytest.mark.asyncio
async def test_create_poll_answers_len_error(mocker):
    mocker_post = mocker.patch.object(hook, "post", new_callable=AsyncMock)

    with pytest.raises(expected_exception=ValueError, match="Answer length cannot exceed 55 characters"):
        await hook.create_poll(question="test", answers=[
            "tttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt"])

    mocker_post.assert_not_called()


@pytest.mark.asyncio
async def test_create_poll_question_len_error(mocker):
    mocker_post = mocker.patch.object(hook, "post", new_callable=AsyncMock)

    with pytest.raises(expected_exception=ValueError, match="Question length cannot exceed 300 characters"):
        await hook.create_poll(
            question="ttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt",
            answers=["test"]
        )

    mocker_post.assert_not_called()


@pytest.mark.asyncio
async def test_create_poll_int_to_str(mocker):
    mocker_post = mocker.patch.object(hook, "post", new_callable=AsyncMock)

    text = "test"
    text2 = "test"
    emoji = 100000

    expected_body = {
        "poll": {
            "question": {
                "text": text
            },
            "answers":
                [{
                    "poll_media": {
                        "text": text2,
                        "emoji": {
                            "id": str(emoji)
                        }
                    },
                }
            ],
        }
    }

    await hook.create_poll(question=text, answers=[text2], emojis=[emoji])

    mocker_post.assert_called_once_with(json=expected_body)


@pytest.mark.asyncio
async def test_send_embedded_message_full(mocker):
    mocker_post = mocker.patch.object(hook, "post", new_callable=AsyncMock)

    expected_body = {
        "embeds": [{
            "title": "test",
            "color": 2
        }]
    }

    await hook.send_embedded_message(title="test", color=2)

    mocker_post.assert_called_with(json=expected_body)


@pytest.mark.asyncio
async def test_send_embedded_message_empty_title(mocker):
    response = httpx.Response(400, request=httpx.Request(
        "POST", "https://www.test.test"))
    mocker_post = mocker.patch.object(hook, "post", new_callable=AsyncMock, side_effect=httpx.HTTPStatusError(
        message="Error!", request=response.request, response=response))

    with pytest.raises(expected_exception=httpx.HTTPStatusError):
        await hook.send_embedded_message(title="")

    mocker_post.assert_called_once()


@pytest.mark.asyncio
async def test_send_embedded_author_full(mocker):
    mocker_post = mocker.patch.object(hook, "post", new_callable=AsyncMock)

    expected_body = {
        "embeds": [
            {
                "author": {
                    "name": "test",
                    "url": "https://test.test",
                    "icon_url": "https://test.test"
                },
                "description": "test",
                "color": 2
            },
        ]
    }

    await hook.send_embedded_author(name="test", avatar_url="https://test.test",
                                    url="https://test.test", description="test", color=2)

    mocker_post.assert_called_once_with(json=expected_body)


@pytest.mark.asyncio
async def test_send_embedded_author_empty_name(mocker):
    response = httpx.Response(400, request=httpx.Request(
        method="POST", url="https://test.test"))
    mocker_post = mocker.patch.object(hook, "post", new_callable=AsyncMock, side_effect=httpx.HTTPStatusError(
        message="Error!", request=response.request, response=response))

    with pytest.raises(expected_exception=httpx.HTTPStatusError):
        await hook.send_embedded_author(name="", avatar_url="https://test.test")

    mocker_post.assert_called_once()


@pytest.mark.asyncio
async def test_send_embedded_url_full(mocker):
    mocker_post = mocker.patch.object(hook, "post", new_callable=AsyncMock)

    expected_body = {
        "embeds": [
            {
                "title": "test",
                "url": "https://test.test",
                "color": 2
            }
        ]
    }

    await hook.send_embedded_url(title="test", url="https://test.test", color=2)

    mocker_post.assert_called_once_with(json=expected_body)


@pytest.mark.asyncio
async def test_send_embedded_url_empty_title(mocker):
    response = httpx.Response(400, request=httpx.Request(
        method="POST", url="https://test.test"))
    mocker_post = mocker.patch.object(hook, "post", new_callable=AsyncMock, side_effect=httpx.HTTPStatusError(
        message="Error!", request=response.request, response=response))
    expected_body = {
        "embeds": [
            {
                "title": "",
                "url": "https://test.test",
                "color": 2
            }
        ]
    }

    with pytest.raises(expected_exception=httpx.HTTPStatusError):
        await hook.send_embedded_url(url="https://test.test", title="")

    mocker_post.assert_called_once()


@pytest.mark.asyncio
async def test_send_embedded_url_image_full(mocker):
    mocker_post = mocker.patch.object(hook, "post", new_callable=AsyncMock)

    expected_body = {
        "content": "test",
        "embeds": [{
            "image": {
                "url": "https://test.test"
            },
            "color": 2
        }]
    }

    await hook.send_embedded_url_image(
        url="https://test.test", message="test", color=2)

    mocker_post.assert_called_once_with(json=expected_body)


@pytest.mark.asyncio
async def test_send_embedded_url_image_empty_url(mocker):
    response = httpx.Response(400, request=httpx.Request(
        method="POST", url="https://test.test"))
    mocker_post = mocker.patch.object(hook, "post", new_callable=AsyncMock, side_effect=httpx.HTTPStatusError(
        message="Error!", request=response.request, response=response))

    with pytest.raises(expected_exception=httpx.HTTPStatusError):
        await hook.send_embedded_url_image(url="")

    mocker_post.assert_called_once()


@pytest.mark.asyncio
async def test_send_embedded_field_full(mocker):
    mocker_post = mocker.patch.object(hook, "post", new_callable=AsyncMock)

    expected_body = {
        "embeds": [{
            "fields": [{
                "name": "test",
                "value": "test",
                "inline": True
            }],
            "color": 2
        }]
    }

    await hook.send_embedded_field(names=["test"], values=[
        "test"], inline=[True], color=2)

    mocker_post.assert_called_once_with(json=expected_body)


@pytest.mark.asyncio
async def test_send_embedded_fields_empty_list(mocker):
    mocker_post = mocker.patch.object(hook, "post", new_callable=AsyncMock)

    with pytest.raises(expected_exception=ValueError, match="Lists must contain at least one element each!"):
        await hook.send_embedded_field(names=[], values=[], inline=[], color=2)

    mocker_post.assert_not_called()


@pytest.mark.asyncio
async def test_send_embedded_fields_not_same_len(mocker):
    mocker_post = mocker.patch.object(hook, "post", new_callable=AsyncMock)

    with pytest.raises(expected_exception=ValueError, match="Lengths of all lists must match!"):
        await hook.send_embedded_field(names=["test", "test"], values=[
            "test"], inline=[True], color=2)

    mocker_post.assert_not_called()
