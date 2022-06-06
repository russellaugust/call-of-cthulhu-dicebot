from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Character, Skill
from .forms import CharacterForm
from django.shortcuts import render


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