$(document).ready(function() {

  $("#add-univ-button").click(function() {
    var university = $("#university-input").val();

    if(university != "") {

      $.ajax({
        url: "/add-univ",
        method: "post",
        dataType: "json",
        data: {"university": university},
        success: function(result) {
          window.swal({title: result.title, text: result.message, icon: result.status}).then(function() {
            window.location = result.href;
          });
        }
      });

    } else {
      window.swal({title: "Error!", text: "Enter name of university!", icon: "error"});
    }
  });

});
