
  // ---------------- map show / hide ----------------------
window.addEventListener('load', function() {

const registerButton = document.querySelector(".register-btn-main")
console.log("registerButton : " + registerButton )
const registerButtonHeader = document.querySelector(".register-btn-header")
const map = document.querySelector(".mapSection")
const home = document.querySelector('.home')
const header = document.querySelector('.global-header')
const closeButton = document.querySelector('.mapSection-closeButton')

registerButton.addEventListener('click', ()=>{
    console.log('ciblage-ok')

    home.style.filter = "blur(0.5rem)"
    header.style.filter = "blur(0.5rem)"
    console.log('filter-ok')

    map.classList.toggle('mapSection-show')
    console.log('map-showing-ok')
})

registerButtonHeader.addEventListener('click', ()=>{
    console.log('ciblage-ok')

    home.style.filter = "blur(0.5rem)"
    header.style.filter = "blur(0.5rem)"
    console.log('filter-ok')

    map.classList.toggle('mapSection-show')
    console.log('map-showing-ok')
})

closeButton.addEventListener('click', ()=>{
  console.log('ciblage-2-ok')

  home.style.filter = "blur(0rem)"
  header.style.filter = "blur(0rem)"
  console.log('blur-off')

  map.classList.toggle('mapSection-show')
  console.log('map-hidden')
})

const loginButton1 = document.querySelector(".login-btn-main")
const loginButton2 = document.querySelector(".sign-in-btn-header")
loginButton1.addEventListener('click', ()=>{
  window.location = "/login"
})
loginButton2.addEventListener('click', ()=>{
  window.location = "/login"
})

  // ------------------- map functions ----------------------

  const regions = document.querySelectorAll('.mapSection-regions')
  const button = document.querySelector('.mapSection-buttonLink')

  regions.forEach((item)=>{
    item.addEventListener('click', (e)=>{
      console.log(e)
      console.log(e.target.id)
      switch(e.target.id){
        case "region-1":
          button.href = "/register?course_id=course-v1:icope+Occitanie+2022&enrollment_action=enroll"
          break
        case "region-2":
          button.href = "https://www.google.fr/"
          break
        case "region-3":
          button.href = ""
          break
        default:
          null
      }
    })
  })



function restart_color_button(){
      const all_region_button = document.getElementsByClassName("mapSection-map-region-texts")
      for (region of all_region_button){
        region.style.color = "#fff"
      }
      const all_region_domtom_button = document.getElementsByClassName("mapSection-map-domTom-description")
      for (region of all_region_domtom_button){
        region.style.color = "#000"
      }
      
    }

function selectRegion(region) {

  const redirect_to_occitanie = ['Autre', 'Guadeloupe', 'Martinique', 'Guyane', 'Mayotte', 'Reunion', 'world']

  const button = document.querySelector('.mapSection-buttonLink')
  const buttonDiv = document.querySelector('.mapSection-button')
  
  const selectedText = document.getElementById(region)
  restart_color_button()
  selectedText.style.color = "#F2816F"

  buttonDiv.style.background =  "#F2816F"
  if (redirect_to_occitanie.includes(region)) {
    region = 'Occitanie'
  }
  button.href = "/register?course_id=course-v1%3Aicope%2B" + region + "%2B2022&enrollment_action=enroll"
  }

  console.log('All assets are loaded')
})