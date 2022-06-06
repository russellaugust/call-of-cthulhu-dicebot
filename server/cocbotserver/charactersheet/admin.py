from django.contrib import admin
from .models import Character, Skill, Weapon, Player, RollHistory, CharacterSkill

# Register your models here.
admin.site.register(Player)
admin.site.register(Character)
admin.site.register(Skill)
admin.site.register(Weapon)
admin.site.register(RollHistory)
admin.site.register(CharacterSkill)

