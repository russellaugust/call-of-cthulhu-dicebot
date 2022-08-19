import discord
import requests, datetime

API_LINK = "http://localhost:8000/charactersheet"

def __response_valid__(response):
    try:
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as e:
        # Whoops it wasn't a 200
        return False

def get_or_create_player(json: dict) -> dict:
    discord_id = json.get('discord_id', None)
    response = requests.get(url=f"{API_LINK}/player/{discord_id}")
    if __response_valid__(response):
        return response.json()
    else:
        response = requests.post(url=f"{API_LINK}/player/", json=json)
        return response.json()

def get_or_create_channel(json: dict) -> dict:
    channel_id = json.get('channel_id', None)
    response = requests.get(url=f"{API_LINK}/discordchannel/{channel_id}")
    if __response_valid__(response):
        return response.json()
    else:
        response = requests.post(url=f"{API_LINK}/discordchannel/", json=json)
        return response.json()

def get_message(discord_id: int) -> dict:
    response = requests.get(url=f"{API_LINK}/discordmessage/{discord_id}")
    return response.json()

def create_message(json: dict) -> dict:
    response = requests.post(url=f"{API_LINK}/discordmessage/",json=json)
    return response.json()

def message_content_update(discord_id, content) -> dict:
    response = requests.patch(url=f"{API_LINK}/discordmessage/{discord_id}/",
                              json={'content' : content})
    return response.json()

def message_delete(discord_id):
    response = requests.delete(url=f"{API_LINK}/discordmessage/{discord_id}/")

def create_roll(json: dict) -> dict:
    response = requests.post(url=f"{API_LINK}/roll/",json=json)
    return response.json()


# player = get_or_create_player(json={
#     "name": "",
#     "discord_name": "test name",
#     "discord_id": 2342342323 })

# print(player)

# channel = get_or_create_channel(json={
#     "name": "Testing Channel2",
#     "channel_id": 1234,
#     "parent_id": 7839 })

# print(channel)

# message = create_message(json={
#     "messagetime": "2022-08-16T19:34:00Z",
#     "discord_id": 12345221,
#     "content": "TEST!",
#     "reply_msg_id": 9876,
#     "player": player.get('id'),
#     "discordchannel": channel.get('id') })

# print(message)

# message = message_content_update(discord_id=12345221, content="UPDATE!")
# print(message)

message_delete(1008880879508140092)