from django.urls import path
from . import views

app_name = "charactersheet"

urlpatterns = [
    path('character/<int:characterid>', views.charactersheet, name='charactersheet'),
    path('skill/<int:skillid>', views.get_skill, name='get_skill'),
    path('skills/', views.get_skills, name='get_skills'),
    path('character/<int:characterid>/characteristic/<str:characteristic>', views.get_character_characteristic, name='get_character_characteristic'),
    path('characteristics', views.get_characteristics, name='get_characteristics'),
    path('characters/', views.allcharacters, name='allcharacters'),
    # path('upload-metadata-adapter/', views.data_adapter, name='data_adapter'),
    # path('data-adapter-valid/', views.data_adapter_valid, name='data_adapter_valid'),
    # path('<str:scene>/', views.scene, name='scene'),
    # path('<str:scene>/<str:setup>/', views.setup, name='scenesetup'),
    # path('<str:scene>/<str:setup>/<int:take>/', views.take, name='scene_take'),
]