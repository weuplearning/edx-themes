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
        if (currentLanguage === "en" ) {
            targetDiv.innerText = nlText;
        } else {
            targetDiv.innerText = frText;
        }
        
    }

    function forceUpdating() {
        // // dashboard
        // switchTrads("title-part-1", "Qu'est ce que", "Wat is"); 
        // switchTrads("title-part-2", "la E-Academy ?", "de E-Academy ?"); 
        // switchTrads("descript-part-1", "Un programme de formation gratuit qui guide pas à pas les entrepreneurs belges dans leur transition numérique.", "Een gratis opleidingsprogramma dat Belgische ondernemers stap voor stap begeleidt bij hun digitale transitie.");
        // switchTrads("descript-part-2", "Vous y trouverez des contenus variés pour compléter votre panoplie d’outils et booster votre entreprise. Chaque cours, d’une durée moyenne de 40 minutes, vous donne les clés concrètes pour créer ou développer efficacement votre activité. Vous serez également informé en temps réel de nos évènements à venir !", "Ontdek praktische tools en inspirerende content om je bedrijf een boost te geven. Elke cursus, met een gemiddelde duur van 40 minuten, geeft u concrete tips om uw bedrijf op te zetten of effectief te ontwikkelen en blijf in realtime op de hoogte van  komende evenementen!");

        // // webinar    
        // switchTrads("webi-descript-title", "Retrouvez ici les enregistrements de nos évènements en ligne.", "Hier vindt u de opnames van onze online evenementen.");

        // // header
        // switchTrads("nav-webinaire", "Webinaires BECOM", "BECOM-webinars"); 
        // switchTrads("nav-etudes", "Etudes", "Studies"); 
        // switchTrads("nav-actu", "Actualités", "Nieuws"); 

        // footer
        switchTrads("footer-link-cgu", "Conditions générales d'utilisation", "General conditions of use"); 

    }


    setTimeout(() => {
        forceUpdating()
    }, 200);





    // Update footer links
    // if (currentLanguage == "en"  ) {
    //     var link1 = document.getElementById("footer_link_1");
    //     var link2 = document.getElementById("footer_link_2");

    //     try {
    //         link1.href = "/nl/wettelijke-vermeldingen/";
    //         link2.href = "/nl/beleid-inzake-gegevensbescherming/";
    //     } catch (error) {
    //         console.log('footer links not found');
    //     }
    // }




});

