document.addEventListener('DOMContentLoaded', function(){
    document.querySelector('#user-input').addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            document.querySelector('#value-enter').click();
        }
    });
});