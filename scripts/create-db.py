#!/usr/bin/env python

import glob
import sqlite3
import traceback
import yaml

db = sqlite3.connect("pgus")

c = db.cursor()
c.execute('''
CREATE TABLE resolutions (
    id BIGSERIAL PRIMARY KEY,
    title TEXT,
    resolution_date DATE,
    action_date DATE,
    action TEXT,
    motion TEXT,
    resolution TEXT
);
''')

c.execute('''
CREATE TABLE votes (
    id BIGINT,
    name TEXT,
    vote INTEGER
);
''')

count = len(glob.glob("doc/*.yaml"))
i = 1
while i <= count:
    filename = "doc/r%d.yaml" % i
    file = open(filename, "r")
    resolution = yaml.safe_load(file)
    file.close()

    if not "motion" in resolution:
        print "%s missing motion" % filename
        resolution["motion"] = None

    try:
        c.execute("""
                INSERT INTO resolutions (id, title, resolution_date,
                                         action_date, action, motion,
                                         resolution)
                VALUES (?, ?, ?, ?, ?, ?, ?);""",
                (i, resolution["title"], resolution["resolution_date"],
                 resolution["action_date"], resolution["action"],
                 resolution["motion"], resolution["resolution"]))
    except:
        print "INSERT into resolutions failed:"
        print "  id:", i
        print "  title:", resolution["title"]
        print "  resolution_date:", resolution["resolution_date"]
        print "  action_date:", resolution["action_date"]
        print "  action:", resolution["action"]
        print "  resolution:", resolution["resolution"]
        print traceback.format_exc()
        exit(1)

    if not "vote_record" in resolution:
        print "%s missing vote_record" % filename
        i = i + 1
        continue

    for vote in resolution["vote_record"]:
        try:
            if not "vote" in vote:
                vote["vote"] = None

            c.execute("""
                    INSERT INTO votes (id, name, vote)
                    VALUES (?, ?, ?);""",
                    (i, vote["name"], vote["vote"]))
        except:
            print "INSERT into vote failed:"
            print "  id:", i
            print "  name:", vote["name"]
            print "  vote:", vote["vote"]
            print traceback.format_exc()
            exit(1)

    i = i + 1

db.commit()
db.close()
