from dataclasses import fields
from rest_framework import serializers
from .models import Character, CharacterSkill, CharacterWeapon, DiscordMessage, Location, Player, Roll, DiscordChannel, Skill, SkillSet


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
        
class SkillSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillSet
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
    name = serializers.ReadOnlyField()
    class Meta:
        model = CharacterSkill
        # fields = ('name', 'points', 'id', 'improve', 'favorite')
        fields = ('name', 'name_override', 'id', 'skill_fk', 'character_fk', 
                  'personal_points', 'occupation_points', 'experience_points', 
                  'points', 'improve', 'favorite')

class CharacterSerializer(serializers.ModelSerializer):
    # player_fk = PlayerSerializer(read_only=True)
    # location_fk = LocationSerializer(read_only=True)
    characterskill_set = CharacterSkillSerializer(read_only=True, many=True)
    characterweapon_set = CharacterWeaponSerializer(read_only=True, many=True)
    alias = serializers.ReadOnlyField()
    
    hp_max = serializers.ReadOnlyField()
    san_max = serializers.ReadOnlyField()
    move = serializers.ReadOnlyField()
    magic_max = serializers.ReadOnlyField()
    damage_bonus = serializers.ReadOnlyField()
    build = serializers.ReadOnlyField()
    
    class Meta:
        model = Character
        fields = "__all__"
        
class CharacterStatsSerializer(serializers.ModelSerializer):
    """ use only to return the stats list """  
    class Meta:
        model = Character
        fields = ('strength','intelligence','appearance','dexterity',
                  'education','size','constitution','power','luck','hp',
                  'magic','san','move','damage_bonus','build')

class PlayerSerializer(serializers.ModelSerializer):
    # character = CharacterSerializer(read_only=True)
    
    class Meta:
        model = Player
        # fields = "__all__"
        fields = ('discord_id', 'name', 'discord_name', 'character', 'id')
        
class RollExtendedSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)
    class Meta:
        model = Roll
        fields = "__all__"