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
//  html = '';
  html = document.getElementById("flash").innerHTML;
  for (i=0; i<data.length; i++) {
    html += '<div class="alert alert-' + data[i]['type'] + '"><a href="#" class="close" data-dismiss="alert">&times;</a>' + data[i].message + '</div>';
  }
  document.getElementById("flash").innerHTML = html;
  setTimeout(function() {
    $(".alert").fadeTo(500, 0).slideUp(500, function(){
        $(this).remove();
    });
  }, 4000);
//  setTimeout(function() {
//      $(".alert").alert('close');
//  }, 2000);
//  return html;
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
    option.value = null;
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
