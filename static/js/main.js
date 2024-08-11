document.addEventListener('DOMContentLoaded', () => {
    
    document.body.classList.add('dark-mode');

    document.querySelector('button').onclick = () => {
        const printWindow = window.open('', 'PRINT', 'width=600,height=600');
        printWindow.document.write(document.querySelector('#resume-wrapper').innerHTML);
        printWindow.document.close();
        printWindow.focus();
        printWindow.print();
    };
});