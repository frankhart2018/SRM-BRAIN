$(document).ready(function() {

  function validateEmail(email) {
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
  }

  $("#register-button").click(function() {
    var name = $("#name-input").val();
    var email = $("#email-input").val();
    var university = $("#university-input").val();
    var department = $("#department-input").val();
    var year = $("#year-input").val();
    var password = $("#password-input").val();
    var cpassword = $("#cpassword-input").val();

    if(name != "" && email != "" && university != "" && department != "0" && year != "0" && password != "" && cpassword != "") {

      var error = 0;
      var errorString = "";

      if(!validateEmail(email)) {
        error++;
        errorString += "Invalid email address!\n";
      }

      if(password != cpassword) {
        error++;
        errorString += "Passwords do not match!\n";
      }

      if(error > 0) {
        window.swal({title: "Error!", text: errorString, icon: "error"});
      } else {

        $.ajax({
          url: "/register",
          method: "post",
          dataType: "json",
          data: {"name": name, "email": email, "university": university, "department": department, "year": year, "password": password},
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
