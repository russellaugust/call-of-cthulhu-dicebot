import enum
import re, random, ast, time, datetime, secrets

from asyncio.base_events import _run_until_complete_cb

from asyncio.runners import run

UNARY_OPS = (ast.UAdd, ast.USub)
BINARY_OPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod)

class RollResult:
  def __init__(self, argument=None, equation=None, sumtotal=None, stat=None, comment=None, timestamp=None, user=None, nick=None, channel=None, guild=None, secret=False, omit=False):
    '''this will eventually be an additional class that holds the results of rolls since there's a possible scenario for multi-rolling'''
    self.argument = argument
    self.equation = equation
    self.sumtotal = sumtotal
    self.stat = stat
    self.comment = comment
    self.timestamp = timestamp
    self.user = user
    self.nick = nick
    self.channel = channel
    self.guild = guild
    self.secret = secret
    self.omit = omit

  def __str__(self) -> str:
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.timestamp))
    return f"{timestamp} {self.user}/{self.nick}@{self.channel}@{self.guild}: {self.argument} {self.equation} {self.sumtotal} {self.stat} {self.comment} Omit: {self.omit}"
  
  def get_string(self):
    '''return an appropriate string for the content'''
    pretty_string = ""
    if self.stat:
      pretty_string = f"{self.sumtotal} is a **{self.get_success()}**"
    else:
      pretty_string = f"{self.equation} = {self.sumtotal}"

    if self.omit:
        pretty_string = f"~~{pretty_string}~~"

    return pretty_string
  
  def get_timestamp(self):
    return self.timestamp
  
  def get_timestamp_datetime(self):
    return time.localtime(self.timestamp)
  
  def get_timestamp_pretty(self):
    #return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(1347517370))
    return datetime.datetime.fromtimestamp(self.timestamp).strftime('%c')

  def get_argument(self):
    return self.argument
    
  def get_equation(self):
    return self.equation
    
  def get_sumtotal(self):
    return self.sumtotal

  def get_stat(self):
    return self.stat

  def stat_exists(self):
    if self.get_success() is not None:
      return True
    else:
      return False

  def is_real(self):
    if self.get_sumtotal() is not None:
      return True
    else:
      return False

  def get_user(self):
    return self.user

  def get_nick(self):
    return self.nick

  def get_channel(self):
    return self.channel

  def get_guild(self):
    return self.guild

  def is_omitted(self):
      return self.omit

  def get_success(self):
    total = self.get_sumtotal()
    stat = self.get_stat()
    if stat is not None:
      success = self.success_status(total, int(stat))
      return success
    else:
      return None

  def get_success_color(self):
    total = self.get_sumtotal()
    stat = self.get_stat()
    if stat is not None:
      success_color = self.success_status_color(total, int(stat))
      return success_color
    else:
      return 0x0968ed

  def get_comment(self):
    return self.comment
  
  def success_status(self, myroll, stat):
    result = ''
    if myroll == 1:
        result = 'critical'
    elif stat <= 50 and myroll >= 96:
        result = 'fumble'
    elif stat > 50 and myroll >= 99:
        result = 'fumble'
    elif myroll <= stat/5:
        result = 'extreme success'
    elif myroll <= stat/2:
        result = 'hard success'
    elif myroll < stat:
        result = 'normal success'
    elif myroll == stat:
        result = 'lucky success'
    elif myroll > stat:
        result = 'fail'
    return result

  def success_status_color(self, myroll, stat):
    '''returns a color based on success level'''
    result = 0x0968ed # blue
    if myroll == 1:
      result = 0xed0909 # critical
    elif stat <= 50 and myroll >= 96:
      result = 0xfc6805 # fumble
    elif stat > 50 and myroll >= 99:
      result = 0xfc6805 # fumble
    elif myroll <= stat/5:
      result = 0x05fc1a # extreme success
    elif myroll <= stat/2:
      result = 0x60ed09 # hard success
    elif myroll < stat:
      result = 0xb8ed09 # normal success
    elif myroll == stat:
      result = 0xed09d6 # lucky success
    elif myroll > stat:
      result = 0xed0909 # fail
    return result
  
  def error(self):
    return True if self.get_sumtotal is None else False
  


