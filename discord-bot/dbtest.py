import psycopg2

#conn = psycopg2.connect(database="postgres", user="postgres", password="password", host="192.168.1.33", port="5432")
conn = psycopg2.connect(database="postgres", user="randerson", password="blacklotus", host="192.168.1.33", port="5432")
cursor = conn.cursor()

sql = '''   INSERT INTO persons (lastname,firstname)
            VALUES (%s,%s)'''
values = ("Sasha", "Huff")
cursor.execute(sql,values)

cursor.execute('SELECT * from persons')
#row = cursor.fetchone()
rows = cursor.fetchall()
conn.commit()
conn.close()

print(rows)