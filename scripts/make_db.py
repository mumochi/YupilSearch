# Creates a local SQLite database from transcript JSONs.
# A static flat file could be used instead, but downstream code would need to reflect this change.
import os
import json
import sqlite3

conn = sqlite3.connect("../vods.db")
c = conn.cursor()

c.execute("""CREATE TABLE vods(text,start,duration,videoId);""")

for filename in os.listdir("../transcripts"):
    openfile = f"../transcripts/{filename}"
    with open(openfile, 'r') as f:
        data = json.load(f)

    json_id = filename.replace("VOD_", "").replace(".json", "")

    for i in range(len(data)):
        text = data[i]['text']
        start = data[i]['start']
        duration = data[i]['duration']
        videoId = json_id
        c.execute("""INSERT INTO vods (text,start,duration,videoId) VALUES (?,?,?,?)""", (text,start,duration,videoId))

conn.commit()
conn.close()
print("Database created.")
