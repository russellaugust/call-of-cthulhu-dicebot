from django.contrib import admin
from .models import Character, Skill, Weapon, Player, Roll, CharacterSkill

# Register your models here.
admin.site.register(Player)
admin.site.register(Character)
admin.site.register(Skill)
admin.site.register(Weapon)
admin.site.register(Roll)
admin.site.register(CharacterSkill)

