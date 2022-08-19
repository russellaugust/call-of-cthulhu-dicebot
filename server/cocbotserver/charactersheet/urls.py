from django.urls import path, include
from . import views
from rest_framework import routers

app_name = "charactersheet"

router = routers.DefaultRouter()
router.register('discordmessage', views.DiscordMessageView)
router.register('discordchannel', views.DiscordChannelView)
router.register('player', views.PlayerlView)
router.register('roll', views.RollView)
router.register('location', views.LocationView)
# router.register("DiscordMessagePartial", views.DiscordMessagePartialUpdateView)

urlpatterns = [
    path('character/<int:characterid>', views.charactersheet, name='charactersheet'),
    path('skill/<int:skillid>', views.get_skill, name='get_skill'),
    path('skills/', views.get_skills, name='get_skills'),
    path('character/<int:characterid>/characteristic/<str:characteristic>', views.get_character_characteristic, name='get_character_characteristic'),
    path('characteristics/', views.get_characteristics, name='get_characteristics'),
    path('characters/', views.allcharacters, name='allcharacters'),
    
    # APIs
    path('player/<int:discord_id>', views.api_get_player_by_discord, name='api_get_player_by_discord'),
    path('players/', views.api_get_players, name='api_get_players'),
    
    # path('message/create', views.api_message_create, name='api_message_create'),

    # path('message/create', views.api_message_create, name='api_message_create'),
    # path('message/create2', views.DiscordMessageCreateView.as_view(), name='api_message_create2'),
    # path('message/update2/<int:discord_id>', views.DiscordMessagePartialUpdateView.as_view(), name='api_message_update2'),
    # path('message/update/<int:discord_id>', views.api_message_update, name='api_message_update'),
    # path('message/<int:discord_id>', views.api_message_get, name='api_message_get'),
    
    # path('roll/create', views.api_roll_create, name='api_roll_create'),
    
    path('', include(router.urls)),
]