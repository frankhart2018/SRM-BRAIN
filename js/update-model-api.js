$(document).ready(function() {

  $("#update-button").click(function() {
    var desc = $("#model-desc-input").val();

    var id = window.location.href.split("q=")[1];

    if(desc != "") {

      var core_str = "/srmbrain";

      $.ajax({
        url: core_str + "/model",
        method: "post",
        dataType: "json",
        data: {"id": id, "desc": desc},
        success: function(result) {
          window.swal({title: result.title, text: result.message, icon: result.status}).then(function() {
            window.location = result.href;
          });
        },
        error: function(e) {
          console.log(e);
        }
      });

    } else {
      window.swal({title: "Error!", text: "Cannot update to empty description!", icon: "error"});
    }
  });

});
