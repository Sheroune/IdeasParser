from os import listdir  # localisation translation
from os.path import isfile, join  # localisation translation
import pandas as pd  # Modifier translation
import re  # localisation translation

from PIL import Image # pip install Pillow


def convert_idea_images():
    # Read all names of image files
    loc_files_path = "source/ideas_EU4_images"
    image_names = [tr_f for tr_f in listdir(loc_files_path) if isfile(join(loc_files_path, tr_f))]
    for i in image_names:
        # Open an RLE compressed file
        im = Image.open(f"source/ideas_EU4_images/{i}")

        # Explicitly save uncompressed
        im.save(f'output/ideas_EU4_images_output/{i[:-4]}.png', compression=None)
    print(f"Converted {len(image_names)} idea icons.")


def convert_flag_images():
    # Read all names of image files
    loc_files_path = "source/eu4flags"
    image_names = [tr_f for tr_f in listdir(loc_files_path) if isfile(join(loc_files_path, tr_f))]
    for i in image_names:
        # Open an RLE compressed file
        im = Image.open(f"source/eu4flags/{i}")

        # Explicitly save uncompressed
        im.save(f'output/eu4flags_output/{i[:-4]}.png', compression=None)
    print(f"Converted {len(image_names)} flag icons.")


def create_translation_tuples():
    # Read all names of localisation files in loc_eng_files
    loc_files_path = "source/loc_eng_files"
    all_loc_files = [tr_f for tr_f in listdir(loc_files_path) if isfile(join(loc_files_path, tr_f))]
    # Make tuples with translation
    translation_tuples = []
    for loc_file in all_loc_files:
        with open(f"source/loc_eng_files/{loc_file}", "r", encoding='utf-8-sig') as tr_file:
            tr_lines = tr_file.readlines()
        for line in tr_lines:
            mnemonic = line[0:line.find(":")].strip()
            translation_mnemonic = line[line.find('"') + 1:-2:].strip()
            translation_tuples.append((mnemonic, translation_mnemonic))
    return translation_tuples


def parse_eu4Ideas(ideanames):
    df = pd.read_csv('Eu4Ideas/modifier_translation.txt', sep=";")
    translation = create_translation_tuples()
    all_output = "Name;Starter_Ideas;Ambition;Trigger;Idea1;Idea2;Idea3;Idea4;Idea5;Idea6;Idea7;Adjective;Country\n"
    for filename in ideanames:
        with open(f"Eu4Ideas/{filename}.txt", "r") as file:
            lines = file.readlines()
        storage = []
        for i in range(len(lines)):
            temp = lines[i]
            if "#" in temp:
                temp = temp[:temp.find('#'):]
            if "free = yes" in temp:
                temp = temp[:temp.find('free = yes'):]
            lines[i] = temp
        for i in range(len(lines)):
            if len(lines[i].strip()) != 0:
                storage.append(lines[i].rstrip())
        name = ""
        idea_temp = ""
        output = ""
        amount_of_ideas_in_file = 0

        for i in range(len(storage)):
            storage[i] = storage[i].replace("    ", "	")
            if storage[i].count("	") == 0:
                if name != "" and idea_temp != "":
                    # Name of the ideas in code
                    name = name[:name.find(" ="):].replace("Ideas", "ideas")
                    # Entire description - it's a bloody mess, and I don't remember the logic
                    idea_temp = idea_temp.replace("		", "&&&&")
                    idea_temp = idea_temp.replace("{&&&&", "{")
                    idea_temp = idea_temp.replace("	}", "}")
                    idea_temp = idea_temp.replace("}	", "};")
                    idea_temp = idea_temp.replace("	", "")
                    idea_temp = idea_temp.replace("&&&&", " && ")
                    idea_temp = idea_temp.replace("}", "")
                    idea_temp = idea_temp.replace("{", "")
                    idea_temp = idea_temp.replace("bonus = ", "")
                    idea_temp = idea_temp.replace("start = ", "")
                    idea_temp = idea_temp.replace("trigger = ", "")
                    idea_temp = idea_temp.replace("OR = ", "")
                    idea_temp = idea_temp.replace("AND = ", "")
                    # Extracting adjective
                    if len(name[:name.find('_ideas'):]) != 3:
                        idea_temp += f";{name[:name.find('_ideas'):].title()}"
                    elif "_ideas" in name:
                        idea_temp += f";{name[:name.find('_ideas'):]}_ADJ"
                    elif "_Ideas" in name:
                        idea_temp += f";{name[:name.find('_Ideas'):]}_ADJ"
                    # Country
                    idea_temp += f";{name[:name.find('_ideas'):]}"


                    # Translating names and tags and other - no modifiers in loc files for some reason
                    for MODIFIER in translation:
                        if MODIFIER[0] in idea_temp:
                            idea_temp = re.sub(r'\b' + MODIFIER[0] + r'\b', MODIFIER[1], idea_temp)
                    # Translating modifers
                    for MODIFIER in range(len(df.index)):
                        if str(df['MODIFIER'][MODIFIER]) in idea_temp:
                            old = str(df['MODIFIER'][MODIFIER])
                            new = f"{str(df['Emote'][MODIFIER])} {str(df['Translation'][MODIFIER])}"
                            idea_temp = re.sub(r'\b' + old + r'\b', new, idea_temp)

                    idea_temp = idea_temp.replace("  && ", "")
                    # idea_temp = idea_temp.replace("_", " ")

                    amount_of_ideas_in_file += 1
                    output += f"{name};{idea_temp}\n"
                    name = ""
                    idea_temp = ""
                name = storage[i]
            elif storage[i].count("	") > 0:
                idea_temp += storage[i]
        print(f'Idea entries in {filename}.txt: {amount_of_ideas_in_file}')
        with open(f'output/{filename}temp.csv', 'w', encoding="utf-8-sig") as f:
            f.write("Name;Starter_Ideas;Ambition;Trigger;Idea1;Idea2;Idea3;Idea4;Idea5;Idea6;Idea7;Adjective;Country\n")
            f.write(output)
            all_output += output
    with open(f'output/All_ideas.csv', 'w', encoding="utf-8-sig") as f:
        # f.write("Name;Starter_Ideas;Ambition;Trigger;Idea1;Idea2;Idea3;Idea4;Idea5;Idea6;Idea7;Adjective;Country\n")
        f.write(all_output)
        print(f"\nCreated file 'All_ideas.csv' with {len(all_output)} symbols.")


def create_modifier_translation():
    with open(f"source/temp_modifier_translation.txt", "r") as file:
        lines_modifier = file.readlines()
        lines_modifier.sort(key=len, reverse=True)

    with open(f"source/emotes.txt", "r") as file:
        lines_emotes = file.readlines()
        lines_emotes.sort(key=len, reverse=True)

    for emote in lines_emotes:
        temp = emote.replace("\n", "")
        temp = (temp[temp.find(":") + 1:])
        temp = temp[:temp.find(":")]
        for line in range(1, len(lines_modifier)):

            if temp in lines_modifier[line].lower() and not (
                    "<" in lines_modifier[line] or ">" in lines_modifier[line]):
                lines_modifier[line] = lines_modifier[line].replace("\n", "")
                lines_modifier[line] = f"{lines_modifier[line]}{emote}"

    one_string_to_output = ""
    for i in lines_modifier:
        one_string_to_output += i

    with open(f'output/HUH.csv', 'w', encoding="utf-8-sig") as f:
        f.write("MODIFIER;Translation;Emote\n")
        f.write(one_string_to_output)
