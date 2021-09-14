const odkconfig_id = $('input#odk_config').val()
const odkproject_id = $('input#odkproject_id').val();
const odmconfig_id = $('input#odm_config').val();
const odmproject_id = $('input#odmproject_id').val();
const id = $('input#mesh_id').val();
const current_task = $('input#current_task').val();
var upload_title = "Upload progress";
var odk2odm_total = 0;
var odk2odm_progress = 0;  // percentage of upload progress
var task_data = {};

$(document).ready(function () {
    // fill drop down
    get_odm_tasks();
    get_odk_forms();
});

function get_odk_forms() {
    // retrieve all odk forms in selected odk project
    var form_select = document.getElementById("odk_form");
    removeOptions(form_select);
    addDisabledOption(form_select);
    $.getJSON(
        `/api/odk/${odkconfig_id}/projects/${odkproject_id}/forms`,
        function(data) {
            // populate the project dropdown with results
            console.log(data);
            if ("code" in data) {
                if (data.code == 401.2) {
                    flashMessage([{"type": "danger", "message": "ODK server authorization not accepted. Did you change username or password?"}]);
                } else {
                    // something else went wrong, report that!
                    flashMessage([{"type": "danger", "message": data.message}]);
                }
            } else {
                // fill drop down with ODK forms
                data.forEach(function(form) {
                    var option = document.createElement("option");
                    option.text = `Name: ${form.name} Version: ${form.version}`;
                    option.value = form.xmlFormId;
                    form_select.add(option);

                });
                flashMessage([{"type": "success", "message": "Retrieved ODK forms"}]);
            }
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
            console.log(submissions);
            if ("code" in submissions) {
                if (submissions.code == 401.2) {
                    flashMessage([{"type": "danger", "message": "ODK server authorization not accepted. Did you change username or password?"}]);
                } else {
                    // something else went wrong, report that!
                    flashMessage([{"type": "danger", "message": submissions.message}]);
                }
            } else {
                // fill bootstrap table
                $('#submissions').bootstrapTable('load', submissions)
                flashMessage([{"type": "success", "message": "Retrieved submissions"}]);
            }
        }
    )
    .fail(function() {
        // flash a message in case everything fails
        flashMessage([{"type": "danger", "message": "Not able to retrieve tasks"}]);
    });
}

function get_odm_tasks() {
    // retrieves all odm tasks under current odm project
    // get current id of mesh
    document.getElementById("task_create_button").disabled = true;
    document.getElementById("task_delete_button").disabled = true;
    var task_select = document.getElementById("odm_task");
    // clear current tasks in dropdown
    removeOptions(task_select);
    addDisabledOption(task_select);
    $.ajax({
        url: `/api/odm/${odmconfig_id}/projects/${odmproject_id}`,
        dataType: "json",
        success: function(data) {
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
            });
            flashMessage([{"type": "success", "message": "Retrieved ODM tasks"}]);
            document.getElementById("task_create_button").disabled = false;
            document.getElementById("task_delete_button").disabled = false;
        },
        error: function(data) {
            console.log(data);
            if (data.status == 403) {
                flashMessage([{"type": "danger", "message": "ODM server authorization not accepted. Did you change username or password?"}]);
            } else if (data.status == 404) {
                flashMessage([{"type": "danger", "message": "ODM server not available"}]);
            } else {
                flashMessage([{"type": "danger", "message": `Server responded with ${data.status} ${data.statusText}`}]);
            }
        }
    });
}

