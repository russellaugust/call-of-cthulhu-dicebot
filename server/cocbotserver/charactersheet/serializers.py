from dataclasses import fields
from rest_framework import serializers
from .models import Character, CharacterSkill, CharacterWeapon, DiscordMessage, Location, Player, Roll, DiscordChannel, Skill

        
class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        # fields = "__all__"
        fields = ('discord_id', 'name', 'discord_name', 'character')

class DiscordChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscordChannel
        fields = "__all__"

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"

class DiscordMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscordMessage
        fields = "__all__"
        
class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = "__all__"
        
class RollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roll
        fields = "__all__"

class CharacterWeaponSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacterWeapon
        # fields = ('name',)
        fields = "__all__"

class CharacterSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacterSkill
        fields = ('name', 'points', 'id', 'improve', 'favorite')

class CharacterSerializer(serializers.ModelSerializer):
    # player_fk = PlayerSerializer(read_only=True)
    # location_fk = LocationSerializer(read_only=True)
    characterskill_set = CharacterSkillSerializer(read_only=True, many=True)
    characterweapon_set = CharacterWeaponSerializer(read_only=True, many=True)
    
    class Meta:
        model = Character
        # fields = ('id', 'investigator_name', 'characterskill_set')
        fields = "__all__"
        
class CharacterStatsSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Character
        fields = ('strength','intelligence','appearance','dexterity',
                  'education','size','constitution','power','luck','hp',
                  'magic','san','move','damage_bonus','build')