window.pressed = function(){
    var a = document.getElementById('aa');
    if(a.value == "")
    {
        fileLabel.innerHTML = "Choose file";
    }
    else
    {
        var theSplit = a.value.split('\\');
        fileLabel.innerHTML = theSplit[theSplit.length-1];
    }
};

var loadFile = function(event) {
	var image = document.getElementById('output');
	image.src = URL.createObjectURL(event.target.files[0]);
};
var loadVideo = function(event) {
	var video = document.getElementById('video-output');
	video.src = URL.createObjectURL(event.target.files[0]);
};