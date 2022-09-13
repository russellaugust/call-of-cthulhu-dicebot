from django.forms import ModelForm, Textarea
from .models import Character, CharacterSkill, Skill

class CharacterForm(ModelForm):
    class Meta:
        model = Character
        fields = "__all__"
        
class SkillForm(ModelForm):
    class Meta:
        model = Skill
        fields = "__all__"
        widgets = {
            'description': Textarea(attrs={'cols': 100, 'rows': 20}),
        }
        
class SkillAdminForm(ModelForm):
    class Meta:
        model = Skill
        fields = "__all__"
        widgets = {
            'description': Textarea(attrs={'cols': 80, 'rows': 20}),
        }
        
class CharacterSkillsForm(ModelForm):
    class Meta:
        model = CharacterSkill
        # fields = "__all__"
        fields = ('skill_fk', 'personal_points', 'occupation_points', 'experience_points', 'improve', 'favorite')