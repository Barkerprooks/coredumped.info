document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('.copy-link-button');
    
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            buttons.forEach(button => button.innerHTML = 'copy link');
            navigator.clipboard.writeText(`https://coredumped.info/blog/${button.dataset.post}`);
            button.innerHTML = 'copied';
        });
    });
});