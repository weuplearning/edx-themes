import csv
import re
import config
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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


def is_valid_email(email):
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    IP_REGEX = re.compile(r'(?:[0-9]{1,3}\.){3}[0-9]{1,3}') 
    BAD_SPECIAL_CHARS_REGEX = re.compile(r'(\.{2,}|-{2,}|_{2,}|@{2,}|@-|-\.)')


    if bool(EMAIL_REGEX.search(email)) == False:
        return False

    if bool(IP_REGEX.search(email)) == True:
        return False
    
    if bool(BAD_SPECIAL_CHARS_REGEX.search(email)) == True:
        return False
    
    if email[-1] in ['.', '-','_']:
        return False

    return True


def validate_email_column(text):
    print('validating string : "' + text + '"')

def validate_csv(file_path):
    errors = []
    
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader, None)  # Skip header row if present
        
        for line_num, row in enumerate(reader, start=2):  # Start counting from 2 (after header)
            print('line ' + str(line_num) + ' '  + str(row) + ' len :' + str(len(row)))
            
            # skip scanning empty lines, needed for organizing + already handled by parser
            if row == ['', '', '', '', '', '', '']:
                print('skipped empty row')
                continue

            if len(row) < 7:
                errors.append(f"Ligne {line_num}: Nombre de colonnes invalide")
                continue
            
            # Validate column A (Region Code)
            if row[0] not in regions:
                errors.append(f"Ligne {line_num}: Région Invalide '{str(row[0])}'")
            
            # Validate column G (Emails)
            validate_email_column(row[6])
            if len(row[6]) > 0:
                emails = row[6].split(';')
                if any(not is_valid_email(email.strip()) for email in emails):
                    errors.append(f"Ligne {line_num}: Email référent invalide")
                if row[6].endswith(';'):
                    errors.append(f"Ligne {line_num}: Point-virgule superflu à la fin de la cellue du référent")
    
    return errors

def send_warn_emails(errors):
    
    error_str = ''
    for err in errors:
        error_str += err
        error_str += '<br/>'
    
    html = '''<html><head></head><body><p>Bonjour,<br/><br/>
    Une tentative de mise à jour des fichiers de gestion des référents a échouée
    <br/>Voici le résultat d'analyse automatisée :<br/>
    <hr>
    <pre><code>''' + error_str + '''</code></pre>
    <hr>
    <br/><br/>Bonne r&eacute;ception<br/>
    L'&eacute;quipe WeUp Learning
    </p></body></html>'''

    for email in config.linter_warn_emails:
        part2 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
        fromaddr = config.mailer_expeditor
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = email
        msg['Subject'] = "umn - Echec de mise à jour des référents"

        server = smtplib.SMTP(config.mailer_addr, 25)
        server.starttls()
        server.login(config.mailer_login, config.mailer_password)
        msg.attach(part2)
        text = msg.as_string()
        server.sendmail(fromaddr, email, text)
        server.quit()
        print('Email sent to '+str(email))
    


if __name__ == "__main__":
    file_path = config.csv_path  # Change this to your actual file path
    validation_errors = validate_csv(file_path)
    f = open(config.linter_log_path, 'w')
    if validation_errors:
        print("Validation Errors:")
        for error in validation_errors:
            print(error)
            f.write(str(error))
    
    
        if (config.linter_warn_email_enable == True):
            send_warn_emails(validation_errors)
    
    
    else:
        print("CSV file is valid!")
    f.write(str(len(validation_errors)))
    f.close()    




# /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/umn/lms/utils/custom_referents_fields/lint_csv.py