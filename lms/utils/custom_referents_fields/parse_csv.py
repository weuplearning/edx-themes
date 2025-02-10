# -*- coding: utf-8 -*-

import csv
import hashlib
import json
import regions
import pprint
import config

# Function to generate a unique hash
def generate_hash(*args):
    return hashlib.sha256(''.join(args).encode()).hexdigest()

def debug_row(row):
    pprint.pp(row)

def generate_options(options_list):
    options = ""
    for item in options_list:
        item = item.replace("\n", "")
        options += f'{{\n"name": "{item}",\n"value": "{item}"\n}},\n'
    options = options.rstrip(",\n")  # Remove the trailing comma from the last element
    return options
    

def generate_custom_field(list_input,name="name",label="label",error_messages=""):
    options = generate_options(list_input)

    
    output_text = f'''
        {{
            "name": "{name}",
            "defaultValue": "",
            "errorMessages": "{error_messages}",
            "form": "register",
            "instructions": "",
            "label": "{label}",
            "restrictions": "",
            "required": false,
            "requiredStr": "",
            "type": "select",
            "options": [
                {options}
            ]
        }}
    '''
    return output_text

def remove_region_duplicates(data):
    result = {}
    for region, schools in data.items():
        seen = set()
        unique_schools = []
        for school in schools:
            if school not in seen:
                unique_schools.append(school)
                seen.add(school)
        result[region] = unique_schools
    return result

def remove_school_duplicates(data):
    result = {}
    for region, schools in data.items():
        seen = set()
        unique_schools = []
        for school in schools:
            if school not in seen:
                unique_schools.append(school)
                seen.add(school)
        result[region] = unique_schools
    return result

def remove_class_duplicates(data):
    unique_entries = set()
    cleaned_data = {}

    for key, value in data.items():
        unique_value = []
        for entry in value:
            entry_tuple = tuple(entry.items())  # Convert dictionary to a tuple of items
            if entry_tuple not in unique_entries:
                unique_entries.add(entry_tuple)
                unique_value.append(entry)
        cleaned_data[key] = unique_value
    
    return cleaned_data

def formation_data_factory(unsafe, formation, diplomalvl, school_class, schoolyear, referent):

    if formation == '':
        formation = 'N/A'
    if diplomalvl == '':
        diplomalvl = 'N/A'
    if school_class == '':
        school_class ='N/A'
    if schoolyear == '':
        schoolyear = 'N/A'
    if referent == '':
        referent = 'N/A'
    
    #print('\n┌─┤formation_data_factory├────────────┐')
    #print('│ formation :"' + formation + '"')
    #print('│ diplomalvl :"' + diplomalvl + '"')
    #print('│ school_class :"' + school_class + '"')
    #print('│ schoolyear :"' + schoolyear + '"')
    #print('│ referent :"' + referent + '"')
    #
    #print('└─────────────────────────────────────┘')
    
    
    output = {}
    output['title'] = formation
    output['class'] = school_class
    output['year'] = schoolyear
    output['diplomalvl'] = diplomalvl
    referent = referent.replace('\n', '')
    referent = referent.replace('\r', '')
    
    
    # referents = referent.split(";")
    if(unsafe == True):
        output['referents'] = referent
    
    return output

def remove_list_duplicates(list_object):
  return list(dict.fromkeys(list_object))

def validate_referent(ref):
    ''' catch badly formatted referents line 
        especially when using ';'
    '''
    if "'" in ref:
        return False
    if '"' in ref:
        return False
    if (len(ref) > 3) and (ref[-1] == ';'):
        return False
    

