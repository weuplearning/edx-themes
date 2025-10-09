// JS FILTER BAR
let filteredList = document.getElementById("filterItems");
let menuOpen = false;
let selectedCategories = [];

// function toggleMenu() {
//   filteredList.classList.toggle("filter-open");
//   menuOpen = !menuOpen;
//   const filterItems = document.getElementById('filterItems');
//   filterItems.style.display = menuOpen ? 'flex' : 'none';
// }

function handleCategoryChange(event) {
    const checkboxValue = event.target.value.toLowerCase();
    const isChecked = event.target.checked;
    const labelElement = event.target.parentElement;

    if (isChecked) {
        // Add category to the selected categories
        selectedCategories.push(checkboxValue);
        labelElement.classList.add("active");
    } else {
        // Remove category from the selected categories
        const index = selectedCategories.indexOf(checkboxValue);
        if (index > -1) {
            selectedCategories.splice(index, 1);
        }
        labelElement.classList.remove("active");
    }

    // Get all the courses
    // const courseList = document.getElementsByClassName("course-item-not-enrolled");
    let courseListEnrolled = document.getElementById('not-last-courses').getElementsByClassName("course-item");
    let courseListFinishedCourses = document.getElementById('finished-courses').getElementsByClassName("course-item");

    let courseList = [...courseListEnrolled, ...courseListFinishedCourses] 

    // If nothing is selected, show all the courses
    if (selectedCategories.length === 0) {
        for (const course of courseList) {
            course.classList.remove("course-item-hide");
        }
    } else {
        // Show or hide courses depending on whether their category is selected
        for (const course of courseList) {
            let courseTag = ''
            if (course.children[0].children[0]){
                courseTag = course.children[0].children[0].attributes[3].textContent.toLowerCase();
            }

            const isHidden = course.classList.contains("course-item-hide");

            // Check if the course tag is in the selected categories
            const shouldHide = !selectedCategories.includes(courseTag);

            if (shouldHide && !isHidden) {
                course.classList.add("course-item-hide");
            } else if (!shouldHide && isHidden) {
                course.classList.remove("course-item-hide");
            }
        }
    }
}
