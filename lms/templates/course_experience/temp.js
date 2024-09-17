console.clear()
console.log("begin")
var schoolData = ${ json.dumps(schools) | n};
var formationsData = ${ json.dumps(formations) | n};

if (document.getElementById('schoolregion').value === '') {
    document.getElementById('school').innerHTML = '';
    document.getElementById('formation').innerHTML = '';
    document.getElementById('class').innerHTML = '';
    document.getElementById('year').innerHTML = '';
}

console.log(schoolData)
console.log(formationsData)
function updateSchools() {
    let perfSchoolsBegin = performance.now();
    console.log("%cUpdate Schools", "color:green")
    var regionSelect = document.getElementById('schoolregion');
    var schoolSelect = document.getElementById('school');
    var selectedRegion = regionSelect.value;
    var formationSelect = document.getElementById('formation');

    // Clear current school options
    schoolSelect.innerHTML = '';
    schoolSelect.disabled = true;
    formationSelect.disabled = true;
    if (selectedRegion && schoolData[selectedRegion]) {
        var cur_schools = schoolData[selectedRegion];
        console.table(cur_schools)
        for (var i = 0; i < cur_schools.length; i++) {
            var option = document.createElement('option');
            option.value = cur_schools[i];
            option.text = cur_schools[i];
            schoolSelect.appendChild(option);
        }
        schoolSelect.disabled = false;
    }

    // Reset other fields
    //document.getElementById('formation').innerHTML = '<option value=""> </option>';
    //document.getElementById('class').innerHTML = '<option value=""> </option>';
    //document.getElementById('year').innerHTML = '<option value=""> </option>';
    document.getElementById('formation').innerHTML = '';
    document.getElementById('class').innerHTML = '';
    document.getElementById('year').innerHTML = '';
    document.getElementById('diplomalevel').innerHTML = '';

    updateFormations()
    evalOptionsAmount()
    let perfSchoolsTime = performance.now() - perfSchoolsBegin
    console.log("perfSchoolsTime", perfSchoolsTime)
    if (selectedRegion === '') {
        document.getElementById('formation').innerHTML = '';
        document.getElementById('class').innerHTML = '';
        document.getElementById('year').innerHTML = '';
    }

}

function updateDiplomalevel() {
    var diplomaLevel = document.getElementById('diplomalevel');

    console.log("%cUpdate Formations", "color: green")
    var schoolSelect = document.getElementById('school');
    var selectedSchool = schoolSelect.value;

    // Clear current diploma options
    formationSelect.innerHTML = '';
    document.getElementById('formation').innerHTML = '';
    document.getElementById('class').innerHTML = '';
    document.getElementById('year').innerHTML = '';

    if (selectedSchool && formationsData[selectedSchool]) {
        var formations = formationsData[selectedSchool];
        console.table(formations)
        var uniqueFormations = new Set();

        for (var i = 0; i < formations.length; i++) {
            var formation = formations[i];
            if (!uniqueFormations.has(formation.title)) {
                uniqueFormations.add(formation.title);
                var option = document.createElement('option');
                option.value = formation.title;
                option.text = formation.title;
                formationSelect.appendChild(option);
            }
        }
        formationSelect.disabled = false;
    }
    updateClasses()
    evalOptionsAmount()
}

function updateFormations() {
    var formationSelect = document.getElementById('formation');

    console.log("%cUpdate Formations", "color: green")
    var schoolSelect = document.getElementById('school');
    var selectedSchool = schoolSelect.value;

    // Clear current formation options
    formationSelect.innerHTML = '';
    document.getElementById('class').innerHTML = '';
    document.getElementById('year').innerHTML = '';

    if (selectedSchool && formationsData[selectedSchool]) {
        var formations = formationsData[selectedSchool];
        console.table(formations)
        var uniqueFormations = new Set();

        for (var i = 0; i < formations.length; i++) {
            var formation = formations[i];
            if (!uniqueFormations.has(formation.title)) {
                uniqueFormations.add(formation.title);
                var option = document.createElement('option');
                option.value = formation.title;
                option.text = formation.title;
                formationSelect.appendChild(option);
            }
        }
        formationSelect.disabled = false;
    }
    updateClasses()
    evalOptionsAmount()
}

function updateClasses() {
    console.log("%cUpdate Classes", "color: green")

    var formationSelect = document.getElementById('formation');
    var classSelect = document.getElementById('class');
    var yearSelect = document.getElementById('year');
    var selectedFormation = formationSelect.value;
    var schoolSelect = document.getElementById('school');
    var selectedSchool = schoolSelect.value;

    // Clear current class and year options
    classSelect.innerHTML = '';
    yearSelect.innerHTML = '';

    if (selectedFormation && selectedSchool && formationsData[selectedSchool]) {
        var formations = formationsData[selectedSchool];

        for (var i = 0; i < formations.length; i++) {
            var formation = formations[i];
            if (formation.title === selectedFormation) {
                if (formation.class && !Array.from(classSelect.options).some(o => o.value === formation.class)) {
                    var option = document.createElement('option');
                    option.value = formation.class;
                    option.text = formation.class;
                    classSelect.appendChild(option);
                    classSelect.disabled = false;
                }
                if (formation.year && !Array.from(yearSelect.options).some(o => o.value === formation.year)) {
                    var option = document.createElement('option');
                    option.value = formation.year;
                    option.text = formation.year;
                    yearSelect.appendChild(option);
                    yearSelect.disabled = false;

                }
            }
        }
    }
    evalOptionsAmount()
}