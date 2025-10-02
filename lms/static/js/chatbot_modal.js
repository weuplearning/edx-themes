function afficherModaleCGU(e) {
    if (e) {
        e.preventDefault();
    }
    const overlay = document.createElement('div');
    overlay.id = 'modal-overlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.7);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    `;
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: relative;
        width: 90%;
        height: 90%;
        max-width: 1200px;
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        overflow: hidden;
    `;
    const btnFermer = document.createElement('button');
    btnFermer.innerHTML = '&times;';
    btnFermer.style.cssText = `
        position: absolute;
        top: 10px;
        right: 10px;
        background-color: #ff4444;
        color: white;
        border: none;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        font-size: 28px;
        cursor: pointer;
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        line-height: 1;
    `;
    btnFermer.onmouseover = () => btnFermer.style.backgroundColor = '#cc0000';
    btnFermer.onmouseout = () => btnFermer.style.backgroundColor = '#ff4444';
    const iframe = document.createElement('iframe');
    iframe.src = 'https://hec-chatbot.vercel.app/chat';
    iframe.style.cssText = `
        width: 100%;
        height: 100%;
        border: none;
    `;
    const fermerModale = () => {
        document.body.removeChild(overlay);
    };
    btnFermer.addEventListener('click', fermerModale);
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            fermerModale();
        }
    });
    modal.appendChild(btnFermer);
    modal.appendChild(iframe);
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
}
document.addEventListener('DOMContentLoaded', () => {
    const cguElement = document.getElementById('cgu');
    if (cguElement) {
        cguElement.addEventListener('click', afficherModaleCGU);
    }
});