$(document).ready(function() {

  function validateEmail(email) {
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
  }

  $("#send-button").click(function() {
    var email = $("#email-input").val();

    if(email != "") {

      var error = 0;
      var errorString = "";

      if(!validateEmail(email)) {
        error++;
        errorString += "Invalid email address!\n";
      }

      if(error > 0) {
        window.swal({title: "Error!", text: errorString, icon: "error"});
      } else {

        window.swal({
          title: "Checking...",
          text: "Please wait, processing!",
          showConfirmButton: false,
          allowOutsideClick: false
        });

        var core_str = "/srmbrain";

        $.ajax({
          url: core_str + "/reset",
          method: "post",
          dataType: "json",
          data: {"email": email},
          success: function(result) {
            window.swal.close();
            window.swal({title: result.title, text: result.message, icon: result.status}).then(function() {
              window.location = result.href;
            });
          }
        });

      }

    } else {
      window.swal({title: "Error!", text: "Enter an email address!", icon: "error"});
    }
  });

});
