window.addEventListener("load", function () {
    console.log("ADDED LISTENER")

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
    }
    catch{
        console.log("could not get openedx cookie")
    }
    if(currentLanguage===undefined){
        currentLanguage = getCookie('django_language');
    }

    function switchTrads(divId, frText, nlText) {
        console.log(divId)
        const targetDiv = document.getElementById(divId);       
        if (!targetDiv) return; 

        if (currentLanguage === "nl-nl" && targetDiv.innerText === frText) {
            targetDiv.innerText = nlText;
            
        } else if (targetDiv.innerText === nlText) {
            targetDiv.innerText = frText;
        }
        
    }

    // header
    setTimeout(() => {
    // Your code here
    console.log('Delayed code after full page load');
    switchTrads("nav-webinaire", "Webinaire BECOM", "BECOM-webinar"); 
    switchTrads("nav-etudes", "Etudes", "Studies"); 
    switchTrads("nav-actu", "Actualités", "Nieuws"); 
    }, 1000); // delay in milliseconds (1000 = 1 second)
    
    // dashboard
    switchTrads("title-part-1", "Qu'est ce que", "Wat is"); 
    switchTrads("title-part-2", "la E-Academy ?", "de E-Academy ?"); 
    switchTrads("descript-part-1", "Un programme de formation gratuit qui guide pas à pas les entrepreneurs belges dans leur transition numérique.", "Een gratis opleidingsprogramma dat Belgische ondernemers stap voor stap begeleidt bij hun digitale transitie.");
    switchTrads("descript-part-2", "Vous y trouverez des contenus variés pour compléter votre panoplie d’outils et booster votre entreprise. Vous serez également informé en temps réel de nos évènements à venir !", "Ontdek praktische tools en inspirerende content om je bedrijf een boost te geven, en blijf in realtime op de hoogte van  komende evenementen!");

    // webinar    
    switchTrads("webi-descript-title", "Retrouver ici les enregistrements de nos évènements en ligne.", "Hier vindt u de opnames van onze online evenementen.");
    
    // footer
    switchTrads("footer_link_1", "Mentions légales", "Algemene voorwaarden"); 



    function updateButtonText(sectionId, oldTextNL, newTextNL, oldTextFR, newTextFR) {
        const section = document.getElementById(sectionId);
        if (!section) return;
        const buttons = section.getElementsByClassName('course-target-link');

        for (let i = 0; i < buttons.length; i++) {
            if (currentLanguage === "nl-nl" && buttons[i].innerText === oldTextNL) {
                buttons[i].innerText = newTextNL;
            } else if (buttons[i].innerText === oldTextFR) {
                buttons[i].innerText = newTextFR;
            }
        }
    }

    // Update "Reprendre le cours" buttons
    updateButtonText("new-section", 'De cursus hervatten', 'Hervatten', 'Reprendre le cours', 'Reprendre');
    updateButtonText("not-last-courses", 'De cursus hervatten', 'Hervatten', 'Reprendre le cours', 'Reprendre');


    // Update footer links
    if (currentLanguage == "nl-nl"  ) {
        var link1 = document.getElementById("footer_link_1");
        var link2 = document.getElementById("footer_link_2");
        var link3 = document.getElementById("footer_link_3");
        var footerRight = document.getElementById("text-footer-right")

        if (footerRight) {
            footerRight.innerText = "Een programma op initiatief van"
        }

        // Change the href attributes
        try {
            link1.href = "/nl/wettelijke-vermeldingen/";
            link2.href = "/nl/beleid-inzake-gegevensbescherming/";
            link3.href = "/nl/faq-nl/";
        } catch (error) {
            console.log(error);
        }
    }

    
})


setTimeout(() => {

    try {
        var ongoingCourses = document.getElementById('not-last-courses')
        
        if (ongoingCourses.children.length == 0) {
            ongoingCourses.innerText = 'Cette liste est actuellement vide' 
        }
        if (currentLanguage === "nl-nl") {
            if (finishedCourses.children.length == 0) {
                finishedCourses.innerText = 'Deze lijst is momenteel leeg' 
            }
        }
        
    } catch (error) {
        console.log(error);
    }

    try {
        var finishedCourses = document.getElementById('finished-courses')
        if (finishedCourses.children.length == 0) {
            finishedCourses.innerText = 'Cette liste est actuellement vide' 
        }
        if (currentLanguage === "nl-nl") {
            if (finishedCourses.children.length == 0) {
                finishedCourses.innerText = 'Deze lijst is momenteel leeg' 
            }
        }

    } catch (error) {
        console.log(error);
    }

}, 1000);



setTimeout(() => {
    var emptySection = document.getElementsByClassName('empty-dashboard-message')[0]
    if (emptySection) {
        emptySection.getElementsByClassName('btn')[0].href = '/dashboard/elearning'
    }
}, 1000);

