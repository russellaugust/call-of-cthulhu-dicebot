from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Character, CharacterSkill, DiscordChannel, Location, Player, Skill, DiscordMessage, Roll, SkillSet
from .forms import CharacterForm, CharacterSkillsForm, SkillForm
from django.shortcuts import render
from .serializers import CharacterSerializer, CharacterSkillSerializer, CharacterStatsSerializer, DiscordMessageSerializer, LocationSerializer, PlayerSerializer, RollExtendedSerializer, RollSerializer, DiscordChannelSerializer, SkillSerializer, SkillSetSerializer
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import serializers
from django.forms import inlineformset_factory, modelformset_factory


# Create your views here.

def attach_player(request, character_pk, player_discord_id):
    """ Attach a character to a player."""
    character = Character.objects.get(pk=character_pk)
    player = Player.objects.get(discord_id=player_discord_id)
    print (hasattr(player, 'character'))
    print (character.player_fk)
    if not hasattr(player, 'character') and character.player_fk is None:
        character.player_fk = player
        character.save()
        return JsonResponse({"success":True})
    else:
        return JsonResponse({"success":False})

def release_character(request,  player_discord_id):
    """ Release a character from a player."""
    player = Player.objects.get(discord_id=player_discord_id)
    if hasattr(player, 'character'):
        character = player.character
        character.player_fk = None
        character.save()
        return JsonResponse({"success":True})
    else:
        return JsonResponse({"success":False})
    
def attach_skillset(request, character_pk, skillset_pk):
    # if request.method == 'POST':
    
    character = Character.objects.get(pk=character_pk)

    # get skills that already exist for character
    char_skills = character.characterskill_set.all() #.values_list('id', flat=True)
    char_skills_idlist = char_skills.values_list('skill_fk', flat=True)
    
    skillset = SkillSet.objects.get(pk=skillset_pk).skills.all()        
    
    skills_to_add = [skill for skill in skillset if skill.id not in char_skills_idlist]
    
    for skill in skills_to_add:
        skill = CharacterSkill(skill_fk=skill, character_fk=character)
        skill.save()
    
    return JsonResponse({"success":True})

def edit_skills(request):
    SkillFormSet = modelformset_factory(model=Skill,
                                   form=SkillForm,
                                   extra=3 )
    formset = SkillFormSet()
    
    if request.method == 'POST':
        formset = SkillFormSet(request.POST)
        if formset.is_valid():
            formset.save()
        else:
            print(formset.errors)

    context = {'formset':formset}
    return render(request, 'skills.html', context)
        
def edit_character_skills(request, character_pk):
    CharacterSkillFormSet = inlineformset_factory(
        parent_model=Character, 
        model=CharacterSkill, 
        form=CharacterSkillsForm)
    character = Character.objects.get(pk=character_pk)
    formset = CharacterSkillFormSet(instance=character)
    
    if request.method == 'POST':
        formset = CharacterSkillFormSet(request.POST, instance=character)
        if formset.is_valid():
            formset.save()
        else:
            print(formset.errors)

    context = {'formset':formset}
    return render(request, 'characterskills.html', context)
    
def favorite_charskill(request, charskill_pk):
    """favorites the skill"""
    pass


def charactersheetform(request):
    # template with form structure for CRUD
    pass

def charactersheet(request, characterid):
    if request.method == 'POST':
        #data = json.load(request)
        
        pass
        
    character = Character.objects.get(pk=characterid)
    
    #return HttpResponse("You're looking at %s." % obj.investigator_name)
    return render(request, 'charactersheet.html', {'character': character})

# def allcharacters(request):
#     characters = Character.objects.all()
#     allcharacternames = ""
#     allcharacternames = [character.investigator_name for character in characters]
#     return HttpResponse("You're looking at scene %s." % allcharacternames)

