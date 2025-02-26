document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('.copy-link-button');
    
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            buttons.forEach(button => button.innerHTML = 'Copy Link');
            navigator.clipboard.writeText(`https://coredumped.info/${button.dataset.post}`);
            button.innerHTML = 'copied';
        });
    });
});