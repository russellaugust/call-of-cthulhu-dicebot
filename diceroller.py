import re, random, ast, time, datetime

UNARY_OPS = (ast.UAdd, ast.USub)
BINARY_OPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod)

class DiceResult:
  def __init__(self, argument=None, equation=None, sumtotal=None, stat=None, comment=None, timestamp=None):
    '''this will eventually be an additional class that holds the results of rolls since there's a possible scenario for multi-rolling'''
    self.argument = argument
    self.equation = equation
    self.sumtotal = sumtotal
    self.stat = stat
    self.comment = comment
    self.timestamp = timestamp

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
      return None

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
    result = 0xed0909
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
  


class DiceRolls:
  def __init__(self, rolls_arg):

    self.rolls = []
    rolls_arg = rolls_arg.lower() # normalize the argument
    
    self.process_roll_command(rolls_arg) # begin parsing user input

  def getroll(self, rollnumber=0):
    if len(self.rolls)>rollnumber:
      return self.rolls[rollnumber]
    else:
      return None

  def getrolls(self):
    return self.rolls

  def get_roll_count(self):
    return len(self.rolls)

  def generate_roll(self, roll_arg):
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

    dr = DiceResult(argument=roll_arg, equation=equation, sumtotal=total, stat=stat, comment=comment)
    return dr

  def process_roll_command(self, rolls_arg):
    # process the user input and see if its a command

    # if its a repeat command
    if "repeat(" in rolls_arg.lower(): # checks if 'repeat('
      pattern = r'repeat\((.+),\s*([0-9]+)\)' # pattern to check for correct formatting inside 'repeat()'
      found = re.search(pattern, rolls_arg)
      if found:
        for x in range (0, int(found.group(2))):
          self.rolls.append(self.generate_roll(found.group(1)))
      else:
        None

    else:
      self.rolls.append(self.generate_roll(rolls_arg))

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
      return [random.randint(1, sides) for roll in range(0, amount)]

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
                  'repeat(1D100 45,10)',
                  '1D100 45',
                  '50',
                  '45 # rolling for intelligence',
                  'i farted',
                  "45 + 45 + 23 (10-1) # hello#hello #hello #herloo!"]
  

  for test_string in test_strings:
    print ("///////////////////////////////////////////////////////////////////")
    myrolls = DiceRolls(test_string)

    for dice in myrolls.getrolls():
      results = "{}: {} = {} is a {} // comment={}".format(dice.get_argument(), dice.get_equation(), dice.get_sumtotal(), dice.get_success(), dice.get_comment())
      print (results)
