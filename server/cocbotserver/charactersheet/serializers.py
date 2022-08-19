from dataclasses import fields
from rest_framework import serializers
from .models import DiscordMessage, Location, Player, Roll, DiscordChannel


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = "__all__"

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
        
class RollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roll
        fields = "__all__"
