
$(document).ready(function(){
    $('[data-bs-toggle="tooltip"]').tooltip();   
  });
  
  
  function RevealToken() {
    var token_form = document.getElementById("token");
    var revealButton = document.getElementById("revealButton");
  
    if (token_form.getAttribute("type") == "password") {
      token_form.setAttribute("type", "text");
      revealButton.innerHTML = "Hide Api Token";
    }
    else {
      token_form.setAttribute("type", "password");
      revealButton.innerHTML = "Reveal Api Token";
    }
  }
  
  
  function copy_to_clipboard() {
    var copyText = document.getElementById("token");
  
    navigator.clipboard.writeText(copyText.value);
    
    $('[data-bs-toggle="tooltip"]').attr('title', 'Copied!');
  
    $('[data-bs-toggle="tooltip"]').each(function( index ) {
      var tooltip = bootstrap.Tooltip.getInstance($(this));
      tooltip.setContent({'.tooltip-inner': 'Copied!'});
    })
  }
  
  
  $('[data-bs-toggle="tooltip"]').mouseout(function(){
    $('[data-bs-toggle="tooltip"]').each(function( index ) {
      var tooltip = bootstrap.Tooltip.getInstance($(this));
      tooltip.setContent({'.tooltip-inner': 'Copy to clipboard'});
    })
  });