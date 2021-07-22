#!/usr/bin/env python3

import yaml
import requests
import validators
import random
import os

SETTINGSFILE = "settings.yaml"

class Settings:

    def __init__(self):
        self.__settings__ = {}
        with open(SETTINGSFILE) as f:
            self.__settings__ = yaml.load(f, Loader=yaml.FullLoader)

    def __update__(self, field, info):
        with open(SETTINGSFILE, 'w') as outfile:
            self.__settings__[field] = info
            yaml.dump(self.__settings__, outfile, default_flow_style=False)

    def __refresh__(self):
        with open(SETTINGSFILE) as f:
            self.__settings__ = yaml.load(f, Loader=yaml.FullLoader)

    def list_of_properties(self):
        return list(self.__settings__.keys())

    def dictionary_of_properties(self):
        return self.__settings__
        
    @property
    def announce(self):
        self.__refresh__()
        return self.__settings__['announce']

    @announce.setter
    def announce(self, announce_bool):
        if isinstance(announce_bool, bool):
            self.__update__("announce", announce_bool)
        else:
            raise ValueError('This needs to be True or False')

    @property
    def database_enabled(self):
        self.__refresh__()
        return self.__settings__['database_enabled']

    @database_enabled.setter
    def database_enabled(self, input):
        self.__update__("database_enabled", input)


    @property
    def card_path(self):
        return self.__settings__['card_path']

    @card_path.setter
    def card_path(self, input):
        self.__update__("card_path", input)


    @property
    def database_path(self):
        return self.__settings__['database_path']

    @database_path.setter
    def database_path(self, input):
        self.__update__("database_path", input)


    @property
    def audio_rolls_path(self):
        self.__refresh__()
        return self.__settings__['audio_rolls_path']


    @property
    def voice_volume(self):
        self.__refresh__()
        return self.__settings__['voice_volume']

    @voice_volume.setter
    def voice_volume(self, input):
        self.__update__("voice_volume", input)

    @property
    def current_voice_path(self):
        audio_path = self.__settings__['audio_path']
        voice_subpath = self.__settings__['voice_subpath']
        audio_current_voice = self.__settings__['audio_current_voice']
        fullpath = os.path.join(audio_path, voice_subpath, audio_current_voice)
        return fullpath

    # GIFS

    @property
    def gifs_critical(self):
        self.__refresh__()
        return self.__settings__['gif_critical']

    @property
    def gif_random_critical(self):
        self.__refresh__()
        return random.choice(self.__settings__['gif_critical'])

    @gifs_critical.setter
    def gif_critical(self, input):
        self.__update__("gif_critical", input)

    @property
    def gifs_fumble(self):
        self.__refresh__()
        return self.__settings__['gif_fumble']

    @property
    def gif_random_fumble(self):
        self.__refresh__()
        return random.choice(self.__settings__['gif_fumble'])

    @gifs_fumble.setter
    def gif_fumble(self, input):
        self.__update__("gif_fumble", input)

    @property
    def gifs_lucky(self):
        self.__refresh__()
        return self.__settings__['gif_lucky']

    @property
    def gif_random_lucky(self):
        self.__refresh__()
        return random.choice(self.__settings__['gif_lucky'])

    @gifs_lucky.setter
    def gif_lucky(self, input):
        self.__update__("gif_lucky", input)

    def link_exists(self, link):
        if validators.url(link):
            request = requests.get(link)
            if request.status_code == 200:
                return True
            else:
                return False

    # Dice Rolls

    @property
    def dice_improve(self):
        self.__refresh__()
        return self.__settings__['dice_improve']

    @dice_improve.setter
    def dice_improve(self, input):
        self.__update__("dice_improve", input)

    @property
    def dice_default(self):
        self.__refresh__()
        return self.__settings__['dice_default']

    @dice_default.setter
    def dice_default(self, input):
        self.__update__("dice_default", input)

if __name__ == '__main__':
    x = Settings()
    #print (x.voice_volume)
    print (x.gif_random_lucky)
    print (x.gif_random_critical)
    print (x.current_voice_path)
    #x.link_exists(x.gif_lucky)
    print (x.database_enabled)