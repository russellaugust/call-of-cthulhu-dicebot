from django.contrib import admin
from .models import Location, Character, Skill, SkillSet, Weapon, Player, CharacterSkill, CharacterWeapon
from .models import Roll, DiscordMessage, DiscordChannel
from .forms import SkillAdminForm

# Register your models here.
admin.site.register(Player)
admin.site.register(Roll)
admin.site.register(Character)
# admin.site.register(Skill)
admin.site.register(Weapon)
admin.site.register(CharacterSkill)
admin.site.register(CharacterWeapon)
admin.site.register(Location)
admin.site.register(DiscordChannel)
admin.site.register(SkillSet)

@admin.register(DiscordMessage)
class DiscordMessageAdmin(admin.ModelAdmin):
    ordering = ['-discord_id']
# admin.site.register(DiscordMessage)

class SkillAdmin(admin.ModelAdmin):
    form = SkillAdminForm
    
admin.site.register(Skill, SkillAdmin)