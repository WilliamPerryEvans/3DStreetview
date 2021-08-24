const odkconfig_id = $('input#odk_config').val()
const odkproject_id = $('input#odkproject_id').val();
const odmconfig_id = $('input#odm_config').val();
const odmproject_id = $('input#odmproject_id').val();
const id = $('input#mesh_id').val();
var progress_title = "Upload progress";
var odk2odm_total = 0;
var odk2odm_progress = 0;  // percentage of upload progress
var task_data = {};

$(document).ready(function () {
    // fill drop down
    get_odm_tasks();
    get_odk_forms();
});

function get_odk_forms() {
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
    form_id = document.getElementById('odk_form').value;
    url = `/api/odk/${odkconfig_id}/projects/${odkproject_id}/forms/${form_id}/submissions`
    $.getJSON(
        url,
        function(submissions) {
            // get the list of attachments per submission
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
                        var option = document.createElement("option");
                        option.text = `Name: ${task.name} id: ${task.id}`;
                        option.value = task.id;
                        task_select.add(option);
                });
            }),
            flashMessage([{"type": "success", "message": "Retrieved tasks"}]);
            document.getElementById("task_create_button").disabled = false;
            document.getElementById("task_delete_button").disabled = false;
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
    var task_select = document.getElementById("odm_task");
    const task_id = task_select.value;
    if (task_id != "null") {
        document.getElementById("task_create_button").disabled = true;
        document.getElementById("task_delete_button").disabled = true;
        // clear current tasks in dropdown
        $.getJSON(
            `/api/odm/${odmconfig_id}/projects/${odmproject_id}/tasks/${task_id}`,
            function(data) {
                task_data = data;  // globalize current task data
                // change content of status texts and bars
                $('#task_id span').text(`Task: ${task_id}`);
                $('#images_count span').text(` ${data.images_count}`);
                $('#processing_time span').text(` ${millisToMinutesAndSeconds(data.processing_time)}`);
                $('#progress_title').text(progress_title);
                prog = document.getElementById('upload_progress')
                prog.style = `width: ${odk2odm_progress/odk2odm_total*100}%`
                prog.textContent = `${odk2odm_progress}/${odk2odm_total}`;
                prog = document.getElementById('running_progress')
                prog.style = `width: ${data.running_progress*100}%`
                prog.textContent = `${Math.round(data.running_progress*100)} %`;
                // handle status of buttons
                if (data.images_count > 0 && (data.status != 10 && data.status != 20)){   // status checks are according to https://docs.webodm.org/#status-codes
                    // make the run button active
                    document.getElementById('odm_commit').disabled = false
                    document.getElementById('odm_cancel').disabled = true
                } else {
                    document.getElementById('odm_commit').disabled = true
                    document.getElementById('odm_cancel').disabled = false
                    document.getElementById('odm_delete').disabled = false
                }
                if (data.status == 10 || data.status == 20){
                    $("#odm_commit").html("<i class=\"fas fa-cog fa-spin\"></i> Task running")
                } else {
                    $("#odm_commit").html("<i class=\"fas fa-play-circle\"></i> Launch task")
                }
            }
        );
        flashMessage([{"type": "success", "message": `Retrieved task ${task_id}`}]);
        document.getElementById("task_create_button").disabled = false;
        document.getElementById("task_delete_button").disabled = false;
    }
}

function delete_odm_task() {
    // Deletes selected odm task from odm server
    document.getElementById("task_delete_button").disabled = true;
    var task_select = document.getElementById("odm_task");
    const task_id = task_select.value;
    if (confirm(`If you delete task ${task_id}, all of its assets will be destroyed`)) {
        $.ajax({
            type: 'POST',
            url: `/api/odm/${odmconfig_id}/projects/${odmproject_id}/tasks/${task_id}/remove/`,
    //        data: JSON.stringify(content),
            contentType: "application/json",
            dataType: 'json',
            // Submit parent form on success.
            success: function(data) {
                console.log(data);
                // refresh project list
                get_odm_tasks();
                flashMessage([{"type": "success", "message": "ODM task deleted"}]);
                document.getElementById("task_delete_button").disabled = false;
            },
            // Enable save button again.
            error: function() { flashMessage([{"type": "danger", "message": "Not able to delete ODM task"}]) }
        });
    }
}

