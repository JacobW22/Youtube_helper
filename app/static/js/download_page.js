$(document).ready(function(){
    // Fade In page
    $('.first-container').fadeIn(500).removeClass('d-none').addClass('d-flex');
    $('.second-container').fadeIn(1000).removeClass('d-none').addClass('d-flex');

    // Add slideDown animation to Bootstrap dropup when expanding.
    $('.dropup').on('show.bs.dropdown', function() {
    $(this).find('.dropdown-menu').first().stop(true, true).slideToggle(300);
});


    // Add slideUp animation to Bootstrap dropup when collapsing.
    $('.dropup').on('hide.bs.dropdown', function() {
    $(this).find('.dropdown-menu').hide();
});
});
