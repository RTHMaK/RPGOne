
window.addEventListener('load', function() {
    
    var results = document.getElementById('results');
    
    function search() {
        console.log('Im searching!');
        results.innerHTML = '<div style="color:red;">hello</div> world<br/>new line<div class="person-row">some stuff</div>';
        console.log(results.innerHTML);
    }
    
    var searchBtn = document.getElementById('searchBtn');
    
    searchBtn.addEventListener('click', search);
});