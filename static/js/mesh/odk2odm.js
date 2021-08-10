$(document).ready(function () {
    // fill drop down
    get_odm_tasks();
    get_odk_forms();
});

function get_odk_forms() {
    const odkconfig_id = $('input#odk_config').val();
    const odkproject_id = $('input#odkproject_id').val();
    var form_select = document.getElementById("odk_form");
    removeOptions(form_select);
    addDisabledOption(form_select);
    $.getJSON(
        `/api/odk/${odkconfig_id}/projects/${odkproject_id}/forms`,
        function(data) {
            // populate the project dropdown with results
            console.log(data);
            // fill drop down with ODK forms
            data.forEach(function(form) {
                var option = document.createElement("option");
                option.text = `Name: ${form.name} Version: ${form.version}`;
                option.value = form.xmlFormId;
                form_select.add(option);

            });
            flashMessage([{"type": "success", "message": "Retrieved forms"}]);
        }
    )
    .fail(function() {
        // flash a message in case everything fails
        flashMessage([{"type": "danger", "message": "Not able to retrieve tasks"}]);
    });
}

function get_submissions() {
    // get submissions of selected ODK form
    const odkconfig_id = $('input#odk_config').val();
    const odkproject_id = $('input#odkproject_id').val();
    form_id = document.getElementById('odk_form').value;
    url = `/api/odk/${odkconfig_id}/projects/${odkproject_id}/forms/${form_id}/submissions`
    $.getJSON(
        url,
        function(submissions) {
            // get the list of attachments per submission
            attachments = submissions.map(get_attachments);
            console.log(submissions);
            // fill bootstrap table
            $('#submissions').bootstrapTable('load', submissions)
            flashMessage([{"type": "success", "message": "Retrieved submissions"}]);
        }
    )
    .fail(function() {
        // flash a message in case everything fails
        flashMessage([{"type": "danger", "message": "Not able to retrieve tasks"}]);
    });
}

function get_attachments(submission){
    console.log(url);
    res = $.getJSON({
        url: `${url}/${submission.instanceId}/attachments`,
        async: false
    });
    return res.responseJSON
}


function get_odm_tasks()
{    // get current id of mesh
    const id = $('input#mesh_id').val();
    const odmconfig_id = $('input#odm_config').val();
    const odmproject_id = $('input#odmproject_id').val();
    document.getElementById("task_create_button").disabled = true;
    document.getElementById("task_delete_button").disabled = true;
    var task_select = document.getElementById("odm_task");
    // clear current tasks in dropdown
    removeOptions(task_select);
    addDisabledOption(task_select);
    $.getJSON(
        `/api/odm/${odmconfig_id}/projects/${odmproject_id}`,
        function(data) {
            // populate the project dropdown with results
            data.tasks.forEach(function(x) {
                $.getJSON(
                    `/api/odm/${odmconfig_id}/projects/${odmproject_id}/tasks/${x}`,
                    function(task) {
//                    });
                        var option = document.createElement("option");
                        option.text = `Name: ${task.name} id: ${task.id}`;
                        option.value = task.id;
                        task_select.add(option);
                });
            }),
            flashMessage([{"type": "success", "message": "Retrieved tasks"}]);
            document.getElementById("task_create_button").disabled = false;
            document.getElementById("task_delete_button").disabled = false;
//            // fill information about the current selected task
//            get_odm_task();
        }
    )
    .fail(function() {
        // flash a message in case everything fails
        flashMessage([{"type": "danger", "message": "Not able to retrieve tasks"}]);
    });
}

function get_odm_task()
{
    // get current id of mesh
    const id = $('input#mesh_id').val();
    const odmconfig_id = $('#odm_config').val();
    const odmproject_id = $('input#odmproject_id').val();
    var task_select = document.getElementById("odm_task");
    const task_id = task_select.value;
    document.getElementById("task_create_button").disabled = true;
    document.getElementById("task_delete_button").disabled = true;
    // clear current tasks in dropdown
    $.getJSON(
        `/api/odm/${odmconfig_id}/projects/${odmproject_id}/tasks/${task_id}`,
        function(data) {
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
            flashMessage([{"type": "success", "message": `Retrieved task ${task_id}`}]);
            document.getElementById("task_create_button").disabled = false;
            document.getElementById("task_delete_button").disabled = false;
}



function create_odm_task() {
    // get current id of mesh
    const id = $('input#mesh_id').val();
    const odmconfig_id = $('#odm_config').val();
    const odmproject_id = $('input#odmproject_id').val();
    const task_name = $('input#odm_task_name').val();
    content = {
        "name": task_name,
        "partial": true,
        "options": {}
    }
    $.ajax({
        type: 'POST',
        url: `/api/odm/${odmconfig_id}/projects/${odmproject_id}/tasks/`,
        data: JSON.stringify(content),
        contentType: "application/json",
        dataType: 'json',
        // Submit parent form on success.
        success: function(data) {
            console.log(data);
            // refresh project list
            get_odm_tasks();
            $('#newOdmTask').modal('hide');
            flashMessage([{"type": "success", "message": "New ODM task created"}]);

        },
        // Enable save button again.
        error: function() { flashMessage([{"type": "danger", "message": "Not able to create ODM task"}]) }
    });
}

function buttons () {
    return {
      btnTransfer: {
        text: 'Transfer to ODK',
        icon: 'fa-exchange',
        event: function () {
          alert('This button will allow you to transfer. Not implemented yet.')
        },
        attributes: {
          title: 'Transfer all files filtered below to the selected ODM task'
        }
      },
    }
}
