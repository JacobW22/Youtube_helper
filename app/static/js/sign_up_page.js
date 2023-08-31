$(document).ready(function(){

    // Fade In page
    $('.main-container').fadeIn(500).removeClass('d-none').addClass('d-flex');

});

document.addEventListener("DOMContentLoaded", function () {
  var form = document.getElementById("main_form"); 
  form.addEventListener("submit", sendForm);
});

function sendForm(event) {
  event.preventDefault();

  var emailField = document.getElementById("emailField");
  var form = event.target; 

  emailField.value = emailField.value.toLowerCase();
  form.submit();
}


function sendFormWithClick() {
  event.preventDefault();

  var emailField = document.getElementById("emailField");
  var submit = document.getElementById("submitBtn"); 

  emailField.value = emailField.value.toLowerCase();
  submit.click();
}