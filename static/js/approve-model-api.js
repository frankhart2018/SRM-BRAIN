$(document).ready(function() {

  $("#approve-button").click(function() {

    var url = $(location).attr("href");
    var id = url.split("=")[1];

    $.ajax({
      url: "/approve",
      method: "post",
      dataType: "json",
      data: {"id": id, "status": 1},
      success: function(result) {
        window.swal({title: result.title, text: result.message, icon: result.status}).then(function() {
          window.location = result.href;
        });
      }
    });

  });

  $("#reject-button").click(function() {

    var url = $(location).attr("href");
    var id = url.split("=")[1];

    $.ajax({
      url: "/approve",
      method: "post",
      dataType: "json",
      data: {"id": id, "status": -1},
      success: function(result) {
        window.swal({title: result.title, text: result.message, icon: result.status}).then(function() {
          window.location = result.href;
        });
      }
    });

  });

});
