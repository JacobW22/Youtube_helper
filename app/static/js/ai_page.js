$(document).ready(function(){

    updateCountdown();

    $( ".position_icons" ).hover(
      function() {
        $(this).closest( '.d-flex' ).find(".fa-solid").css({'transform':'translateY(-0.30em)'});
      }, function() {
        $(this).closest( '.d-flex' ).find(".fa-solid").css({'transform':'translateY(0)'});
      }
    );

  });

  $(".downloading_modal").on('shown.bs.modal', function() {
    $('.modal-backdrop').css('opacity', '0.6');
  });

  $( ".position_icons" ).on( "click", function() {
    $('#selection_modal').modal("hide");
  });
  

  function getTimeUntilMidnight() {
    const now = new Date();
    const midnight = new Date(now);
    midnight.setHours(24, 0, 0, 0); // Set to midnight of the next day

    const timeDifference = midnight - now;
    return timeDifference;
  }

  function updateCountdown() {
    const countdownElement = document.getElementById('countdown');
    const timeDifference = getTimeUntilMidnight();
    const seconds = Math.floor(timeDifference / 1000) % 60;
    const minutes = Math.floor((timeDifference / (1000 * 60)) % 60);
    const hours = Math.floor((timeDifference / (1000 * 60 * 60)) % 24);

    countdownElement.textContent = `New Tickets avalivable in: ${hours}h ${minutes}m ${seconds}s`;

    setTimeout(updateCountdown, 1000);
  }