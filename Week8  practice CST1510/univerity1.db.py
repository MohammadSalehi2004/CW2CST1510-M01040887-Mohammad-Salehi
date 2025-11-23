import sqlite3

# creating our database, connect either finds an already existing database and if it doesnt exist then it creates one
dbconn = sqlite3.connect("university1.db")

# creating cursor obj
cur = dbconn.cursor()

# creating a table
cur.execute('''CREATE TABLE IF NOT EXISTS student (stdname TEXT PRIMARY KEY, program TEXT, mark INTEGER)''')

# Inserting DATA - A row into the table
cur.executemany("INSERT INTO student(stdname, program, mark) VALUES(?, ?, ?)", [("Mohammad", "IT", 70), ("Ali", "AI", 75)])

# changes to be saved by using "comit"
dbconn.commit()

# query the database
cur.execute("SELECT * FROM student")
print(cur.fetchall())

# closing the connection
dbconn.close()