function update_odm_task() {
    // get all information on selected odm task and update all information in html according to status
    // get current id of mesh
    var task_select = document.getElementById("odm_task");
    const task_id = task_select.value;
    if (task_id != "null") {
        document.getElementById("task_create_button").disabled = true;
        document.getElementById("task_delete_button").disabled = true;
        document.getElementById("odm_download").disabled = true;
        // clear current tasks in dropdown
        $.getJSON(
            `/api/odm/${odmconfig_id}/projects/${odmproject_id}/tasks/${task_id}`,
            function(data) {
                console.log(data);
                task_data = data;  // globalize current task data
                // change content of status texts and bars
                $('#task_id span').text(`Task: ${task_id}`);
                $('#images_count span').text(` ${data.images_count}`);
                $('#processing_time span').text(` ${millisToMinutesAndSeconds(data.processing_time)}`);
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
                if (data.status != 10 && data.status != 20){
                    $("#odm_commit").html("<i class=\"fas fa-play-circle\"></i> Launch task")
                    if (data.available_assets.length > 0) {
                        var assets_select = document.getElementById("odm_assets");
                        // remove any children
                        assets_select.innerHTML = "";
                        // add children
                        data.available_assets.forEach(function(x) {
                            option = document.createElement("a");
                            option.className = "dropdown-item";
                            option.text = `${x}`;
                            option.href = `/api/odm/${odmconfig_id}/projects/${odmproject_id}/tasks/${task_id}/download/${x}`;
                            option.value = x;
                            assets_select.append(option);
                        });
                        // enable the button, triggering this dropdown menu
                        document.getElementById("odm_download").disabled = false;
                        // button needs one click before dropdown works
                        $("#odm_download").click();

                    }
                } else {
                    $("#odm_commit").html("<i class=\"fas fa-cog fa-spin\"></i> Task running")
                    setTimeout(function() {
                        update_odm_task();
                    }, 2000);
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
    // create a new odm task in selected odm project via a HTML modal
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
    // Commit odm task so that it is processed
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
    console.log(url);
    $.ajax({
        type: 'POST',
        url: url,
        contentType: "application/json",
        dataType: 'json',
        // Submit parent form on success.
        success: function(data) {
            console.log(data);
            setTimeout(function() {
                update_odm_task();
                }, 2000);
            flashMessage([{"type": "success", "message": "ODM task commited"}]);
        },
        // Enable save button again.
        error: function() { flashMessage([{"type": "danger", "message": "Not able to commit ODM task"}]) }
    });
}

function cancel_odm_task() {
    // Cancel currently selected and running odm task (only available when running)
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
            update_odm_task();
            flashMessage([{"type": "success", "message": "ODM task commited"}]);
        },
        // Enable save button again.
        error: function() { flashMessage([{"type": "danger", "message": "Not able to commit ODM task"}]) }
    });
}

function getodk_postodm(all=false) {
    // posts a list of odk submissions from selected odk project and form to back end worker
    // back-end worker then transfers selected submissions to the selected odm server-project-task
    odk2odm_progress = 0;
    // get the selected items
    if (all==false) {
        // only get selected
        submissions = $('#submissions').bootstrapTable('getSelections')
    } else {
        // get all items
        submissions = $('#submissions').bootstrapTable('getData');
    }
    console.log(submissions);
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
                        $.ajax({
                            type: 'POST',
                            url: `/api/mesh/odk2odm/${id}`,
                            data: JSON.stringify({
                                "submissions": submissions,
                                "odm_task": document.getElementById("odm_task").value,
                                "odk_formId": document.getElementById('odk_form').value
                            }),
                            contentType: "application/json",
                            dataType: 'json',
                            statusCode: {
                                202: function(msg) {
                                    console.log(msg);
                                    setTimeout(update_upload(), 2000);
                                }

                            },
                            // Enable save button again.
                            error: function(xhr, data) {
                                console.log(xhr);
                                if (xhr.status == 429) {
                                    flashMessage([{"type": "warning", "message": `${xhr.responseText}`}])
                                }
                            }
                        });
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
}

function update_upload() {
    // retrieve status of back-end worker upload, the last submitted job is the default selected job to query status from
    // retrieve mesh from database
    url = `/api/mesh/${id}`;
    $('#upload_title').text("Upload progress");
    prog = document.getElementById('upload_progress')
    $.getJSON(url,
        function(mesh) {
            if (`${mesh.current_task}` != "null") {
                url = `/api/status/${mesh.current_task}`
                $.getJSON(
                    url,
                    function(task) {
                        $('#upload_title').text(`${task.state}: ${task.status}`);
                        if (task["state"] == "SUCCESS"){
                            prog.style = `width: 100%`;
                            prog.textContent = `Upload completed`;
                            update_odm_task();


                        } else if (task["state"] == "PENDING") {
                            console.log("Upload is pending")
                            prog.style = `width: 0%`;
                            prog.textContent = `Uploading pending`;
                            $('#upload_title').text("Upload pending...");
                            setTimeout(function() {
                                // keep on refreshing until upload's done
                                update_upload();
                            }, 2000);
                        } else if (task["state"] == "FAILURE") {
                            console.log("Upload failed")
                            prog.style = `width: 0%`;
                            prog.textContent = `Upload failed, please retry`;
                            $('#upload_title').text("Upload failed...");
                        } else {
                            // upload is busy, make sure that no jobs can be started, stopped or deleted
                            document.getElementById('odm_commit').disabled = true
                            document.getElementById('odm_cancel').disabled = true
                            document.getElementById('odm_delete').disabled = true
                            prog.style = `width: ${task.current/task.total*100}%`
                            prog.textContent = `${task.current}/${task.total}`;
                            setTimeout(function() {
                                // keep on refreshing until upload's done
                                update_upload();
                            }, 2000);
                        }
                    }
                );
            } else {
                prog.style = `width: 0%`;
                prog.textContent = ``;
            }
        }
    );
}

function buttons () {
    // bootstrap table button configuration. We have two buttons: one to transfer all queried submissions, and one to
    // only transfer the check-box selected ones
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
    // TODO: implement when Ivan's work on meshlab is sorted out
    alert("This functionality is not yet implemented. If you want to retrieve the mesh, please go to the configured ODM server and project and download it from there.")
}

$( document ).ready(function() {
    update_upload();
    update_odm_task();
});