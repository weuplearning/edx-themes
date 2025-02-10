#!/bin/bash
echo "fetching latest csv from google sheets api"
/edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/umn/lms/utils/custom_referents_fields/fetch_google_csv.py 
echo "[Done]"

echo "Linting CSV for any errors"
/edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/umn/lms/utils/custom_referents_fields/lint_csv.py



# Check if linter has produced log
if [[ ! -f "/edx/app/edxapp/edx-themes/umn/lms/utils/custom_referents_fields/csv/csv_linter.log" ]]; then
    echo "Error: File 'out.log' does not exist."
    exit 1  # Exit with an error code
fi

last_char=$(tail -c 1 /edx/app/edxapp/edx-themes/umn/lms/utils/custom_referents_fields/csv/csv_linter.log)

if [[ "$last_char" == "0" ]]; then
    echo "Parsing CSV into JSON Files..."
    /edx/app/edxapp/venvs/edxapp/bin/python /edx/app/edxapp/edx-themes/umn/lms/utils/custom_referents_fields/parse_csv.py
    echo "[Done]"
    echo "Copying Files to Form folder"

    cp -f /edx/app/edxapp/edx-themes/umn/lms/utils/custom_referents_fields/output/umn_formations_safe.json /edx/app/edxapp/edx-platform/lms/djangoapps/wul_apps/custom_fields_editor_umn/umn_formations_safe.json
    cp -f /edx/app/edxapp/edx-themes/umn/lms/utils/custom_referents_fields/output/umn_formations.json /edx/app/edxapp/edx-platform/lms/djangoapps/wul_apps/custom_fields_editor_umn/umn_formations.json
    cp -f /edx/app/edxapp/edx-themes/umn/lms/utils/custom_referents_fields/output/umn_schools.json /edx/app/edxapp/edx-platform/lms/djangoapps/wul_apps/custom_fields_editor_umn/umn_schools.json
    echo "[Done]"

fi





