from email.mime import base
from django.db import models

# Create your models here.

class Player(models.Model):
    name       = models.CharField(blank=False,max_length=32,help_text="")
    discord_id = models.IntegerField(blank=True,null=True,help_text="")

    def __str__(self):
        return str(f"{self.name}")

class DiscordMessage(models.Model):        
    messagetime = models.DateField()
    discord_id = models.IntegerField(blank=True,null=True,help_text="")
    user = models.ForeignKey(Player, on_delete=models.CASCADE,blank=True,null=True)
    channel = models.IntegerField(blank=True,null=True,help_text="")
    content = models.CharField(blank=True,max_length=500,help_text="")
    reply_msg_id = models.IntegerField(blank=True,null=True,help_text="")
        
    def __str__(self):
        return str(f"{self.messagetime}")

class Roll(models.Model):
    player_fk   = models.ForeignKey(Player, on_delete=models.CASCADE,blank=True,null=True)
    message_fk  = models.ForeignKey(DiscordMessage, on_delete=models.CASCADE,blank=True,null=True)
    messagetime = models.DateTimeField(auto_now_add=True, blank=True)
    argument    = models.CharField(blank=True,max_length=50,help_text="")
    equation    = models.CharField(blank=True,max_length=50,help_text="")
    result      = models.CharField(blank=True,max_length=50,help_text="")
    stat        = models.IntegerField(blank=True,null=True,help_text="")
    success     = models.CharField(blank=True,max_length=50,help_text="")
    comment     = models.CharField(blank=True,max_length=50,help_text="")

    def __str__(self):
        return str(f"{self.name}")

class Skill(models.Model):
    name            = models.CharField(blank=False,max_length=32,help_text="")
    description     = models.CharField(blank=True,max_length=6000,help_text="")
    base_points     = models.CharField(blank=False, default="0",max_length=32,help_text="")
    category        = models.CharField(blank=True,max_length=50,help_text="")
    specialization  = models.CharField(blank=True,max_length=32,help_text="")

    def __str__(self):
        if self.specialization == "":
            return str(f"{self.name}")
        else:
            return str(f"{self.name} ({self.specialization})")

class CharacterSkill(models.Model):
    skill_fk           = models.ForeignKey(Skill, on_delete=models.CASCADE,blank=True,null=False)
    base_calc_points   = models.IntegerField(default=0,blank=False,null=False,help_text="")
    personal_points    = models.IntegerField(default=0,blank=False,null=False,help_text="")
    occupation_points  = models.IntegerField(default=0,blank=False,null=False,help_text="")
    experience_points  = models.IntegerField(default=0,blank=False,null=False,help_text="")
    improve            = models.BooleanField(default=False,help_text="")
    favorite           = models.BooleanField(default=False,help_text="")

    def __str__(self):
        if self.skill_fk.specialization == "":
            return str(f"{self.skill_fk.name}")
        else:
            return str(f"{self.skill_fk.name} ({self.skill_fk.specialization})")
    
    def points(self):
        return int(self.skill_fk + self.personal_points + self.occupation_points + self.experience_points)

class Weapon(models.Model):
    skill_fk        = models.ForeignKey(Skill, on_delete=models.CASCADE,blank=True,null=True)
    name            = models.CharField(blank=False,max_length=32,help_text="")
    damage          = models.CharField(blank=True,max_length=32,help_text="")
    hands           = models.IntegerField(blank=True,null=True,help_text="")
    base_range      = models.CharField(blank=True,max_length=32,help_text="")
    uses_per_rnd    = models.IntegerField(blank=True,null=True,help_text="")
    magazine        = models.IntegerField(blank=True,null=True,help_text="")
    cost            = models.FloatField(blank=True,null=True, max_length=32,help_text="")
    malfunction     = models.IntegerField(blank=True,null=True,help_text="")
    common_in_era   = models.CharField(blank=True,max_length=32,help_text="")

    def __str__(self):
        return str(f"{self.name}")

class Character(models.Model):
    characterskill_fk   = models.ManyToManyField(CharacterSkill,blank=True)
    weapon_fk           = models.ManyToManyField(Weapon,blank=True)
    player_fk           = models.ForeignKey(Player, on_delete=models.CASCADE,blank=True,null=True)
    
    investigator_name   = models.CharField(verbose_name="Investigator",blank=False,max_length=50,help_text="")
    occupation          = models.CharField(blank=True,max_length=50,help_text="")
    birthplace          = models.CharField(blank=True,max_length=50,help_text="")
    sex                 = models.CharField(blank=True,max_length=10,help_text="")
    age                 = models.IntegerField(blank=True,null=True,help_text="")

    strength        = models.IntegerField(verbose_name="STR",blank=True,null=True,help_text="")
    intelligence    = models.IntegerField(verbose_name="INT",blank=True,null=True,help_text="")
    appearance      = models.IntegerField(verbose_name="APP",blank=True,null=True,help_text="")
    dexterity       = models.IntegerField(verbose_name="DEX",blank=True,null=True,help_text="")
    education       = models.IntegerField(verbose_name="EDU",blank=True,null=True,help_text="")
    size            = models.IntegerField(verbose_name="SIZ",blank=True,null=True,help_text="")
    constitution    = models.IntegerField(verbose_name="CON",blank=True,null=True,help_text="")
    power           = models.IntegerField(verbose_name="POW",blank=True,null=True,help_text="")
    luck            = models.IntegerField(blank=True,null=True,help_text="")

    hp              = models.IntegerField(blank=True,null=True,help_text="")
    magic           = models.IntegerField(blank=True,null=True,help_text="")
    san             = models.IntegerField(blank=True,null=True,help_text="")
    san_daystart    = models.IntegerField(blank=True,null=True,help_text="")

    temporary_insanity  = models.BooleanField(default=False,help_text="")
    indefinite_insanity = models.BooleanField(default=False,help_text="")
    dying_unconcious    = models.BooleanField(default=False,help_text="")
    dying_majorwound    = models.BooleanField(default=False,help_text="")

    def hp_max(self):
        return int((self.size+self.constitution)/10)

    def san_max(self):
        return int(99)

    def move(self):
        def age_modifier(move_value):
            if self.age   >= 80: return move_value-5
            elif self.age >= 70: return move_value-4
            elif self.age >= 60: return move_value-3
            elif self.age >= 50: return move_value-2
            elif self.age >= 40: return move_value-1
            else: return move_value

        if self.dexterity > self.size and self.strength > self.size:
            return age_modifier(9)
        elif self.dexterity >= self.size or self.strength >= self.size or self.dexterity == self.size == self.strength:
            return age_modifier(8)
        elif self.dexterity < self.size and self.strength < self.size:
            return age_modifier(7)

    def magic_max(self):
        return int(self.power/5)
    
    def damage_bonus(self):
        str_siz = self.strength + self.size
        if str_siz <= 64:    return str("-2")
        elif str_siz <= 84:  return str("-1")
        elif str_siz <= 124: return str("0")
        elif str_siz <= 164: return str("1D4")
        elif str_siz <= 204: return str("1D6")

    def build(self):
        str_siz = self.strength + self.size
        if str_siz <= 64:    return int(-2)
        elif str_siz <= 84:  return int(-1)
        elif str_siz <= 124: return int(0)
        elif str_siz <= 164: return int(1)
        elif str_siz <= 204: return int(2)

    def __str__(self):
        return str(f"{self.investigator_name}")
