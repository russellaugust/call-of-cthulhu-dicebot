from django.forms import ModelForm
from .models import Character, CharacterSkill, Skill

class CharacterForm(ModelForm):
    class Meta:
        model = Character
        fields = "__all__"
        
class SkillForm(ModelForm):
    class Meta:
        model = Skill
        fields = "__all__"
        
class CharacterSkillsForm(ModelForm):
    # skill = Skill.objects.all()
    # skill = SkillForm()
    
    class Meta:
        model = CharacterSkill
        # fields = "__all__"
        fields = ('skill_fk', 'personal_points', 'occupation_points', 'experience_points', 'improve', 'favorite')