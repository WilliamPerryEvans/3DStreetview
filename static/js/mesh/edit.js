// use bathymetry_edit.js as example for form capture and submit after other stuff

var flashMessage = function(data){
  html = '';
  for (i=0; i<data.length; i++) {
    html += '<div class="alert alert-' + data[i]['type'] + '"><a href="#" class="close" data-dismiss="alert">&times;</a>' + data[i].message + '</div>';
  }
  return html;
};
//$(function() {
//    $('#odm_config').on('change', () => {
function removeOptions(selectElement) {
   var i, L = selectElement.options.length - 1;
   for(i = L; i >= 0; i--) {
      selectElement.remove(i);
   }
}

function get_odm_projects()
{
    // get current id of mesh
    const id = $('input#mesh_id').val();
    const odmconfig_id = $('#odm_config').val();
    document.getElementById("task_button").disabled = true;
    // clear current projects in dropdown
    var project_select = document.getElementById("odm_project");
    removeOptions(project_select);
    console.log(odmconfig_id);
    console.log("Hello World");
    $.getJSON(
        `/api/odm/${odmconfig_id}/projects`,
        function(data) {
            // populate the project dropdown with results
            console.log(data.results)
            data.results.forEach(function(x) {
                var option = document.createElement("option");
                option.text = x.name;
                option.value = x.id;
                project_select.add(option);
            });
            $('#flash').append(flashMessage([{"type": "success", "message": "Server found"}]));
            document.getElementById("task_button").disabled = false;

        }
    )
    .fail(function() {
        // flash a message in case everything fails
        $('#flash').append(flashMessage([{"type": "danger", "message": "Server not available"}]));
    });
};

function get_odm_tasks()
{
    // get current id of mesh
    const id = $('input#mesh_id').val();
    const odmconfig_id = $('#odm_config').val();
    var project_select = document.getElementById("odm_project");
    const odmproject_id = project_select.value;
    console.log(odmproject_id);
    var task_select = document.getElementById("odm_task");
    // clear current tasks in dropdown
    removeOptions(task_select);
    $.getJSON(
        `/api/odm/${odmconfig_id}/projects/${odmproject_id}`,
        function(data) {
            // populate the project dropdown with results
            console.log(data)
            data.tasks.forEach(function(x) {
                var option = document.createElement("option");
                option.text = x;
                option.value = x;
                task_select.add(option);
            });
            $('#flash').append(flashMessage([{"type": "success", "message": "Retrieved tasks"}]));

        }
    )
    .fail(function() {
        // flash a message in case everything fails
        $('#flash').append(flashMessage([{"type": "danger", "message": "Not able to retrieve tasks"}]));
    });
};
