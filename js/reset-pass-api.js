$(document).ready(function() {

  $("#reset-button").click(function() {
    var password = $("#password-input").val();
    var cpassword = $("#cpassword-input").val();

    if(password != "" && cpassword != "") {

      var error = 0;
      var errorString = "";

      if(password != cpassword) {
        error++;
        errorString += "Passwords should be same!";
      }

      if(error > 0) {
        window.swal({title: "Error!", text: errorString, icon: "error"});
      } else {

        var core_str = "/srmbrain";

        var email = window.location.href.split("q=")[1];

        $.ajax({
          url: core_str + "/reset-pass",
          method: "post",
          dataType: "json",
          data: {"email": email, "password": password},
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
