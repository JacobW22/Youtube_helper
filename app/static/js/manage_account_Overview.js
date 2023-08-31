$(document).ready(function(){

    // Style url tags
    var text = $('td:nth-child(2)').text();


    $('td:nth-child(2)').wrapInner(function() {
        return "<a href='" + $(this).text() + "' target='_blank' rel='noopener noreferrer'></a>"
    });

    $('td:nth-child(2)').find("a").prepend("<i class='fa-solid fa-arrow-up-right-from-square'>&nbsp;</i>")


    // Counting animation
    $('.count').each(function () {
        $(this).prop('Counter',-1).animate({
            Counter: $(this).text()
        }, {
            duration: 1000,
            easing: 'swing',
            step: function (now) {
                $(this).text(Math.ceil(now));
            }
        });
    });

});