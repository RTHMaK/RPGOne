
window.addEventListener('load', function() {
    
    function search() {
        console.log('Im searching!');
    }
    
    var searchBtn = document.getElementById('searchBtn');
    
    searchBtn.addEventListener('click', search);
});