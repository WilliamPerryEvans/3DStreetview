$(document).ready(function () {
    // simulate a click
    document.getElementById("formButton").click();
});

// use bathymetry_edit.js as example for form capture and submit after other stuff
function openTab(evt, tabName) {
  // Declare all variables
  var i, tabcontent, tablinks;

  // Get all elements with class="tabcontent" and hide them
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }

  // Get all elements with class="tablinks" and remove the class "active"
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }

  // Show the current tab, and add an "active" class to the button that opened the tab
  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.className += " active";
}

var flashMessage = function(data){
  html = '';
  for (i=0; i<data.length; i++) {
    html += '<div class="alert alert-' + data[i]['type'] + '"><a href="#" class="close" data-dismiss="alert">&times;</a>' + data[i].message + '</div>';
  }
  return html;
};

function removeOptions(selectElement) {
   var i, L = selectElement.options.length - 1;
   for(i = L; i >= 0; i--) {
      selectElement.remove(i);
   }
}

function addDisabledOption(selectElement) {
    var option = document.createElement("option");
    option.text = " -- select an option -- ";
//    option.value = x.id;
    option.disabled = true;
    option.selected = true;
    selectElement.add(option);
}

function millisToMinutesAndSeconds(millis) {
    var minutes = Math.floor(millis / 60000);
    var seconds = ((millis % 60000) / 1000).toFixed(0);
	//ES6 interpolated literals/template literals
  	//If seconds is less than 10 put a zero in front.
    return `${minutes}:${(seconds < 10 ? "0" : "")}${seconds}`;
}

function get_odm_projects()
{
    // get current id of mesh
    const id = $('input#mesh_id').val();
    const odmconfig_id = $('#odm_config').val();
    document.getElementById("project_create_button").disabled = true;
    document.getElementById("project_delete_button").disabled = true;
    // clear current projects in dropdown
    var project_select = document.getElementById("odm_project");
    removeOptions(project_select);
    addDisabledOption(project_select);
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
            document.getElementById('flash').innerHTML =flashMessage([{"type": "success", "message": "Server found"}]);
            document.getElementById("project_create_button").disabled = false;
            document.getElementById("project_delete_button").disabled = false;

        }
    )
    .fail(function() {
        // flash a message in case everything fails
        document.getElementById('flash').innerHTML = flashMessage([{"type": "danger", "message": "Server not available"}]);
    });
};

function get_odm_tasks()
{    // get current id of mesh
    const id = $('input#mesh_id').val();
    const odmconfig_id = $('#odm_config').val();
    var project_select = document.getElementById("odm_project");
    const odmproject_id = project_select.value;
    document.getElementById("task_button").disabled = true;
    document.getElementById("task_create_button").disabled = true;
    document.getElementById("task_delete_button").disabled = true;

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
            document.getElementById('flash').innerHTML = flashMessage([{"type": "success", "message": "Retrieved tasks"}]);
            document.getElementById("task_button").disabled = false;
            document.getElementById("task_create_button").disabled = false;
            document.getElementById("task_delete_button").disabled = false;


        }
    )
    .fail(function() {
        // flash a message in case everything fails
        document.getElementById('flash').innerHTML = flashMessage([{"type": "danger", "message": "Not able to retrieve tasks"}]);
    });
};

function get_odm_task()
{
    // get current id of mesh
    const id = $('input#mesh_id').val();
    const odmconfig_id = $('#odm_config').val();
    var project_select = document.getElementById("odm_project");
    const odmproject_id = project_select.value;
    var task_select = document.getElementById("odm_task");
    const task_id = task_select.value;
    document.getElementById("task_button").disabled = true;
    document.getElementById("task_create_button").disabled = true;
    document.getElementById("task_delete_button").disabled = true;

    console.log(task_id);
    // clear current tasks in dropdown
    $.getJSON(
        `/api/odm/${odmconfig_id}/projects/${odmproject_id}/tasks/${task_id}`,
        function(data) {
                console.log(data);
                // change content of status texts and bars
                $('#task_id span').text(`Task: ${task_id}`);
                $('#images_count span').text(` ${data.images_count}`);
                $('#processing_time span').text(` ${millisToMinutesAndSeconds(data.processing_time)}`);
                prog = document.getElementById('upload_progress')
                prog.style = `width: ${data.upload_progress*100}%`
                prog.textContent = `${Math.round(data.upload_progress*data.images_count)}/${data.images_count}`;
                prog = document.getElementById('running_progress')
                prog.style = `width: ${data.running_progress*100}%`
                prog.textContent = `${Math.round(data.running_progress*100)} %`;
            });
            document.getElementById('flash').innerHTML = flashMessage([{"type": "success", "message": `Retrieved task ${task_id}`}]);
            document.getElementById("task_button").disabled = false;
            document.getElementById("task_create_button").disabled = false;
            document.getElementById("task_delete_button").disabled = false;
    // open the edit tab
    openTab(event, 'task_view')

}

