from email.mime import base
from unicodedata import name
from django.db import models
from django.core.validators import RegexValidator
import math


# Create your models here.

class Player(models.Model):
    name         = models.CharField(blank=True,max_length=32,help_text="")
    discord_name = models.CharField(blank=False,max_length=32,help_text="")
    discord_id   = models.IntegerField(unique=True,blank=False,null=False,help_text="")

    def __str__(self):
        return str(f"{self.discord_name} aka {self.name}")
    
    
class DiscordChannel(models.Model):
    name       = models.CharField(blank=False,max_length=100,help_text="")
    channel_id = models.IntegerField(unique=True,blank=False,null=False,help_text="")
    parent_id  = models.IntegerField(blank=True,null=True,help_text="")
    
    def __str__(self):
        return str(f"{self.name}: {self.channel_id}")


class DiscordMessage(models.Model): 
    messagetime = models.DateTimeField(blank=False)
    discord_id = models.IntegerField(unique=True,blank=False,null=False,help_text="")
    content = models.CharField(blank=True,max_length=2500,help_text="")
    reply_msg_id = models.IntegerField(blank=True,null=True,help_text="")
    
    player  = models.ForeignKey(Player, on_delete=models.CASCADE,blank=False,null=False)
    discordchannel = models.ForeignKey(DiscordChannel, on_delete=models.CASCADE,blank=False,null=False)
        
    def __str__(self):
        return str(f"{self.player.discord_name} - MSG{self.discord_id} - {self.messagetime}")

class Roll(models.Model):
    messagetime = models.DateTimeField(blank=False)
    argument    = models.CharField(blank=True,null=True,max_length=50,help_text="")
    equation    = models.CharField(blank=True,null=True,max_length=50,help_text="")
    result      = models.CharField(blank=True,null=True,max_length=50,help_text="")
    stat        = models.IntegerField(blank=True,null=True,help_text="")
    success     = models.CharField(blank=True,null=True,max_length=50,help_text="")
    comment     = models.CharField(blank=True,null=True,max_length=100,help_text="")
    omit        = models.BooleanField(blank=False,null=False,help_text="")
    
    player      = models.ForeignKey(Player, on_delete=models.CASCADE,blank=True,null=True)
    discordchannel     = models.ForeignKey(DiscordChannel, on_delete=models.CASCADE,blank=False,null=False)

    def __str__(self):
        return " | ".join(filter(None, 
                                 [str(self.player),
                                 f"{self.messagetime:%Y-%m-%d %H:%M:%S}", 
                                 self.argument, 
                                 self.success]))
        # return str(f"{self.name}")

class Location(models.Model):
    place    = models.CharField(blank=False,max_length=32,help_text="")
    INT_EXT_CHOICES = [
        ('INT', 'Interior'),
        ('EXT', 'Exterior'),
        ('INT/EXT', 'Interior/Exterior'),]
    int_ext     = models.CharField(blank=False,max_length=32,choices=INT_EXT_CHOICES,help_text="")
    description = models.CharField(blank=True,max_length=2000,help_text="")
    connection  = models.ManyToManyField("self",blank=True,help_text="")

    def __str__(self):
        return str(f"{self.int_ext} - {self.place}")


stats_equation = RegexValidator(
            regex=r'^(?:STR|INT|APP|DEX|EDU|SIZ|CON|POW){0,1}[/*+-]{0,1}\d+$',
            message='Must be simple equation with STR|INT|APP|DEX|EDU|SIZ|CON|POW ie DEX/2',
            code='invalid_equation')

class Skill(models.Model):
    name            = models.CharField(blank=False,max_length=32,help_text="")
    description     = models.CharField(blank=True,max_length=6000,help_text="")
    base_points     = models.CharField(blank=False, default="0",validators=[stats_equation],max_length=32,help_text="")
    category        = models.CharField(blank=True,max_length=50,help_text="")
    specialization  = models.CharField(blank=True,max_length=32,help_text="")

    def __str__(self):
        if self.specialization == "":
            return str(f"{self.name} ({self.base_points})")
        else:
            return str(f"{self.name} ({self.specialization}) ({self.base_points})")
        
