import sqlite3, time
from datetime import datetime
import diceroller

def initialize_db():
    conn = sqlite3.connect('dicebot.db')
    c = conn.cursor()

    # Creates table if the tables don't exist.
    c.execute('''CREATE TABLE IF NOT EXISTS rolls
        (   _id INTEGER PRIMARY KEY,
            messagetime timestamp, 
            user text, 
            nick text, 
            argument text, 
            equation text, 
            result int,
            stat int,
            success text,
            comment text,
            guild text,
            channel text)''')

    # Creates table if the tables don't exist.
    c.execute('''CREATE TABLE IF NOT EXISTS licorice
        (   ranking int, 
            flavor text, 
            link text, 
            quote text)''')

    conn.commit()
    conn.close()

# adds the player roll to the database.  Repeated rolls are separate entries.
def add_roll(user=None, nick=None, argument=None, equation=None, result=None, stat=None, success=None, comment=None, guild=None, channel=None):
    conn = sqlite3.connect('dicebot.db')
    c = conn.cursor()

    sql = "INSERT INTO rolls (messagetime, user, nick, argument, equation, result, stat, success, comment, guild, channel) VALUES (?,?,?,?,?,?,?,?,?,?,?)"
    values = (time.time(), user, nick, argument, equation, result, stat, success, comment, guild, channel)
    c.execute(sql,values)
    conn.commit()
    conn.close()

def get_as_rolls(date_in_epoch=0, date_out_epoch=None, number_of_entries=1, requested_user=None, requested_guild=None, requested_channel=None):
    conn = sqlite3.connect('dicebot.db')
    c = conn.cursor()
    conn.commit()

    # i don't think this is doing anything. maybe just a backup?
    select_stmt = '''SELECT * FROM rolls ORDER BY messagetime DESC LIMIT (%s)''' % (number_of_entries,)

    date_out_epoch = time.time() if date_out_epoch is None else date_out_epoch
    if number_of_entries == -1:
        select_stmt = '''SELECT * from rolls WHERE messagetime BETWEEN (%s) and (%s) ORDER BY messagetime''' % (date_in_epoch, date_out_epoch)
    elif number_of_entries >= 0:
        select_stmt = '''SELECT * from rolls WHERE messagetime BETWEEN (%s) and (%s) ORDER BY messagetime DESC LIMIT (%s)''' % (date_in_epoch, date_out_epoch, number_of_entries)

    x = c.execute(select_stmt)
    records = x.fetchall()

    rolls = []
    for record in records:
        messagetime = record[1]
        user = record[2]
        nick = record[3]
        argument = record[4]
        equation = record[5]
        result = record[6]
        stat = record[7]
        success = record[8]
        comment = record[9]
        guild = record[10]
        channel = record[11]

        # checks if user/guild/channel is None or equal, and then allows it.  All entries need to match in order for it to save an entry
        if (requested_user is None or requested_user == user) and (requested_guild is None or guild == requested_guild) and (requested_channel is None or channel == requested_channel):
            print (user)
            roll = diceroller.DiceResult(argument=argument, equation=equation, sumtotal=result, stat=stat, comment=comment, timestamp=messagetime)
            rolls.append(roll)


    conn.close()
    return rolls

# Returns a list of entries base on date. Defaults to last entry. -1 is all entries.
def get_entries_as_string(date_in_epoch=0, date_out_epoch=None, number_of_entries=1):
    conn = sqlite3.connect('dicebot.db')
    c = conn.cursor()
    conn.commit()

    # i don't think this is doing anything. maybe just a backup?
    select_stmt = '''SELECT * FROM rolls ORDER BY messagetime DESC LIMIT (%s)''' % (number_of_entries,)

    date_out_epoch = time.time()
    if number_of_entries == -1:
        select_stmt = '''SELECT * from rolls WHERE messagetime BETWEEN (%s) and (%s) ORDER BY messagetime''' % (date_in_epoch, date_out_epoch)
    elif number_of_entries >= 0:
        select_stmt = '''SELECT * from rolls WHERE messagetime BETWEEN (%s) and (%s) ORDER BY messagetime DESC LIMIT (%s)''' % (date_in_epoch, date_out_epoch, number_of_entries)

    x = c.execute(select_stmt)
    records = x.fetchall()

    output = []
    for record in records:
        nick = record[3]
        equation = record[5]
        result = record[6]
        stat = record[7]
        success = record[8]
        comment = "" if record[9] is None else record[9]
        guild = record[10]
        channel = record[11]

        if success is not None:
            output.append("**{}:** {} {} {} (Stat={})".format(nick, result, success, comment, stat))
        else:
            output.append("**{}:** {} {}".format(nick, result, comment))

    conn.close()
    return output

