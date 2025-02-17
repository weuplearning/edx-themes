#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
PURPLE='\033[0;35m'

NC='\033[0m'

echo -e "${PURPLE}(1/4) Fetching latest csv from google sheets api...${NC}"
/edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/umn/lms/utils/custom_referents_fields/fetch_google_csv.py 
echo -e "${GREEN}[Done]${NC}"
echo ''

echo -e "${PURPLE}(2/4) Linting CSV for any errors...${NC}"
/edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/umn/lms/utils/custom_referents_fields/lint_csv.py
echo -e "${GREEN}[Done]${NC}"
echo ''


# Check if linter has produced log
if [[ ! -f "/edx/app/edxapp/edx-themes/umn/lms/utils/custom_referents_fields/csv/csv_linter.log" ]]; then
    echo "Error: File 'out.log' does not exist."
    exit 1  # Exit with an error code
fi

last_char=$(tail -c 1 /edx/app/edxapp/edx-themes/umn/lms/utils/custom_referents_fields/csv/csv_linter.log)

if [[ "$last_char" == "0" ]]; then
    echo -e "${PURPLE}(3/4) Parsing CSV into JSON Files...${NC}"

    /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/umn/lms/utils/custom_referents_fields/parse_csv.py

    echo -e "${GREEN}[Done]${NC}"
    echo ''

    echo -e "${PURPLE}(4/4) Copying Files to Form folder${NC}"

    cp -f /edx/app/edxapp/edx-themes/umn/lms/utils/custom_referents_fields/output/umn_formations_safe.json /edx/app/edxapp/edx-platform/lms/djangoapps/wul_apps/custom_fields_editor_umn/umn_formations_safe.json
    cp -f /edx/app/edxapp/edx-themes/umn/lms/utils/custom_referents_fields/output/umn_formations.json /edx/app/edxapp/edx-platform/lms/djangoapps/wul_apps/custom_fields_editor_umn/umn_formations.json
    cp -f /edx/app/edxapp/edx-themes/umn/lms/utils/custom_referents_fields/output/umn_schools.json /edx/app/edxapp/edx-platform/lms/djangoapps/wul_apps/custom_fields_editor_umn/umn_schools.json
    echo -e "${GREEN}[Done]${NC}"

else
    echo -e "${RED}Error ! Linter found some errors, see ./csv/csv_linter.log for more details${NC}"
echo ""
fi


# /edx/app/edxapp/edx-themes/umn/lms/utils/custom_referents_fields/update_referents.sh