# def get_character_characteristic(request, characterid, characteristic):
#     '''return value of requested character characteristic'''
#     if characteristic == "str": return HttpResponse(Character.objects.get(pk=characterid).strength)
#     if characteristic == "int": return HttpResponse(Character.objects.get(pk=characterid).intelligence)
#     if characteristic == "app": return HttpResponse(Character.objects.get(pk=characterid).appearance)
#     if characteristic == "dex": return HttpResponse(Character.objects.get(pk=characterid).dexterity)
#     if characteristic == "edu": return HttpResponse(Character.objects.get(pk=characterid).education)
#     if characteristic == "siz": return HttpResponse(Character.objects.get(pk=characterid).size)
#     if characteristic == "cond": return HttpResponse(Character.objects.get(pk=characterid).constitution)
#     if characteristic == "pow": return HttpResponse(Character.objects.get(pk=characterid).power)
#     if characteristic == "luck": return HttpResponse(Character.objects.get(pk=characterid).luck)
#     if characteristic == "hp": return HttpResponse(Character.objects.get(pk=characterid).hp)
#     if characteristic == "magic": return HttpResponse(Character.objects.get(pk=characterid).magic)
#     if characteristic == "san": return HttpResponse(Character.objects.get(pk=characterid).san)
#     else: return 0

# def get_skills(request):
#     '''return all skills available for all characters'''
#     skills = Skill.objects.all()
#     return JsonResponse(
#         {"skills" : [{
#             'name'           : skill.name, 
#             'id'             : skill.id, 
#             'specialization' : skill.specialization}
            
#             for skill in skills]}
#     )
    
# API methods

from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def api_get_players(request):
    players = Player.objects.all()
    serializer = PlayerSerializer(players, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def api_get_player_by_discord(request, discord_id):
    player = Player.objects.get(discord_id=discord_id)
    serializer = PlayerSerializer(player, many=False)
    return Response(serializer.data)

@api_view(['GET'])
def api_get_character_stats(request, character_id):
    character = Character.objects.get(id=character_id)
    serializer = CharacterStatsSerializer(character, many=False)
    return Response(serializer.data)


@api_view(['POST'])
def api_roll_create(request):
    serializer = RollSerializer(data=request.data, many=True)
    if serializer.is_valid():
        serializer.save()
    else:
        print(serializer.errors)
    
    return Response(serializer.data)


class CharacterView(viewsets.ModelViewSet):
    '''
    Access to the API for Player.
    '''
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer
    
class LocationView(viewsets.ModelViewSet):
    '''
    Access to the API for Player.
    '''
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

class PlayerView(viewsets.ModelViewSet):
    '''
    Access to the API for Player.
    '''
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    
    lookup_field = 'discord_id'

class DiscordChannelView(viewsets.ModelViewSet):
    '''
    Access to the API for DiscordChannel.
    '''
    queryset = DiscordChannel.objects.all()
    serializer_class = DiscordChannelSerializer
    
    lookup_field = 'channel_id'
    
class RollExtendedView(viewsets.ModelViewSet):
    '''
    Access to the API for Roll.
    '''
    queryset = Roll.objects.all()
    serializer_class = RollExtendedSerializer
    
    def get_queryset(self):
        # print ()
        channel_id = int(self.kwargs['channel_id'])
        num_items = int(self.kwargs['num_items'])
        channel = DiscordChannel.objects.get(channel_id=channel_id)
        queryset = Roll.objects.filter(omit=False, discordchannel=channel).order_by('-messagetime')[:num_items]
        # queryset = Roll.objects.filter(omit=False).order_by('-messagetime')
        return queryset

class RollView(viewsets.ModelViewSet):
    '''
    Access to the API for Roll.
    '''
    queryset = Roll.objects.all()
    serializer_class = RollSerializer

class DiscordMessageView(viewsets.ModelViewSet):
    '''
    Interact with DiscordMessage, discord_id for retrieval.
    '''
    queryset = DiscordMessage.objects.all()
    serializer_class = DiscordMessageSerializer
    
    # use the message discord_id to retrieve the message.
    lookup_field = 'discord_id'
    
class SkillView(viewsets.ModelViewSet):
    '''
    Interact with Skill.
    '''
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    
class SkillSetView(viewsets.ModelViewSet):
    '''
    Interact with SkillSet.
    '''
    queryset = SkillSet.objects.all()
    serializer_class = SkillSetSerializer
    
class CharacterSkillView(viewsets.ModelViewSet):
    '''
    Interact with a character's skill.
    '''
    queryset = CharacterSkill.objects.all()
    serializer_class = CharacterSkillSerializer