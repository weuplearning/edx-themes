const CHATBOT_NAME = "Compagnon";
let isOpen = false;
let slideRatio = 1;
let slideInitialHeight = 1;
let slideInitialWidth = 1;
let slideHeightAvailable = window.innerHeight;
const isMenuOpen = () => {
    const hamburger = document.querySelector("#hamburger");
    return hamburger?.ariaExpanded === "true";
}
const createCompanionSideBar = () => {
    const section = document.createElement("section");
    section.id = "companion-side-bar";
    section.classList.add("cs-right");
    section.classList.add("area-secondary-wrapper");
    section.setAttribute("aria-label", "companion-side-bar");
    section.setAttribute("style", "position: absolute; top: 0px; overflow: visible; transform-origin: center center; display: block;");
    section.innerHTML =
    `
    <div class="view-content" tabindex="-1" style="position: relative; text-align: center; top: 0;" data-tabindex="-1">
        <div class="view-content__title"></div>
        <!--<iframe src="https://hec-chatbot-git-dev-lucas-auberts-
        projects.vercel.app">-->
        <iframe src="https://hec-chatbot.vercel.app/chat">
        <!--<iframe src="http://localhost:3000/chat">-->
        </iframe>
    </div> `;



    const frame = document.querySelector("#frame");
    if (frame) {
        frame.appendChild(section);
        const styleElement = document.createElement("style");
        styleElement.id = "companion-style";
        styleElement.innerHTML = "";
        document.body.appendChild(styleElement);
        const slide = document.querySelector('#slide');
        slideRatio = slide.offsetWidth / slide.offsetHeight;
        slideInitialWidth = slide.offsetWidth;
        slideInitialHeight = slide.offsetHeight;
        slide.classList.add("slide-companion");
        const topBar = document.querySelector("#top-bar");
        topBar.classList.add("top-bar-companion");

    }
}

const overlayClick = () => {
    companionClick();
    const overlay = document.querySelector(".sidebar-overlay");
    overlay.removeEventListener("click", overlayClick);
}

const getCentralWidth = () => {
    const companionSideBar = document.querySelector("#companion-side-bar");
    const sideBar = document.querySelector("#sidebar");

    const companionSideBarWidth = companionSideBar.offsetWidth;
    const sideBarWidth = sideBar.offsetWidth;
    let centralWidth = window.innerWidth;
    if (isOpen && window.innerWidth >= 900) {
        centralWidth -= companionSideBarWidth;
    }
    if (isMenuOpen() && window.innerWidth >= 900) {
        centralWidth -= sideBarWidth;
    }
    return centralWidth;
}


let updateStyle = () => {
    const companionSideBar = document.querySelector("#companion-side-bar");
    const topBar = document.querySelector("#top-bar");
    const bottomBar = document.querySelector("#bottom-bar");

    slideHeightAvailable = window.innerHeight - topBar.offsetHeight - bottomBar.offsetHeight - 20;
    if (companionSideBar) {
        if (bottomBar) {
            const centralWidth = getCentralWidth();
            if (window.innerWidth < 900 && isOpen) {
                if (!document.body.classList.contains('compagnon-open')) {
                    document.body.classList.add('compagnon-open');
                    const overlay = document.querySelector(".sidebar-overlay");
                    overlay.addEventListener("click", overlayClick);
                }
            } else if (window.innerWidth >= 900 || !isOpen) {
                if (document.body.classList.contains('compagnon-open')) {
                    document.body.classList.remove('compagnon-open');
                    const overlay = document.querySelector(".sidebar-overlay");
                    overlay.removeEventListener("click", overlayClick);
                }
            }
            const styleElement = document.querySelector("#companion-style");
            styleElement.innerHTML = "";

            const slide = document.querySelector('#slide');
            if (slide.offsetWidth) {
                slideRatio = slide.offsetWidth / slide.offsetHeight;
                slideInitialWidth = slide.offsetWidth;
                slideInitialHeight = slide.offsetHeight;
            }

            if (!isNaN(slideRatio)) {
                const sideBar = document.querySelector("#sidebar");
                let slideWidth = Math.min(slideHeightAvailable * slideRatio,centralWidth - 20);
                let scale = slideWidth / slideInitialWidth;
                slideWidth = slideInitialWidth;
                let slideHeight = slideInitialHeight;

                const styleElement = document.querySelector("#companion-style");
                styleElement.innerHTML =  `
                    .top-bar-companion {
                        width: ${centralWidth}px !important;
                    }

                    ${isOpen ? (
                        `.slide-companion {
                            width: ${slideWidth}px !important;
                            height: ${slideHeight}px !important;
                            transform: translate(${(isMenuOpen() ? sideBar.offsetWidth : 0) + (centralWidth - slideWidth * scale) / 2}px, ${(window.innerHeight - slideHeight * scale) / 2}px) scale(${scale}) !important;
                        }`
                    ) : ""}
                `;
            }
        }
    }
}


