# Call of Cthulhu Dicebot and Character Manager
A Call of Cthulhu dice bot.  It will also include a character sheet organizer linked directly to the dicebot in the future. Right now this is just for our private game.  It's meant to focus on Call of Cthulhu to keep the commands simpler. It also stores all rolls in a database that will hopefully get used later for some fun starts or calling up previous info.

It's also worth noting that some of the commands are stupid in-jokes meant specifically for our group. 

## Current Commands
Below is some of the functionality of this bot. Both *!r* and *.r* will work.

### Rolling Against Stats:
Returns what you rolled and how successful the roll was. In the example, 45 is the stat you're rolling against like INT or CON.

Example:

```
!r 1d100 45
!r 45
```

The dicebot will give you the results of the roll, how successful the roll was, and a color that makes it clear if it was a good or bad (green to red).  The roll can be a
critical, extreme success, hard success, success, lucky!, fail, or fumble.

Or group plays with a house rule that if you roll your exact stat, it's LUCKY! and you gain one luck point.

### Standard Rolls
Returns the results of your roll and completes the math.

Examples:
```
!r 1d6
!r 1d10+12
!r 2d4+1d6+5
```

### Comments
This just adds a little context to your roll.  This also gets stored in the database!

Examples:
```
!r 1d6 # int roll for my life
```

### Repeating Rolls
This will execute the roll as many times as in the second field. So 5 times in the above examples.  Unfortunately comments need to be inside the repeat command for now.

Examples:
```
!r repeat(1d6+4 #comment, 5)
!r repeat(45, 5)
```
## Roadmap

Import characters for quicker use with dicebot. 
Show last 5 rolls.
