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

    function switchTrads(divId, frText, nlText) {
        const targetDiv = document.getElementById(divId);       
        if (!targetDiv) return; 
        if (currentLanguage === "nl-nl" ) {
            targetDiv.innerText = nlText;
        } else {
            targetDiv.innerText = frText;
        }
        
    }

    function forceUpdating() {
        // dashboard
        switchTrads("title-part-1", "Qu'est ce que", "Wat is"); 
        switchTrads("title-part-2", "la E-Academy ?", "de E-Academy ?"); 
        switchTrads("descript-part-1", "Un programme de formation gratuit qui guide pas à pas les entrepreneurs belges dans leur transition numérique.", "Een gratis opleidingsprogramma dat Belgische ondernemers stap voor stap begeleidt bij hun digitale transitie.");
        switchTrads("descript-part-2", "Vous y trouverez des contenus variés pour compléter votre panoplie d’outils et booster votre entreprise. Chaque cours, d’une durée moyenne de 40 minutes, vous donne les clés concrètes pour créer ou développer efficacement votre activité. Vous serez également informé en temps réel de nos évènements à venir !", "Ontdek praktische tools en inspirerende content om je bedrijf een boost te geven. Elke cursus, met een gemiddelde duur van 40 minuten, geeft u concrete tips om uw bedrijf op te zetten of effectief te ontwikkelen en blijf in realtime op de hoogte van  komende evenementen!");
        switchTrads("citation-part-1", '"Chez Becom, nous croyons que la connaissance est la clé de la croissance. C’est pourquoi nous soutenons des initiatives telles que l’Amazon e-Academy, qui élèvent le niveau du e-commerce belge. Nous mettons à disposition des contenus essentiels tels que des webinaires et des conseils de première ligne, afin que les boutiques en ligne et les commerçants numériques soient mieux armés dans leur parcours digital"', '"Bij Becom geloven we dat kennis de sleutel is tot groei. Daarom steunen we initiatieven zoals de Amazon e-Academy die de Belgische e-commerce naar een hoger niveau tilt. We stellen belangrijke basiscontent zoals webinars en eerstelijnsadvies vrij ter beschikking, zodat webshops en digitale handelaren sterker staan in hun digitale reis."')
        switchTrads("citation-part-2", "- Greet, Directrice générale de Becom", "- Greet, Managing Director Becom")

        // jobs
        switchTrads("wiki-button", "Vous souhaitez consulter d'autres études ? Devenez membre de Becom et accédez au wiki de Becom", "Wilt u andere studies raadplegen? Word lid van Becom en krijg toegang tot de Becom-wiki")

        // webinar    
        switchTrads("webi-descript-title", "Retrouvez ici les enregistrements de nos évènements en ligne.", "Hier vindt u de opnames van onze online evenementen.");

        // header
        switchTrads("nav-webinaire", "Webinaires BECOM", "BECOM-webinars"); 
        switchTrads("nav-etudes", "Etudes", "Studies"); 
        switchTrads("nav-actu", "Actualités", "Nieuws"); 

        // footer
        switchTrads("footer_link_1", "Mentions légales", "Algemene voorwaarden"); 
        switchTrads("footer_link_2", "Politique de confidentialité", "Privacybeleid"); 
    }


    setTimeout(() => {
        forceUpdating()
    }, 200);



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

        try {
            link1.href = "/nl/wettelijke-vermeldingen/";
            link2.href = "/nl/beleid-inzake-gegevensbescherming/";
        } catch (error) {
            console.log('footer links not found');
        }

        // Update jobs link
        var jobsLink = document.getElementById("wiki-button");
        try {
            jobsLink.href = "https://wiki.becom.digital/nl/";
        } catch (error) {
            console.log('jobs link not found');
        }
    }


    setTimeout(() => {

        try {
            var ongoingCourses = document.getElementById('not-last-courses')

            if (ongoingCourses.children.length == 0) {
                if (currentLanguage === "nl-nl") {
                    ongoingCourses.innerText = 'Deze lijst is momenteel leeg' 
                } else {
                    ongoingCourses.innerText = 'Cette liste est actuellement vide' 
                }
            }
        } catch (error) {
            console.log('no not-last-courses section');
        }

        try {
            var finishedCourses = document.getElementById('finished-courses')
            
            if (finishedCourses.children.length == 0) {
                if (currentLanguage === "nl-nl") {
                    finishedCourses.innerText = 'Deze lijst is momenteel leeg' 
                } else {
                    finishedCourses.innerText = 'Cette liste est actuellement vide' 
                }
            }
        } catch (error) {
            console.log('no finished-courses section');
        }

    }, 500);



    setTimeout(() => {
        var emptySection = document.getElementsByClassName('empty-dashboard-message')[0]
        if (emptySection) {
            emptySection.getElementsByClassName('btn')[0].href = '/dashboard/elearning'
        }
    }, 500);

});

