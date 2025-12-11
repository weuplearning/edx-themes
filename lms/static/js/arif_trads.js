
window.addEventListener("load", function () {

    // DEFINE CURRENT LANGUAGE
    function getCookie(name) {
        var value = "; " + document.cookie;
        var parts = value.split("; " + name + "=");
        if (parts.length > 1) {
            // Return the last occurrence of the cookie
            return parts[parts.length - 1].split(";")[0];
        }
        return undefined;
    }


    let currentLanguage
    try{
        currentLanguage = getCookie('openedx-language-preference');
    } catch{
        console.log("could not get openedx cookie")
    }
    if(currentLanguage === undefined){
        try{
            currentLanguage = getCookie('django_language');
        } catch{
            currentLanguage = "fr";
            console.log("could not get openedx cookie")
        }
    }


    function switchTrads(divId, frText, enText) {
        const targetDiv = document.getElementById(divId);       
        if (!targetDiv) return; 
        if (currentLanguage === "en" ) {
            targetDiv.innerText = enText;
        } else {
            targetDiv.innerText = frText;
        }
    }


    function forceUpdating() {
        // courses
        switchTrads("discovery-message", "LES COURS", "COURSES"); 
        switchTrads("enroll-to-course", "Accéder au cours", "Access the course"); 

        // Dashboard 
        switchTrads("see-more", "En savoir plus", "See more"); 

        // footer
        switchTrads("footer-link-cgu", "Conditions générales d'utilisation", "General conditions of use"); 
    }


    setTimeout(() => {
        forceUpdating()
    }, 200);

});

