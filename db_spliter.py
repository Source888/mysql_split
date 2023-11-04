# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 02:34:12 2023

@author: Source888
"""
import re
import os
import datetime

input_file = "all_db_dump_autocommit.sql"


output_directory = "py_splited"


max_file_size = 50* 1024 * 1024




os.makedirs(output_directory, exist_ok=True)


current_part = []
current_part_size = 0
part_number = 1
current_database = None
insert_table = None
insert_found = False
last_line = False 
insert_finished = False

start_new_file = True


with open(input_file, "r", encoding="utf-8") as dump_file:
    for line in dump_file:
        
        if line.startswith("CREATE DATABASE") and current_database is None:
           
            current_database = line.split()[2].strip("`;\n")
        
        if line.startswith("INSERT INTO"):
         
            insert_found = True
            insert_table = line
            if line.endswith('VALUES'):
                insert_finished = True
            else:
                insert_finished = False 
        if line.endswith('VALUES') and not insert_finished:
            insert_table = insert_table + line
        if start_new_file and last_line and not (current_database is None):
           current_part.insert(0, f"USE `{current_database}`;\n")
        if start_new_file and last_line:
           current_part.insert(1, f"{insert_table}\n")
           start_new_file = False
           last_line = False
        current_part.append(line)
        current_part_size += len(line.encode("utf-8")) 
        
        if current_part_size > max_file_size:
            last_line = line.strip().endswith("),")
            
            part_filename = os.path.join(output_directory, f"part_{part_number}.sql")
            now = datetime.datetime.now()
            
            with open(part_filename, "w", encoding="utf-8") as part_file:
                part_file.writelines(current_part)
                print(f"End part: {part_number}; Time {now}")

            
            part_number += 1
            current_part = []
            current_part_size = 0
            current_database = None
            insert_found = False
            start_new_file = True

        

   

print(f"Дамп таблицы разбит на части {max_file_size/(1024*1024*1024)} GB")