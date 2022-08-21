from django.contrib import admin
from .models import Location, Character, Skill, Weapon, Player, CharacterSkill, CharacterWeapon
from .models import Roll, DiscordMessage, DiscordChannel

# Register your models here.
admin.site.register(Player)
admin.site.register(DiscordMessage)
admin.site.register(Roll)
admin.site.register(Character)
admin.site.register(Skill)
admin.site.register(Weapon)
admin.site.register(CharacterSkill)
admin.site.register(CharacterWeapon)
admin.site.register(Location)
admin.site.register(DiscordChannel)