const resizeObserver = new ResizeObserver(updateStyle);

const hamburgerClick = () => {
    if (isMenuOpen() && isOpen) {
        if (window.innerWidth - 245 * 2 < 900) {
            isOpen = !isOpen;
            const companionSideBar = document.querySelector("#companion-side-bar");
            if (companionSideBar) {
                companionSideBar.classList.remove("open");
            }
        }
    }
    updateStyle();
    setTimeout(() => {
        updateStyle();
    }, 300);
}


const openCloseCompanion = () => {
    isOpen = !isOpen;
    const companionSideBar = document.querySelector("#companion-side-bar");
    if (companionSideBar) {
        if (isOpen) {
            companionSideBar.classList.add("open");
        } else {
            companionSideBar.classList.remove("open");
        }
    }
}
const companionClick = () => {
    openCloseCompanion();
    const hamburger = document.querySelector("#hamburger");

    if (hamburger) {
        const menuOpen = isMenuOpen();
        if (window.innerWidth - 245 * 2 < 900) {
            if (menuOpen) {
                hamburger.click();
            }
        }
    }
    updateStyle();
}


const resizePage = () => {
    if (getCentralWidth() < 655 && isOpen) {
        openCloseCompanion();
    }
    updateStyle();
}

const createChatbotEntry = () => {
    const timeinterval = setInterval(() => {
        const helpLink = document.querySelector("#link-right-0");
        if (helpLink) {
            clearInterval(timeinterval);
            const text = helpLink.querySelector(".top-tab-text");
            if (text) {
                text.innerHTML = "<svg class='help-button' xmlns=\"http://www.w3.org/2000/svg\" height=\"24px\" viewBox=\"0 -960 960960\" width=\"24px\" fill=\"currentColor\"><path d=\"M478-240q21 0 35.5-14.5T528-290q0-21-14.5-35.5T478-340q-21 0-35.5 14.5T428-290q0 21 14.535.5T478-240Zm-36-154h74q0-33 7.5-52t42.5-52q26-26 41-49.5t15-56.5q0-56-41-86t-97-30q-57 0-92.5 30T342-618l66 26q5-18 22.5-39t53.5-21q32 0 48 17.5t1638.5q0 20-12 37.5T506-526q-44 39-54 59t-10 73Zm38 314q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q830 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-12785.5T480-80Zm0-80q134 0 227-93t93-227q0-134-93-227t-227-93q-134 0-227 93t-93 227q0 134 93 227t227 93Zm0-320Z\"/></svg>";

                helpLink.classList.add("visible");
            }
            const span = document.createElement("span");
            span.innerText = "Aide";
            span.classList.add("help-button__tooltip");
            const linksParent = helpLink.parentNode;
            linksParent.appendChild(span);
            const companionButton = document.createElement("button");
            companionButton.classList.add("companion-button");
            companionButton.classList.add("cs-button");
            companionButton.classList.add("btn");
            companionButton.innerHTML = ` <span class="text">${CHATBOT_NAME}</span>`;

            linksParent.parentNode.appendChild(companionButton);
            companionButton.addEventListener("click", companionClick);
            createCompanionSideBar();
            const sideBar = document.querySelector("#sidebar");
            resizeObserver.observe(sideBar);
            updateStyle();
            window.addEventListener("resize", resizePage);
            const hamburger = document.querySelector("#hamburger");
            hamburger.addEventListener("click", hamburgerClick);
        }
    }, 100);

}

document.addEventListener('DOMContentLoaded', () => {
    createChatbotEntry();
})


