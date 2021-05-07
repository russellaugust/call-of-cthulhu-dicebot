#!/usr/bin/env python3

import yaml
import requests
import validators

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
        return self.__settings__['audio_rolls_path']


    @property
    def voice_volume(self):
        self.__refresh__()
        return self.__settings__['voice_volume']

    @voice_volume.setter
    def voice_volume(self, input):
        self.__update__("voice_volume", input)


    @property
    def gif_critical(self):
        self.__refresh__()
        return self.__settings__['gif_critical']

    @gif_critical.setter
    def gif_critical(self, input):
        self.__update__("gif_critical", input)

    @property
    def gif_fumble(self):
        self.__refresh__()
        return self.__settings__['gif_fumble']

    @gif_fumble.setter
    def gif_fumble(self, input):
        self.__update__("gif_fumble", input)

    @property
    def gif_lucky(self):
        self.__refresh__()
        return self.__settings__['gif_lucky']

    @gif_lucky.setter
    def gif_lucky(self, input):
        self.__update__("gif_lucky", input)

    def link_exists(self, link):
        if validators.url(link):
            request = requests.get(link)
            if request.status_code == 200:
                print('Web site exists')
            else:
                print('Web site does not exist') 

if __name__ == '__main__':
    x = Settings()
    print (x.voice_volume)
    print (x.gif_critical)
    print (x.gif_fumble)
    print (x.gif_lucky)

    x.link_exists(x.gif_lucky)