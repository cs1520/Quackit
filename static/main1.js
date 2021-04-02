var msgBoard = [];
var timBoard = [];
var pos = 0;

function sendMessage() {

    data()

}

function renderPage(d) {
    document.getElementById("channel").innerHTML = d["Color"];
}

function data(){
    fetch(`/groupdata`)
        .then(response => response.text())
        .then(data => {
            console.log(data);
        });
}


window.onload = function() {

    console.log("Hello");

    this.data();
}