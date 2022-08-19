from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Character, DiscordChannel, Location, Player, Skill, DiscordMessage, Roll
from .forms import CharacterForm
from django.shortcuts import render
from .serializers import DiscordMessageSerializer, LocationSerializer, PlayerSerializer, RollSerializer, DiscordChannelSerializer
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import serializers


# Create your views here.

def charactersheetform(request):
    # template with form structure for CRUD
    pass

def charactersheet(request, characterid):
    if request.method == 'POST':
        #data = json.load(request)
        print("bam")
        pass
        
    character = Character.objects.get(pk=characterid)
    #return HttpResponse("You're looking at %s." % obj.investigator_name)
    return render(request, 'charactersheet.html', {'character': character, 'characterid' : characterid})

def allcharacters(request):
    characters = Character.objects.all()
    allcharacternames = ""
    allcharacternames = [character.investigator_name for character in characters]
    return HttpResponse("You're looking at scene %s." % allcharacternames)

def get_character_characteristic(request, characterid, characteristic):
    '''return value of requested character characteristic'''
    if characteristic == "str": return HttpResponse(Character.objects.get(pk=characterid).strength)
    if characteristic == "int": return HttpResponse(Character.objects.get(pk=characterid).intelligence)
    if characteristic == "app": return HttpResponse(Character.objects.get(pk=characterid).appearance)
    if characteristic == "dex": return HttpResponse(Character.objects.get(pk=characterid).dexterity)
    if characteristic == "edu": return HttpResponse(Character.objects.get(pk=characterid).education)
    if characteristic == "siz": return HttpResponse(Character.objects.get(pk=characterid).size)
    if characteristic == "cond": return HttpResponse(Character.objects.get(pk=characterid).constitution)
    if characteristic == "pow": return HttpResponse(Character.objects.get(pk=characterid).power)
    if characteristic == "luck": return HttpResponse(Character.objects.get(pk=characterid).luck)
    if characteristic == "hp": return HttpResponse(Character.objects.get(pk=characterid).hp)
    if characteristic == "magic": return HttpResponse(Character.objects.get(pk=characterid).magic)
    if characteristic == "san": return HttpResponse(Character.objects.get(pk=characterid).san)
    else: return 0

    #return HttpResponse("Placeholder.")
    #return {'pick': characterid, 'all_picks': characteristic}

    # data = {
    #     'name': 'Vitor',
    # }

    # return JsonResponse(data)

def get_characteristics(request):
    '''return a list of all characteristics'''
    pass

def get_character_skill(request):
    '''return value of requested character skill'''
    pass

def get_character_skills(request):
    '''return list of skills character has'''
    pass

def get_skill(request, skillid):
    '''return information on the requested skill'''
    skill = {
        'name'          : Skill.objects.get(pk=skillid).name,
        'description'   : Skill.objects.get(pk=skillid).description,
        'base_points'   : Skill.objects.get(pk=skillid).base_points,
        'category'      : Skill.objects.get(pk=skillid).category,
        'specialization': Skill.objects.get(pk=skillid).specialization,
    }

    return JsonResponse(skill)

def get_skills(request):
    '''return all skills available for all characters'''
    skills = Skill.objects.all()
    return JsonResponse(
        {"skills" : [{
            'name'           : skill.name, 
            'id'             : skill.id, 
            'specialization' : skill.specialization}
            
            for skill in skills]}
    )
    
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


# @api_view(['GET','POST'])
# def api_message_create(request):
#     serializer = DiscordMessageSerializer(data=request.data, many=True)
#     if serializer.is_valid():
#         serializer.save()
#     else:
#         print(serializer.errors)
    
#     return Response(serializer.data)

# @api_view(['GET'])
# def api_message_get(request, discord_id):
#     message = DiscordMessage.objects.get(discord_id=discord_id)
#     serializer = DiscordMessageSerializer(instance=message, many=False)
#     return Response(serializer.data)

# @api_view(['POST'])
# def api_message_update(request, discord_id):
#     message = DiscordMessage.objects.get(discord_id=discord_id)
#     serializer = DiscordMessageSerializer(instance=message, data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#     else:
#         print(serializer.errors)
    
#     return Response(serializer.data)

@api_view(['POST'])
def api_roll_create(request):
    serializer = RollSerializer(data=request.data, many=True)
    if serializer.is_valid():
        serializer.save()
    else:
        print(serializer.errors)
    
    return Response(serializer.data)


class LocationView(viewsets.ModelViewSet):
    '''
    Access to the API for Player.
    '''
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

class PlayerlView(viewsets.ModelViewSet):
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
    
    # def post(self, request, *args, **kwargs):
    #     print('yes')
    #     return self.retrieve(request, *args, **kwargs)

    # def create(self, request):
    #     # do your thing here
    #     print("test")
    #     return super().create(request)

# class DiscordMessagePartialUpdateView(GenericAPIView, 
#                                       mixins.UpdateModelMixin, 
#                                       mixins.RetrieveModelMixin):
#     '''
#     Get or Update the DiscordMessage content using a discord_id.
#     '''
#     queryset = DiscordMessage.objects.all()
#     serializer_class = DiscordMessageSerializer
#     lookup_field = 'discord_id'

#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)
    
#     def put(self, request, *args, **kwargs):
#         return self.partial_update(request, *args, **kwargs)