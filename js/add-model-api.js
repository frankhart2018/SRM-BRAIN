$(document).ready(function() {

  $("#add-model-button").click(function() {
    var name = $("#model-name-input").val();
    var desc = $("#model-desc-input").val();
    var model = $("#model-input").val();

    if(name != "" && desc != "" && model != "") {

      var core_str = "/srmbrain";

      var form_data = new FormData();
      form_data.append('model_name', $("#model-name-input").val());
      form_data.append('model_desc', $("#model-desc-input").val());
      form_data.append('dataset', $("#dataset-input").val());
      form_data.append('code', $("#code-input")[0].files[0]);
      form_data.append('model', $("#model-input")[0].files[0]);

      $.ajax({
        url: core_str + "/add-model",
        method: "post",
        data: form_data,
        contentType: false,
        cache: false,
        processData: false,
        success: function(result) {
          window.swal({title: result.title, text: result.message, icon: result.status}).then(function() {
            window.location = result.href;
          });
        }
      });

    } else {
      window.swal({title: "Error!", text: "Filling name, description and uploading model is necessary!", icon: "error"});
    }
  });

});
