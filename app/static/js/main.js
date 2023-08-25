// Changing hamburger icon when clicked
$(".navbar-toggler-icon").css("background-image", "url(\"data:image/svg+xml,%3Csvg style='color: white' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' width='40' zoomAndPan='magnify' viewBox='0 0 30 30.000001' height='40' preserveAspectRatio='xMidYMid meet' version='1.0'%3E%3Cdefs%3E%3CclipPath id='id1'%3E%3Cpath d='M 3.386719 7.164062 L 26.613281 7.164062 L 26.613281 22.40625 L 3.386719 22.40625 Z M 3.386719 7.164062 ' clip-rule='nonzero' fill='white'%3E%3C/path%3E%3C/clipPath%3E%3C/defs%3E%3Cg clip-path='url(%23id1)'%3E%3Cpath fill='white' d='M 3.398438 22.40625 L 26.601562 22.40625 L 26.601562 19.867188 L 3.398438 19.867188 Z M 3.398438 16.054688 L 26.601562 16.054688 L 26.601562 13.515625 L 3.398438 13.515625 Z M 3.398438 7.164062 L 3.398438 9.703125 L 26.601562 9.703125 L 26.601562 7.164062 Z M 3.398438 7.164062 ' fill-opacity='1' fill-rule='nonzero'%3E%3C/path%3E%3C/g%3E%3C/svg%3E\")");

$(".navbar-toggler").click(function() {
    var icon = $(this).children("span");
    var value = $(this).attr('aria-expanded');

if (value == 'true') {
    $(".navbar").css("background","black");
    icon.css("background-image", "url(\"data:image/svg+xml,%3Csvg style='color: white' xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' class='bi bi-chevron-compact-down' viewBox='0 0 16 16'%3E%3Cpath fill-rule='evenodd' d='M1.553 6.776a.5.5 0 0 1 .67-.223L8 9.44l5.776-2.888a.5.5 0 1 1 .448.894l-6 3a.5.5 0 0 1-.448 0l-6-3a.5.5 0 0 1-.223-.67z' fill='white'%3E%3C/path%3E%3C/svg%3E\")")
}
else {
    $(".navbar").css("background","transparent");
    icon.css("background-image", "url(\"data:image/svg+xml,%3Csvg style='color: white' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' width='40' zoomAndPan='magnify' viewBox='0 0 30 30.000001' height='40' preserveAspectRatio='xMidYMid meet' version='1.0'%3E%3Cdefs%3E%3CclipPath id='id1'%3E%3Cpath d='M 3.386719 7.164062 L 26.613281 7.164062 L 26.613281 22.40625 L 3.386719 22.40625 Z M 3.386719 7.164062 ' clip-rule='nonzero' fill='white'%3E%3C/path%3E%3C/clipPath%3E%3C/defs%3E%3Cg clip-path='url(%23id1)'%3E%3Cpath fill='white' d='M 3.398438 22.40625 L 26.601562 22.40625 L 26.601562 19.867188 L 3.398438 19.867188 Z M 3.398438 16.054688 L 26.601562 16.054688 L 26.601562 13.515625 L 3.398438 13.515625 Z M 3.398438 7.164062 L 3.398438 9.703125 L 26.601562 9.703125 L 26.601562 7.164062 Z M 3.398438 7.164062 ' fill-opacity='1' fill-rule='nonzero'%3E%3C/path%3E%3C/g%3E%3C/svg%3E\")");
}});


// Add slideDown animation to Bootstrap dropdown when expanding.
$('.dropdown').on('show.bs.dropdown', function() {
    $(this).find('.dropdown-menu').first().stop(true, true).slideDown(300);
});

// Add slideUp animation to Bootstrap dropdown when collapsing.
$('.dropdown').on('hide.bs.dropdown', function() {
    $(this).find('.dropdown-menu').hide();
});


// Add event listener for click event on the close button
$('.toast .btn-close').on('click', function() {
    var toast = $(this).closest('.toast');
    // Animate the toast element
    toast.animate({
        opacity: 0,
        height: 0,
        marginBottom: 0
    }, 500, function() {
        // Remove the toast element from the DOM
        toast.remove();
    });
});


// On submit button hover change text alignment in form
$('.input_submit').hover(function() {
    $('.form-control').addClass('align-text-center');
}, function() {
    $('.form-control').removeClass('align-text-center');
});

$(document).ready(function(){

// Timezone settings
const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone; // e.g. "America/New_York"
document.cookie = "django_timezone=" + timezone;

// If a modal hasn't disappeared, hide it
$(window).on("pageshow", function() {
    $('.modal').modal('hide');
});


// Animate toast 
$(".toast").css("opacity", "0");
$(".toast").toast("show");
$(".toast").addClass("custom-fade-in").css("opacity", "1");

setTimeout(function() {
    hideToast();
}, 5000);


function hideToast() {
    var toast = $('.hide_this');
    // Animate the toast element
    toast.animate({
        opacity: 0,
        height: 0,
        marginBottom: 0
    }, 1000, function() {
    // Remove the toast element from the DOM
    toast.remove();
    });
};
  });