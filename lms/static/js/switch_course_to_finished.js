// Switch courses to display
function switch_section() {

    let finished_courses_area = document.getElementById('finished-courses')
    let not_finished_courses_area = document.getElementById('not-last-courses')

    if (finished_courses_area.style.display === "none") {
        finished_courses_area.style.display = "flex";
        not_finished_courses_area.style.display = "none"
        button_targetted.style.borderBottom = '4px solid #368093'
        button_targetted_2.style.borderBottom = 'none'
    } else {
        finished_courses_area.style.display = "none";
        not_finished_courses_area.style.display = "flex"
        button_targetted.style.borderBottom = 'none'
        button_targetted_2.style.borderBottom = '4px solid #368093'
    }
}

let button_targetted = document.getElementById("finished-courses-button")
let button_targetted_2 = document.getElementById("not-last-courses-button")

button_targetted.onclick = function() {
    switch_section()
}
button_targetted_2.onclick = function() {
    switch_section()
}