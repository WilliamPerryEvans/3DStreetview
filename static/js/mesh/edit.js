//$(document).ready(function () {
//    // simulate a click
//    document.getElementById("formButton").click();
//});

// use bathymetry_edit.js as example for form capture and submit after other stuff

function get_odm_projects()
{
    // get current id of mesh
//    const id = $('input#mesh_id').val();
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

function save_project() {
    const id = $('input#mesh_id').val();
    const odmconfig_id = $('#odm_config').val();
    console.log(id);
    console.log(odmconfig_id);
    console.log(document.getElementById("odm_project_name").value);
    console.log(document.getElementById("odm_project_desc").value);
}

$('form.admin-form').submit(function( event ) {
    // Prevent submit.
    event.preventDefault();
    // register the currently chosen ODM project on our own database
    content = {
        "odm_id": parseInt(document.getElementById("odm_config").value),
        "remote_id": parseInt(document.getElementById("odm_project").value)
    }
    console.log(content);

    $.ajax({
        type: 'POST',
        url: `/api/odmproject/create_project`,
        data: JSON.stringify(content),
        contentType: "application/json",
        dataType: 'json',
        // Submit parent form on success.
        success: function() {
            console.log(data);
//            form.submit();
        },
        // Enable save button again.
        error: function() { $('button[type=submit], input[type=submit]').prop('disabled',false); }
    });
        // Prevent submit.

    delete_groups = ["extra_config"]
    delete_groups.forEach(e => $("#" + e).remove());
    // Prevent double actions.
//    $('button[type=submit], input[type=submit]').prop('disabled',true);
    console.log("You have just clicked on --Save--")
    const form = this;
    document.getElementById("odmproject_id").value = 1;
//    form.submit();
    // remove the non-required form components
//    delete_labels.forEach(e => form.removeChild(document.getElementById(e)));
//    console.log(form);
//    $.ajax({
//        type: 'POST',
//        url: `/api/mesh/${id}`,
//        data: JSON.stringify({ "data": data }),
//        contentType: "application/json",
//        dataType: 'json',
//        // Submit parent form on success.
//        success: function() { form.submit(); },
//        // Enable save button again.
//        error: function() { $('button[type=submit], input[type=submit]').prop('disabled',false); }
//    });
});