# Generates a set of licorice flavors and adds them to the database.  This is meant to just be run once.
def create_licorice():
    conn = sqlite3.connect('dicebot.db')
    c = conn.cursor()

    sql = '''INSERT INTO licorice (ranking, flavor, link, quote) VALUES (?,?,?,?)'''
    entries = [
        ('1', 'Cherry', 'https://shop.sprouts.com/product/53779/bulk-foods-cherry-twists', ''),
        ('2', 'Blue Raspberry', 'https://www.instacart.com/sprouts/products/17857224-bulk-foods-blue-rapsberry-twists-1-lb', ''),
        ('3', 'Mixed Berry', 'https://www.instacart.com/store/items/item_768195161', ''),
        ('4', 'Tropical', 'https://www.instacart.com/sprouts/products/20167641-sprouts-organic-tropical-flavored-licorice-twists-16-oz', ''),
        ('5', 'Blood Orange', 'https://www.instacart.com/products/20167944-sprouts-organic-blood-orange-flavored-licorice-twists-16-oz', ''),
        ('6', 'Raspberry', 'https://www.instacart.com/products/17857226-bulk-foods-red-raspberry-twists-1-lb', ''),
        ('7', 'Green Apple', 'https://www.instacart.com/sprouts/products/17857222-bulk-foods-green-apple-twists-1-lb', ''),
        ('8', 'Watermelon', 'https://www.instacart.com/sprouts/products/20167802-sprouts-organic-watermelon-flavored-licorice-twists-16-oz', ''),
        ('9', 'Root Beer', 'https://www.instacart.com/sprouts/products/17857228-bulk-foods-rootbeer-twists-candy-1-lb', ''),
        ('10', 'Peach', 'https://www.instacart.com/sprouts/products/17857232-bulk-foods-peach-twists-1-lb', ''),
        ('11', 'Chocolate', 'https://shop.sprouts.com/product/55866/bulk-foods-chocolate-twists', ''),
        ('12', 'Red Licorice', 'https://shop.sprouts.com/product/55862/bulk-foods-east-coast-style-red-twists', ''),
        ('13', 'Black Licorice', 'https://www.instacart.com/sprouts/products/17857240-bulk-foods-jumbo-black-licorice-twists-1-lb', ''),
        ('14', 'Pina Colada', 'https://allcitycandy.com/products/kennys-juicy-pina-colada-licorice-twists-16-oz-package', 'it’s really bad, like the worst')
    ]

    for entry in entries:
        c.execute(sql,(entry))
        conn.commit()

    conn.close()

# Returns a random licorice flavor
def get_random_licorice():
    conn = sqlite3.connect('dicebot.db')
    c = conn.cursor()

    x = c.execute('''
    SELECT flavor, link FROM licorice
    ORDER BY random() 
    LIMIT 1;''')

    randomflavor = x.fetchall()[0]

    conn.close()
   
    return randomflavor

# This is what runs if you JUST run the database.py.  Its for testing or pre-loading data if needed.
if __name__ == '__main__':
    '''first load'''
    date_in = datetime(2020, 9, 10, 23, 55, 59).timestamp()
    date_out = datetime(2020, 8, 13, 23, 55, 59).timestamp()

    #add_roll("Russell6", "Russ6", "1d6+34-4", "(3)+34-4", 33, 45, None)

    #get_entries_as_string(date_in_epoch=date_in, date_out_epoch=date_out, number_of_entries=-1)
    #for record in get_entries_as_string(number_of_entries=10):
    #    print (record)

    #create_licorice()
    #licorice = get_random_licorice()
    #print (licorice)
    #add_roll("Russell", "Russ", "1d6+34-4", "(3)+34-4", 33, 45, None)

    #get_entries_as_string(field=, date_in=, date_out=, number_of_entries="1")
