$(document).ready(function() {

  function validateEmail(email) {
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
  }

  $("#edit-details-button").click(function() {
    var name = $("#name-input").val();
    var email = $("#email-input").val();

    if(name != "" && email != "") {

      var error = 0;
      var errorString = "";

      if(!validateEmail(email)) {
        error++;
        errorString += "Invalid email address!\n";
      }

      if(error > 0) {
        window.swal({title: "Error!", text: errorString, icon: "error"});
      } else {

        var core_str = "/srmbrain";

        $.ajax({
          url: core_str + "/about",
          method: "post",
          dataType: "json",
          data: {"name": name, "email": email},
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
