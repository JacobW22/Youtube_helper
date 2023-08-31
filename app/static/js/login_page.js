$(document).ready(function(){
        
    // Fade In page
    $('.main-container').fadeIn(500).removeClass('d-none').addClass('d-flex');

    $('.email').keyup(function(){
      $(this).val($(this).val().toLowerCase());
    });

});