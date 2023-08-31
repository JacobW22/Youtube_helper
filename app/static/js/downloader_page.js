$(document).ready(function(){
    var carousel_slides = document.getElementsByClassName("carousel-item");
    var carousel_indicators = document.getElementsByClassName("indicator");

    if (carousel_slides[0] != undefined && carousel_indicators[0] != undefined) {
    carousel_slides[0].classList.add("active");
    carousel_indicators[0].classList.add("active"); 
    }

    function submitFormWithValue(link) {

    var form = document.getElementById('main_form');

    var input_link = document.getElementById('input_link');

    input_link.value = link;

    form.submit();
    }
});
