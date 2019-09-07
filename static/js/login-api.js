$(document).ready(function() {

  function validateEmail(email) {
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
  }

  $("#login-button").click(function() {
    var email = $("#email-input").val();
    var password = $("#password-input").val();

    if(email != "" && password != "") {

      var error = 0;
      var errorString = "";

      if(!validateEmail(email)) {
        error++;
        errorString += "Invalid email address!\n";
      }

      if(error > 0) {
        window.swal({title: "Error!", text: errorString, icon: "error"});
      } else {

        $.ajax({
          url: "/login",
          method: "post",
          dataType: "json",
          data: {"email": email,  "password": password},
          success: function(result) {
            window.swal({title: result.title, text: result.message, icon: result.status}).then(function() {
              window.location = result.href;
            });
          }
        });

      }

    } else {
      window.swal({title: "Error!", text: "Complete the form!", icon: "error"});
    }
  });

});
