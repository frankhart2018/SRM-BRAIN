$(document).ready(function() {

  $("#add-univ-button").click(function() {
    var university = $("#university-input").val();

    if(university != "") {

      var core_str = "/srmbrain";

      $.ajax({
        url: core_str + "/add-details",
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

  $("#add-dept-button").click(function() {
    var dept_abbr = $("#dept-abbr-input").val();
    var dept = $("#dept-input").val();

    if(dept_abbr != "" && dept != "") {

      var core_str = "/srmbrain";

      $.ajax({
        url: core_str + "/add-details",
        method: "post",
        dataType: "json",
        data: {"dept_abbr": dept_abbr, "dept": dept},
        success: function(result) {
          window.swal({title: result.title, text: result.message, icon: result.status}).then(function() {
            window.location = result.href;
          });
        }
      });

    } else {
      window.swal({title: "Error!", text: "Enter all details!", icon: "error"});
    }
  });

});
