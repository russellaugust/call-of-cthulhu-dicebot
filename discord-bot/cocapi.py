import discord
import requests, datetime

BASE_LINK = "http://localhost:8000"
API_LINK = "http://localhost:8000/api"

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
    
# CHARACTERS
def create_character(json: dict) -> dict:
    response = requests.post(url=f"{API_LINK}/character/", json=json)
    return response.json()

def attach_skillset_to_character(character_id: int, skillset_id: int) -> None:
    requests.get(url=f"{BASE_LINK}/character/{character_id}/attach_skills/{skillset_id}")
    
def character(id) -> dict:
    response = requests.get(url=f"{API_LINK}/character/{id}")
    return response.json()

# MESSAGES
def get_message(discord_id: int) -> dict:
    response = requests.get(url=f"{API_LINK}/discordmessage/{discord_id}")
    return response.json()

def create_message(json: dict) -> dict:
    print (json)
    response = requests.post(url=f"{API_LINK}/discordmessage/",json=json)
    print(response.content)
    return response.json()

def message_content_update(discord_id, content) -> dict:
    response = requests.patch(url=f"{API_LINK}/discordmessage/{discord_id}/",
                              json={'content' : content})
    return response.json()

def message_delete(discord_id) -> None:
    response = requests.delete(url=f"{API_LINK}/discordmessage/{discord_id}/")

# ROLLS
def create_roll(json: dict) -> dict:
    response = requests.post(url=f"{API_LINK}/roll/",json=json)
    return response.json()

def get_roll(id) -> dict:
    response = requests.get(url=f"{API_LINK}/roll/{id}")
    return response.json()

def get_rolls_history(channel_id, amount) -> dict:
    response = requests.get(url=f"{API_LINK}/roll/channel/{channel_id}/amount/{amount}")
    return response.json()

# SKILLS
def get_skillsets() -> dict:
    """ Get list of skillsets, a group of skills, to attach to character sheets. """
    response = requests.get(url=f"{API_LINK}/skillset/")
    return response.json()

def change_charskill(id, json) -> dict:
    """ change specific character skill fields with json patch. """
    response = requests.patch(url=f"{API_LINK}/characterskill/{id}/", json=json)
    return response.json()

def add_charskill(json) -> dict:
    """ Add a character skill to the character sheet. """
    response = requests.post(url=f"{API_LINK}/characterskill/", json=json)
    return response

def delete_charskill(id) -> dict:
    """ Delete a character's skill. """
    response = requests.delete(url=f"{API_LINK}/characterskill/{id}")
    return response

def change_stat(id, json) -> dict:
    """ change specific fields with json patch """
    response = requests.patch(url=f"{API_LINK}/character/{id}/", json=json)
    return response