$(document).ready(function(){
    var i = 0;
    var speed = 50; /* The speed/duration of the effect in milliseconds */
  
    function typeWriter() {
      // Get the text from the source element using jQuery
      var txt = document.getElementById("hidden_username").innerText;
  
      if (i < txt.length) {
        $("#typewriter").append(txt.charAt(i));
        i++;
        setTimeout(typeWriter, speed);
      }
    }
  
    typeWriter();
  });