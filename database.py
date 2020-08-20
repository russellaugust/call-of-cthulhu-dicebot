import sqlite3, time

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
        comment text)''')

# Creates table if the tables don't exist.
c.execute('''CREATE TABLE IF NOT EXISTS licorice
    (   ranking int, 
        flavor text, 
        link text, 
        quote text)''') 

# adds the player roll to the database.  Repeated rolls are separate entries.
def add_roll(user=None, nick=None, argument=None, equation=None, result=None, stat=None, success=None, comment=None):
    sql = "INSERT INTO rolls (messagetime, user, nick, argument, equation, result, stat, success, comment) VALUES (?,?,?,?,?,?,?,?,?)"
    values = (time.time(), user, nick, argument, equation, result, stat, success, comment)
    c.execute(sql,values)
    conn.commit()

# Returns a list of entries base on date. Defaults to last entry.
def get_entry(field, date_in=None, date_out=None, number_of_entries="1"):
    '''if none and none, then return everything'''
    '''if none and date, then return everything from that date and before'''
    '''if date and none, then return everything from that date and after'''
    '''if date and date, then return everything between those two dates'''

    return None # this does not work yet.

# Generates a set of licorice flavors and adds them to the database.  This is meant to just be run once.
def create_licorice():
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

# Returns a random licorice flavor
def get_random_licorice():
    x = c.execute('''
    SELECT flavor, link FROM licorice
    ORDER BY random() 
    LIMIT 1;''')
    return x.fetchall()[0]

# Honestly, I don't know what or why this exists yet.
def close_db():
    conn.close()

# This is what runs if you JUST run the database.py.  Its for testing or pre-loading data if needed.
if __name__ == '__main__':
    '''first load'''
    #create_licorice()
    #licorice = get_random_licorice()
    #print (licorice)
    #add_roll("Russell", "Russ", "1d6+34-4", "(3)+34-4", 33, 45, None)

    #get_entry(field=, date_in=, date_out=, number_of_entries="1")