class SkillSet(models.Model):
    """Model holding sets of skills for applying to a character."""
    name            = models.CharField(blank=False,max_length=32,unique=True,help_text="Name of the skill grouping.")
    description     = models.CharField(blank=True,max_length=100,help_text="Brief explanation of the use of the group.")
    skills          = models.ManyToManyField(Skill, related_name="skills")
    
    def __str__(self):
        return str(self.name)


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
    location_fk         = models.ForeignKey(Location, on_delete=models.CASCADE,blank=True,null=True)
    player_fk           = models.OneToOneField(Player, on_delete=models.CASCADE,blank=True,null=True)
    
    passcode           = models.CharField(max_length=255, blank=True, default="", help_text="Passcode for your character's safety.")
    
    investigator_name       = models.CharField(verbose_name="Investigator Name",blank=False,max_length=50,help_text="")
    investigator_alias      = models.CharField(verbose_name="Investigator Alias",blank=True,default="",max_length=25,help_text="")
    occupation              = models.CharField(blank=True,max_length=50,help_text="")
    birthplace              = models.CharField(blank=True,max_length=50,help_text="")
    sex                     = models.CharField(blank=True,max_length=10,help_text="")
    age                     = models.IntegerField(blank=True,null=True,help_text="")

    strength        = models.IntegerField(verbose_name="STR",blank=True,null=True,help_text="")
    intelligence    = models.IntegerField(verbose_name="INT",blank=True,null=True,help_text="")
    appearance      = models.IntegerField(verbose_name="APP",blank=True,null=True,help_text="")
    dexterity       = models.IntegerField(verbose_name="DEX",blank=True,null=True,help_text="")
    education       = models.IntegerField(verbose_name="EDU",blank=True,null=True,help_text="")
    size            = models.IntegerField(verbose_name="SIZ",blank=True,null=True,help_text="")
    constitution    = models.IntegerField(verbose_name="CON",blank=True,null=True,help_text="")
    power           = models.IntegerField(verbose_name="POW",blank=True,null=True,help_text="")
    luck            = models.IntegerField(blank=True,null=True,help_text="")

    hp              = models.IntegerField(verbose_name="HP",blank=True,null=True,help_text="")
    magic           = models.IntegerField(verbose_name="Magic",blank=True,null=True,help_text="")
    san             = models.IntegerField(verbose_name="SAN",blank=True,null=True,help_text="")
    san_daystart    = models.IntegerField(verbose_name="START",blank=True,null=True,help_text="")

    temporary_insanity  = models.BooleanField(default=False,help_text="")
    indefinite_insanity = models.BooleanField(default=False,help_text="")
    dying_unconcious    = models.BooleanField(default=False,help_text="")
    dying_majorwound    = models.BooleanField(default=False,help_text="")
    
    def alias(self):
        if self.investigator_alias:
            return self.investigator_alias
        else:
            return self.investigator_name

    def hp_max(self):
        return int((self.size+self.constitution)/10)

    def san_max(self):
        # TODO needs to be a calculation off of the mythos skill
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
    
class CharacterSkill(models.Model):
    skill_fk           = models.ForeignKey(Skill, on_delete=models.CASCADE,blank=False,null=False)
    character_fk       = models.ForeignKey(Character, on_delete=models.CASCADE,blank=False,null=False)
    name_override      = models.CharField(null=True,blank=True,max_length=32,help_text="Overrides the original skill name for just this character. Useful for things like Arts and Crafts or Language.")
    personal_points    = models.IntegerField(default=0,blank=False,null=False,help_text="Points distributed from Personal pool.")
    occupation_points  = models.IntegerField(default=0,blank=False,null=False,help_text="Points distributed from chosen Occupation pool.")
    experience_points  = models.IntegerField(default=0,blank=False,null=False,help_text="All points beyond Base, Personal and Occupation.")
    improve            = models.BooleanField(default=False,help_text="")
    favorite           = models.BooleanField(default=False,help_text="")

    def __str__(self):
        return self.name()
        
    def name(self):
        if self.name_override:
            return self.name_override
        else:
            return ' - '.join(
                filter(None, [self.skill_fk.name, self.skill_fk.specialization])
                )
            
    def base_points(self):
        base_points = self.skill_fk.base_points
        if "STR" in self.skill_fk.base_points:
            base_points = self.skill_fk.base_points.replace("STR", str(self.character_fk.strength))
        elif "INT" in self.skill_fk.base_points:
            base_points = self.skill_fk.base_points.replace("INT", str(self.character_fk.intelligence))
        elif "APP" in self.skill_fk.base_points:
            base_points = self.skill_fk.base_points.replace("APP", str(self.character_fk.appearance))
        elif "DEX" in self.skill_fk.base_points:
            base_points = self.skill_fk.base_points.replace("DEX", str(self.character_fk.dexterity))
        elif "EDU" in self.skill_fk.base_points:
            base_points = self.skill_fk.base_points.replace("EDU", str(self.character_fk.education))
        elif "SIZ" in self.skill_fk.base_points:
            base_points = self.skill_fk.base_points.replace("SIZ", str(self.character_fk.size))
        elif "CON" in self.skill_fk.base_points:
            base_points = self.skill_fk.base_points.replace("CON", str(self.character_fk.constitution))
        elif "POW" in self.skill_fk.base_points:
            base_points = self.skill_fk.base_points.replace("POW", str(self.character_fk.power))
            
        # return a floor value
        return math.floor(eval(base_points))

    def points(self):
        return int(self.base_points() + self.personal_points + self.occupation_points + self.experience_points)

class CharacterWeapon(models.Model):
    weapon_fk          = models.ForeignKey(Weapon, on_delete=models.CASCADE,blank=False,null=False)
    character_fk       = models.ForeignKey(Character, on_delete=models.CASCADE,blank=False,null=False)
    favorite           = models.BooleanField(default=False,help_text="")

    def __str__(self):
        return str(f"{self.weapon_fk.name}")
    
    def name(self):
        return str(f"{self.weapon_fk.name}")