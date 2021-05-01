import sqlite3, time, psycopg2
from datetime import datetime
import diceroller
import credentials as cred

class Database:
    # This will let you use the Database class either normally like db = Database('db_file.sqlite) or in a with statement:
    def __init__(self, name):
        if name.split('.')[-1].lower() == "db":
            print("this will connect to a local database...")
            self._conn = sqlite3.connect(name)
            self._cursor = self._conn.cursor()
        else:
            print("this will connect to a remote database server...")
            self._conn = psycopg2.connect(database=cred.database, user=cred.user, password=cred.password, host=cred.host, port=cred.port)
            #self._conn = sqlite3.connect(name)
            self._cursor = self._conn.cursor()


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def connection(self):
        return self._conn

    @property
    def cursor(self):
        return self._cursor

    def commit(self):
        self.connection.commit()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.fetchall()

    def convert_to_roll(self, roll_records):
        # this converts the contents of the db into a roll for reuse
        rolls = []
        for record in roll_records:
            messagetime = record[1]
            user = record[2]
            nick = record[3]
            argument = record[4]
            equation = record[5]
            result = record[6]
            stat = record[7]
            success = record[8]
            comment = record[9]
            channel = record[10]
            guild = record[11]

            # stores roll as class RollResult
            roll = diceroller.DiceResult(argument=argument, equation=equation, sumtotal=result, stat=stat, comment=comment, timestamp=messagetime, user=user, nick=nick, channel=channel, guild=guild)
            rolls.append(roll)
        return rolls

    def add_roll(self, user=None, nick=None, argument=None, equation=None, result_int=None, stat_int=None, success=None, comment=None, guild=None, channel=None):
        sql = "INSERT INTO rolls (messagetime, username, nick, argument, equation, result, stat, success, comment, guild, channel) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        values = (datetime.now(), user, nick, argument, equation, result_int, stat_int, success, comment, guild, channel)
        self.execute(sql,values)
        self.commit()

    def get_as_rolls(self, date_in_epoch=0, date_out_epoch=None, number_of_entries=1, requested_user=None, requested_guild=None, requested_channel=None):
        select_stmt =   '''SELECT * from rolls WHERE messagetime BETWEEN %s and %s AND username = CASE WHEN '%s' IS 'None' THEN username ELSE '%s' END AND channel = CASE WHEN '%s' IS 'None' THEN channel ELSE '%s' END AND guild = CASE WHEN '%s' IS 'None' THEN guild ELSE '%s' END ORDER BY messagetime DESC
                            ''' % (date_in_epoch, date_out_epoch, requested_user, requested_user, requested_channel, requested_channel, requested_guild, requested_guild)
        # sets the date_out time to right now if nothing is inputted, otherwise it uses what it gets
        date_out_epoch = time.time() if date_out_epoch is None else date_out_epoch

        if number_of_entries >= 0:
            # this sql will fine tune the results based on the requested user, channel and guild.  if none is given, it gets all
            select_stmt =   '''SELECT * from rolls WHERE messagetime BETWEEN %s and %s AND username = CASE WHEN '%s' IS 'None' THEN username ELSE '%s' END AND channel = CASE WHEN '%s' IS 'None' THEN channel ELSE '%s' END AND guild = CASE WHEN '%s' IS 'None' THEN guild ELSE '%s' END ORDER BY messagetime DESC LIMIT %s
                            ''' % (date_in_epoch, date_out_epoch, requested_user, requested_user, requested_channel, requested_channel, requested_guild, requested_guild, number_of_entries)
        
        records = self.query(select_stmt)
        rolls = self.convert_to_roll(records)
        return rolls

    # Returns a list of entries base on date. Defaults to last entry. -1 is all entries.
    def get_entries_as_string(self, date_in_epoch=0, date_out_epoch=None, number_of_entries=1, requested_user=None, requested_guild=None, requested_channel=None):
        
        rolls = self.get_as_rolls(date_in_epoch=date_in_epoch, date_out_epoch=date_out_epoch, number_of_entries=number_of_entries, requested_user=requested_user, requested_guild=requested_guild, requested_channel=requested_channel)

        output = []
        for roll in rolls:
            comment = "" if roll.get_comment() is None else roll.get_comment()

            if roll.get_success() is not None:
                output.append("**{}:** {} {} {} (Stat={})".format(roll.get_nick(), roll.get_sumtotal(), roll.get_success(), comment, roll.get_stat()))
            else:
                output.append("**{}:** {} {}".format(roll.get_nick(), roll.get_sumtotal(), comment))

        return output        

if __name__ == '__main__':

    #db = Database('dicebot.db')
    db = Database('postgres')

    result = diceroller.DiceRolls("45")
    print(result)

    '''
    date_in = datetime(2020, 10, 6, 23, 55, 59).timestamp()
    date_out = datetime(2020, 10, 9, 23, 55, 59).timestamp()
    rolls = db.get_as_rolls(date_in, date_out, 3, requested_guild="Not Art", requested_user="Beckyrocks#9891")
    strings = db.get_entries_as_string(date_in, date_out, -1, requested_guild="Not Art", requested_user="Beckyrocks#9891")
    '''

    '''
    for string in strings:
        print (string)
    # for roll in rolls:
    #     print (roll.get_timestamp_pretty() + ": " + roll.get_user() + " // " + roll.get_argument() + " // " + roll.get_guild())
    '''
