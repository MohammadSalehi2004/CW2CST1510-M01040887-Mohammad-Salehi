import sqlite3

#creating our database, connect either finds an already existing database and if it doesnt exist then it creates one
dbconn = sqlite3.connect("university.db")

#creating cursor obj
cur = dbconn.cursor()

#creating a table
cur.execute('''CREATE TABLE IF NOT EXISTS student (MISIS TEXT PRIMARY KEY,stdname TEXT,program TEXT,mark INTEGER)''')

#Inserting DATA - A row into the table
cur.executemany("INSERT INTO student(MISIS, stdname, program, mark) VALUES(?, ?, ?, ?)", [('M01040887', "Mohammad", "IT", 70), ('M84963456', "Ali", "AI", 75)])

#changes to be saved by using "comit"
dbconn.commit()

#query the database
cur.execute("SELECT * FROM student")

print(cur.fetchall())

dbconn.close()
