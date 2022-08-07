import pandas as pd
import utility as ut
import sqlite3 as sl

# ut.convert_idea_images()
# ut.convert_flag_images()
ut.create_modifier_translation()

# Names and parser
ideanames = ["NationalIdeas", "GroupIdeas"]
ut.parse_eu4Ideas(ideanames)
con = sl.connect('Goose.db')
df = pd.read_csv('output/All_ideas.csv', sep=";")
df.to_sql('EU4IDEAS', con)



