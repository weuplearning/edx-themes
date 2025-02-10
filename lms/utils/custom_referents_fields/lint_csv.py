import csv
import re
import config
# Define valid regions
regions = [
    "Guadeloupe",
    "Martinique",
    "Guyane",
    "La Réunion",
    "Mayotte",
    "Île-de-France",
    "Centre-Val de Loire",
    "Bourgogne-Franche-Comté",
    "Normandie",
    "Hauts-de-France",
    "Grand Est",
    "Pays de la Loire",
    "Bretagne",
    "Nouvelle-Aquitaine",
    "Occitanie",
    "Auvergne-Rhône-Alpes",
    "Provence-Alpes-Côte d'Azur",
    "Corse"
]

# Email validation regex
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

def is_valid_email(email):
    return bool(EMAIL_REGEX.match(email))

def validate_csv(file_path):
    errors = []
    
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader, None)  # Skip header row if present
        
        for line_num, row in enumerate(reader, start=2):  # Start counting from 2 (after header)
            
            if len(row) == 7:
                continue
            if len(row) < 7:
                errors.append(f"Line {line_num}: Not enough columns")
                continue
            
            # Validate column A (Region Code)
            if row[0] not in regions:
                errors.append(f"Line {line_num}: Invalid region code '{row[0]}'")
            
            # Validate column G (Emails)
            if len(row[6]) > 0:
                emails = row[6].split(';')
                if any(not is_valid_email(email.strip()) for email in emails):
                    errors.append(f"Line {line_num}: Invalid email format in column G")
                if row[6].endswith(';'):
                    errors.append(f"Line {line_num}: Trailing semicolon in email column G")
    
    return errors

if __name__ == "__main__":
    file_path = config.csv_path  # Change this to your actual file path
    validation_errors = validate_csv(file_path)
    f = open(config.linter_log_path, 'w')
    if validation_errors:
        print("Validation Errors:")
        for error in validation_errors:
            print(error)
            f.write(str(error))
    else:
        print("CSV file is valid!")
    f.write(str(len(validation_errors)))
    f.close()    





# edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/umn/lms/utils/custom_referents_fields/lint_csv.py