function create_odm_task() {
    // get current id of mesh
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

function commit_odm_task() {
    // Commit odm task
    document.getElementById('odm_download').disabled = true
    document.getElementById('odm_commit').disabled = true
    document.getElementById('odm_cancel').disabled = true
    document.getElementById('odm_delete').disabled = true
    var task_select = document.getElementById("odm_task");
    const task_id = task_select.value;
    // get the status of the task and decide what to do
    if (task_data.status == 50 || task_data.status == 40) {
        url = `/api/odm/${odmconfig_id}/projects/${odmproject_id}/tasks/${task_id}/restart/`
    } else {
        url = `/api/odm/${odmconfig_id}/projects/${odmproject_id}/tasks/${task_id}/commit/`
    }
    console.log(url)
    $.ajax({
        type: 'POST',
        url: url,
        contentType: "application/json",
        dataType: 'json',
        // Submit parent form on success.
        success: function(data) {
            console.log(data);
            get_odm_task();
            flashMessage([{"type": "success", "message": "ODM task commited"}]);
//            document.getElementById("task_delete_button").disabled = true;
//            document.getElementById("task_cancel_button").disabled = false;
        },
        // Enable save button again.
        error: function() { flashMessage([{"type": "danger", "message": "Not able to commit ODM task"}]) }
    });
}

function cancel_odm_task() {
    // Commit odm task
    document.getElementById('odm_download').disabled = true
    document.getElementById('odm_commit').disabled = true
    document.getElementById('odm_cancel').disabled = true
    document.getElementById('odm_delete').disabled = true
    var task_select = document.getElementById("odm_task");
    const task_id = task_select.value;
    $.ajax({
        type: 'POST',
        url: `/api/odm/${odmconfig_id}/projects/${odmproject_id}/tasks/${task_id}/cancel/`,
        contentType: "application/json",
        dataType: 'json',
        // Submit parent form on success.
        success: function(data) {
            console.log(data);
            // refresh project list
            get_odm_task();
            flashMessage([{"type": "success", "message": "ODM task commited"}]);
//            document.getElementById("task_delete_button").disabled = false;
        },
        // Enable save button again.
        error: function() { flashMessage([{"type": "danger", "message": "Not able to commit ODM task"}]) }
    });
}

function getodk_postodm(all=false) {
    odk2odm_progress = 0;
//    alert('This button will allow you to transfer. Not implemented yet.')
    // get the selected items
    if (all==false) {
        // only get selected
        submissions = $('#submissions').bootstrapTable('getSelections')
    } else {
        // get all items
        submissions = $('#submissions').bootstrapTable('getData');
    }
    // first get all attachment we want
    attachments = submissions.map(get_attachments);
    no_attachments = attachments.map(a => a.length);
    odk2odm_total = no_attachments.reduce((a, b) => a + b, 0)  // sum up all lengths of attachments to know total no. photos
    // get a list (per survey) of lists of all attachments in each survey
    // check if an ODM task is selected, and has the right status if not return msg
    var task_select = document.getElementById("odm_task");
    const task_id = task_select.value;
    check_odm_task = false;  // check if the odm task is receptive to photo uploads
    if (task_id != "null") {
        // check if the task can be retrieved
        $.getJSON(
            `/api/odm/${odmconfig_id}/projects/${odmproject_id}/tasks/${task_id}`,
            function(data) {
                if ("id" in data) {
                    // check if status is open to photos
                    if (data.status != 10 && data.status != 20) { // not queued or running
                        // push all photos to odm server
                        submissions.map(t => transfer(t, ));
                    }
                } else {
                    flashMessage([{"type": "danger", "message": "ODM server is online, but cannot find chosen task."}]);
                }
            }
        )
        .fail(function() {
            // flash a message as the API call failed
            flashMessage([{"type": "danger", "message": "Not able to retrieve task, is the ODM server offline?"}]);
        });
    } else {
        flashMessage([{"type": "danger", "message": "No ODM task selected. Please select an ODM task or create a new one for uploads."}]);
    }
//    if
//    submit(data)

}
function transfer(submission){
    attachments = get_attachments(submission);
    formId = document.getElementById('odk_form').value;
    attachments.map(x => file_transfer(x, instanceId=submission.instanceId)); // transfer all files per submission
    // TODO: check if attachments are already present on odm side (by getting a thumbnail)
    // if not, transfer file to odm
    // finalize by checking if ODM task

}

function file_transfer(attachment, instanceId){
    if (attachment.exists) {
        // prepare kwargs for retrieval of attachment from odk
        odk_kwargs = {
            projectId: odkproject_id,
            formId: document.getElementById('odk_form').value,
            instanceId: instanceId,
            filename: attachment.name
        }
        odm_kwargs = {
            task_id: document.getElementById("odm_task").value
        }
        content = {
            odk_kwargs: odk_kwargs,
            odm_kwargs: odm_kwargs
        }
        $.ajax({
            type: 'POST',
            url: `/api/mesh/${id}`,
            data: JSON.stringify(content),
            contentType: "application/json",
            dataType: 'json',
            // Submit parent form on success.
            success: function(data) {
                console.log(data);
                // refresh project list
                odk2odm_progress += 1;
                get_odm_task();
                progress_title = `${data}`;

            },
            // Enable save button again.
            error: function() {
                flashMessage([{"type": "danger", "message": `Could not upload file ${attachment.name}`}])
            }
        });
    }
}

function buttons () {
    return {
      btnTransfer: {
        text: 'Transfer to ODK',
        icon: 'fa-exchange-alt',
        event: function() {
            getodk_postodm(all=true)  // perform transfer of all files
        },
        attributes: {
          title: 'Transfer all files filtered below to the selected ODM task'
        }
      },
      btnTransferSelect: {
        text: 'Transfer selection to ODK',
        icon: 'fa-check-square',
        event: function() {
            getodk_postodm(all=false)  // perform transfer of all files
        },
        attributes: {
          title: 'Transfer selected files filtered below to the selected ODM task'
        }
      },
    }
}

function mesh_to_game () {
    alert("This functionality is not yet implemented. If you want to retrieve the mesh, please go to the configured ODM server and project and download it from there.")
}
$( document ).ready(function() {
    setInterval(get_odm_task, 3000);
});