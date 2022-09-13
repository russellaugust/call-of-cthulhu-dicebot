from django.urls import path, re_path, include
from . import views
from rest_framework import routers

app_name = "charactersheet"

# API routers
router = routers.DefaultRouter()
router.register('discordmessage', views.DiscordMessageView)
router.register('discordchannel', views.DiscordChannelView)
router.register('player', views.PlayerView)
router.register('roll', views.RollView)
router.register(r'roll/channel/(?P<channel_id>\d+)/amount/(?P<num_items>\d+)', viewset=views.RollExtendedView)
router.register('location', views.LocationView)
router.register('character', views.CharacterView)
router.register('skill', views.SkillView)
router.register('characterskill', views.CharacterSkillView)
router.register('skillset', views.SkillSetView)

urlpatterns = [
    path('character/<int:characterid>', views.charactersheet, name='charactersheet'),
    path('character/<int:character_pk>/attach_skills/<int:skillset_pk>', views.attach_skillset, name='attach_skillset'),
    path('character/<int:character_pk>/attach_player/<int:player_discord_id>', views.attach_player, name='attach_player'),
    path('player/<int:player_discord_id>/release_character', views.release_character, name='release_character'),
    
    path('character/<int:character_pk>/skills/', views.edit_character_skills, name='edit_character_skills'),
    path('skills/', views.edit_skills, name='edit_skills'),
    
    # APIs
    path('character-stats/<int:character_id>', views.api_get_character_stats, name='api_get_character_stats'),
    path('players/', views.api_get_players, name='api_get_players'),
    
    path('api/', include(router.urls)),
]