class DiceRolls:
  def __init__(self, rolls_arg, repeat=1, keep=0):
    # omit is a + or - integer. +1 means the highest 1 roll, -1 means lowest 1 roll, 0 means keep all rolls. +2 is highest 2 rolls, etc.
    self.rolls = []
    omit = True if keep > 0 or keep < 0 else False
    rolls_arg = rolls_arg.lower() # normalize the argument
    
    # roll the dice [repeat] times and sets omit state for all rolls
    self.rolls = [self.roll_the_dice(rolls_arg, omit=omit) for x in range(0, repeat)]

    if omit is True and self.rolls[0].is_real():
        '''this will reprocess the rolls and mark the correct set as valid or invalid.'''
        # sort the results and pick the top or bottom n results.  Set the rolls field to omit true false
        #most = max(roll.get_sumtotal() for roll in self.rolls)
        rolls_sorted = sorted((roll.get_sumtotal() for roll in self.rolls), reverse=True)
        rolls_to_omit = rolls_sorted[:keep] if keep > 0 else rolls_sorted[keep:]
        print(rolls_to_omit)

        for idx in range(0, len(self.rolls)):
          if self.rolls[idx].get_sumtotal() in rolls_to_omit:
            self.rolls[idx].omit = False

  def __str__(self) -> str:
    outputstr = ""
    for roll in self.rolls:
        outputstr += roll.get_string()
    return(outputstr)

  def override_sumtotal(self, newtotal):
    for idx, roll in enumerate(self.rolls):
      self.rolls[idx].sumtotal = newtotal
    pass

  def getroll(self, rollnumber=0):
    if len(self.rolls)>rollnumber:
      return self.rolls[rollnumber]
    else:
      return None

  def getrolls(self):
    return self.rolls
  
  def getrealrolls(self):
    '''returns only rolls that actually worked, where the total is not None'''
    pass
  
  def get_roll_count(self):
    return len(self.rolls)

  def omitted_rolls(self):
    # returns a list of the omitted rolls
    rolls = []
    for roll in self.rolls:
        if roll.is_omitted():
            rolls.append(roll)
    return rolls

  def not_omitted_rolls(self):
    # returns a list of the rolls there were not omitted
    rolls = []
    for roll in self.rolls:
        if roll.is_omitted() is False:
            rolls.append(roll)
    return rolls

  def highest_roll(self):
      return 0
  
  def highest_roll_string(self, showall=False):
      return 0

  def lowest_roll(self):
      return 0
  
  def lowest_roll_string(self, showall=False):
      return 0

  def __check_omitted__(self):
      '''
      this will need to check the omit state of a set of rolls, or figure out a way to check them all together?
      this is a private def
      '''
      pass

  def roll_the_dice(self, roll_arg, omit=False):
    '''parse the roll'''

    argument = roll_arg
    equation = None
    total = None
    stat = None
    comment = None

    if '#' in roll_arg:
      argument = roll_arg.split('#', 1)[0].strip() # takes off extra whitespace from split argument, cleans it up
      comment = roll_arg.split('#', 1)[1].strip()
  
    # a roll for a stat check, so a 1d100 against a stat or just a clean number
    if bool(re.match(r'^[0-9]+$', argument)) or bool(re.match(r'^1d100\s[0-9]+$', argument)):
      
      pattern_1d100 = r'(?<=1d100\s)([0-9]+)' # pattern to check for dice roll or number
      pattern_int = r'^[0-9]+$' # a pattern to check one single integer

      found = re.search(pattern_1d100, argument) if bool(re.search(pattern_1d100, argument)) else re.search(pattern_int, argument)

      stat = found.group(0)
      equation = self.generate_equation("1d100")
      total = self.calculate_total(equation)

    # this is meant to process everything else, but right now is mainly doing dice rolls. Or basic math.
    else:
      equation = self.generate_equation(argument)
      total = self.calculate_total(equation)

    # stores results in an object
    dr = RollResult(argument=roll_arg, equation=equation, sumtotal=total, stat=stat, comment=comment, omit=omit)
    return dr

  def generate_equation(self, rolls_arg):
    # this will take the roll string and replace the dice roll with a result
    diceroll_pattern = r'([0-9]+d[0-9]+)'
    dicerolls = re.findall(diceroll_pattern, rolls_arg.lower())
    results_string = rolls_arg # setting up the string that we'll be revising

    # check if the pattern is xDxxx for dicerolls
    if len(dicerolls) > 0:      
      for diceroll in dicerolls:
        amount, sides = diceroll.split('d')
        roll_results = self.perform_rolls(int(amount), int(sides))
        
        # formats the results of the roll into a string
        formatted_results = "(" + '+'.join(str(e) for e in roll_results) + ")"
        
        # replaces the current diceroll with it's results
        results_string = results_string.replace(diceroll, formatted_results, 1)
    
    return results_string

  def perform_rolls(self, amount, sides):
    
    if sides == 0 or amount == 0:
      return [0]
    else:
      secretsGenerator = secrets.SystemRandom()
      return [secretsGenerator.randint(1, sides) for roll in range(0, amount)]
      #return [random.randint(1, sides) for roll in range(0, amount)] #less secure

  def calculate_total(self, math_string):
    # this will take a string of numbers and math characters and produce a result. 
    # it will return None if there's any characters other than the legal ones.

    if self.is_arithmetic(math_string):
      return eval(math_string)
    else:
      return None

  def is_arithmetic(self, s):
    def _is_arithmetic(node):
        if isinstance(node, ast.Num):
            return True
        elif isinstance(node, ast.Expression):
            return _is_arithmetic(node.body)
        elif isinstance(node, ast.UnaryOp):
            valid_op = isinstance(node.op, UNARY_OPS)
            return valid_op and _is_arithmetic(node.operand)
        elif isinstance(node, ast.BinOp):
            valid_op = isinstance(node.op, BINARY_OPS)
            return valid_op and _is_arithmetic(node.left) and _is_arithmetic(node.right)
        else:
            raise ValueError('Unsupported type {}'.format(node))

    try:
        return _is_arithmetic(ast.parse(s, mode='eval'))
    except (SyntaxError, ValueError):
        return False

if __name__ == '__main__':
  test_strings = [ '4d100+45+(1d6-4)',
                  '1D100 45',
                  '45 # rolling for intelligence',
                  'i farted',
                  "45 + 45 + 23 (10-1) # hello#hello #hello #herloo!",
                  '1d6+3',
                  '50']
  

  for test_string in test_strings:
    print ("///////////////////////////////////////////////////////////////////")
    myrolls = DiceRolls(test_string, repeat=10, keep=-3)

    for dice in myrolls.getrolls():
      print (dice)

  myrolls = DiceRolls("50", repeat=5, keep=2)
  for dice in myrolls.getrolls():
      print (dice)
  myrolls = DiceRolls("50", repeat=5, keep=-2)
  for dice in myrolls.getrolls():
      print (dice)