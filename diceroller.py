import re, random, ast

UNARY_OPS = (ast.UAdd, ast.USub)
BINARY_OPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod)

class DiceResult:
  def __init__(self, argument=None, equation=None, sumtotal=None, stat=None, comment=None):
    '''this will eventually be an additional class that holds the results of rolls since there's a possible scenario for multi-rolling'''
    self.argument = argument
    self.equation = equation
    self.sumtotal = sumtotal
    self.stat = stat
    self.comment = comment

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


class DiceRolls:
  def __init__(self, rolls_arg):

    self.rolls = []
    rolls_arg = rolls_arg.lower() # normalize the argument
    
    self.process_roll_request(rolls_arg) # begin parsing user input

  def getroll(self, rollnumber=0):
    if len(self.rolls)>rollnumber:
      return self.rolls[rollnumber]
    else:
      return None

  def getrolls(self):
    return self.rolls

  def get_roll_count(self):
    return len(self.rolls)

  def process_roll_request(self, rolls_arg):
    # process the user input and see if its a command

    # if its a repeat command
    if "repeat(" in rolls_arg.lower(): # checks for 'repeat('
      print ("repeat command")
      pattern = r'repeat\((.+),\s*([0-9]+)\)' # pattern to check for correct formatting inside 'repeat()'
      found = re.search(pattern, rolls_arg)
      if found:
        for x in range (0, int(found.group(2))):
          equation = self.generate_results_string(found.group(1))
          total = self.calculate_total(equation)
          dr = DiceResult(argument=found.group(1), equation=equation, sumtotal=total, stat=None)
          self.rolls.append(dr)
      else:
        None

    elif bool(re.match(r'^[0-9]+$', rolls_arg)) or bool(re.match(r'^1d100\s[0-9]+$', rolls_arg)):
    # a roll for a stat check, so a 1d100 against a stat

      print ("dice roll against 1D100")
      
      pattern_1d100 = r'(?<=1d100\s)([0-9]+)' # pattern to check for dice roll or number
      pattern_int = r'^[0-9]+$' # a pattern to check one single integer

      found = re.search(pattern_1d100, rolls_arg) if bool(re.search(pattern_1d100, rolls_arg)) else re.search(pattern_int, rolls_arg)        

      stat = found.group(0)
      equation = self.generate_results_string("1d100")
      total = self.calculate_total(equation)
      
      dr = DiceResult(argument=rolls_arg, equation=equation, sumtotal=total, stat=stat)
      self.rolls.append(dr)

    else:
      # this is meant to process everything else, but right now is mainly doing dice rolls. Or basic math.
      print ("catch-all, standard dice roll")
      equation = self.generate_results_string(rolls_arg)
      total = self.calculate_total(equation)

      dr = DiceResult(argument=rolls_arg, equation=equation, sumtotal=total, stat=None)
      self.rolls.append(dr)


  def generate_results_string(self, rolls_arg):
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
  #test_string = '4d100+45+(1d6-4)'
  #test_string = 'repeat(2d100+6+3d8+(5-2),50)'
  #test_string = '1D100 45'
  #test_string = '45'
  #test_string = 'i farted'
  test_string = "45 + 45 + 23 (10-1)"
  myrolls = DiceRolls(test_string)
  dice = myrolls.getroll(0)

  results = "{}: {} = {} is {}".format("ctx.author.mention", dice.get_equation(), dice.get_sumtotal(), dice.get_success())
  print (results)
