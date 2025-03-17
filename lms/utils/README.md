# Utilitaires UMN

## Rapports de notes

* Rapports hebdomadaires adressés aux référents le lundi à 04h00 UTC et 04h10
	`/edx/app/edxapp/edx-themes/umn/lms/utils/grade_reports_referents/fondamentaux/script.py`
	`/edx/app/edxapp/edx-themes/umn/lms/utils/grade_reports_referents/ingenieur/script.py`

* Rapports journaliers globaux adressées aux administrateurs à 06:00 UTC
	`/edx/app/edxapp/edx-themes/umn/lms/utils/grade_reports_fondamentaux/`
	`/edx/app/edxapp/edx-themes/umn/lms/utils/grade_reports_ingenieur/`
## Gestion des champs custom référents :
`/edx/app/edxapp/edx-themes/umn/lms/utils/custom_referents_fields/update_referents.sh`
Lance les scripts suivants :

* `./custom_referents_fields/fetch_google_csv.py`
* `./custom_referents_fields/lint_csv.py`
si le linter ne détecte pas de problème, lance :
* `./custom_referents_fields/parse_csv.py`
et copie les fichiers dans wul_apps
 