def parse_csv():
    csv_file = config.csv_path
    regions_collec = {}
    schools_collec = {}
    schools_collec_safe = {}
    schools_by_region = {}


    regions_list = []
    schools_list = []
    formation_list = []
    class_list = []
    year_list = []
    referent_list = []
    diplomalvl_list = []
    invalid_lines = []


    with open(csv_file, newline='', encoding='utf-8') as file:
        # !IMPORTANT : renommer les champs de header tel que suivant :
        # region, school, formation,diplomalevel, class, schoolyear, referent
        reader = csv.DictReader(file)
        
        for index,row in enumerate(reader):
            row_number = 2 + index  # Offset added because 0-indexed and header
            #print("----------------------------------------------------------------------------------")
            #print(index)
            #debug_row(row)
            # Lookup country code

            region = row.get('region', "N/A")
            school = row.get('school', "N/A")
            formation = row.get('formation', "N/A")
            school_class = row.get('class', "N/A")
            schoolyear = row.get('schoolyear', "N/A")
            referent = row.get('referent', "N/A")
            
            if(validate_referent(referent) == False):
                invalid_lines.append(row_number)
                print("ERROR")
                continue
            diplomalvl = row.get('diplomalevel',"N/A")

            # Append to list for future use 
            regions_list.append(region)
            schools_list.append(school)
            formation_list.append(formation)
            class_list.append(school_class)
            year_list.append(schoolyear)
            referent_list.append(referent)
            diplomalvl_list.append(diplomalvl)
            
            ## COLLEC 1 : SCHOOLS GROUPED BY REGIONS
            region_code = regions.lookup_region_code(region)
            
            if region not in regions_collec:
                regions_collec[region] = []
                
            regions_collec[region].append(school)
            schools_by_region = remove_region_duplicates(regions_collec)
            #print(schools_by_region)
            ## FOR EACH SCHOOL : ADD UNIQUE FORMATIONS
            if school not in schools_collec:
                schools_collec[school] = []
                schools_collec_safe[school] = []
            # parse formation object
            formation_data = formation_data_factory(unsafe=True, formation=formation, diplomalvl=diplomalvl, school_class=school_class, schoolyear=schoolyear, referent=referent)
            formation_data_safe = formation_data_factory(unsafe=False,formation=formation, diplomalvl=diplomalvl, school_class=school_class, schoolyear=schoolyear, referent=referent)
            schools_collec[school].append(formation_data)
            schools_collec_safe[school].append(formation_data_safe)
    cleaned_safe_schools = remove_class_duplicates(schools_collec_safe)
    cleaned_schools = remove_class_duplicates(schools_collec)

    # print(json.dumps(schools_collec, indent=4))


    with open( config.json_output_folder + "umn_formations.json", "w", encoding='utf-8') as f:
        f.write(json.dumps(schools_collec, indent=4,ensure_ascii=False))

    with open( config.json_output_folder + "umn_formations_safe.json", "w", encoding='utf-8') as f:
        f.write(json.dumps(schools_collec_safe, indent=4,ensure_ascii=False))

    with open( config.json_output_folder + "umn_schools.json", "w", encoding='utf-8') as f:
        f.write(json.dumps(schools_by_region, indent=4,ensure_ascii=False))




    # Write site config
    # remove duplicates
    regions_list = remove_list_duplicates(regions_list)
    schools_list = remove_list_duplicates(schools_list)
    formation_list = remove_list_duplicates(formation_list)
    class_list = remove_list_duplicates(class_list)
    year_list = remove_list_duplicates(year_list)
    diplomalvl_list = remove_list_duplicates(diplomalvl_list)
    referent_list  = remove_list_duplicates(referent_list)

    # create custom fields using generated list
    regions_custom_field = generate_custom_field(regions_list,name="schoolregion",label="région établissement")
    schools_custom_field = generate_custom_field(schools_list,name="school",label="établissement")
    formation_custom_field = generate_custom_field(formation_list,name="formation",label="Formation")
    class_custom_field = generate_custom_field(class_list,name="class",label="Classe")
    year_custom_field = generate_custom_field(year_list,name="year",label="Année")
    diplomalvl_field = generate_custom_field(diplomalvl_list,name="diplomalevel",label="Niveau de diplome")
    referent_custom_field = generate_custom_field(referent_list,name="referent",label="Référent")


    site_config_fields = f'''
    [
    {regions_custom_field.strip()},
    {schools_custom_field.strip()},
    {formation_custom_field.strip()},
    {class_custom_field.strip()},
    {year_custom_field.strip()},
    {diplomalvl_field.strip()},
    {referent_custom_field.strip()}
    ]
    '''
    
    print(invalid_lines)

    
    with open( config.json_output_folder + "site_config_fields.json", "w", encoding='utf-8') as f:
        f.write(site_config_fields)
parse_csv()


# /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/umn/lms/utils/custom_referents_fields/parse_csv.py