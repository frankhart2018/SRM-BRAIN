$(document).ready(function() {

  function validateEmail(email) {
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
  }

  $("#edit-details-button").click(function() {
    var name = $("#name-input").val();
    var email = $("#email-input").val();
    var register = $("#register-input").val();

    if(name != "" && email != "" && register != "") {

      var error = 0;
      var errorString = "";

      if(!validateEmail(email)) {
        error++;
        errorString += "Invalid email address!\n";
      }

      if(register.length != 15) {
        error++;
        errorString += "Invalid register number!\n";
      }

      if(error > 0) {
        window.swal({title: "Error!", text: errorString, icon: "error"});
      } else {

        $.ajax({
          url: "/about",
          method: "post",
          dataType: "json",
          data: {"name": name, "email": email,  "register": register},
          success: function(result) {
            window.swal({title: result.title, text: result.message, icon: result.status}).then(function() {
              window.location = result.href;
            });
          }
        });

      }

    } else {
      window.swal({title: "Error!", text: "Cannot delete information!", icon: "error"});
    }
  });

});
