function sendMessage() {

    data()

}

function renderPage(d) {

    document.getElementById("grouptitle").innerText = d.title;
    document.getElementById("body").style.color = d.primary;
    document.getElementById("body").style.backgroundColor = d.secondary;
    document.getElementById("image").src = d.image;

    var a = document.getElementsByTagName('a')

    for(i =0; i < a.length; i++){
        a[i].style.color = d.primary;
    }

}

function data(){
    fetch(`/groupdata`)
        .then(response => response.json())
        .then(data => {
            console.log(data[0]);
            renderPage(data[0]);
        });
}


window.onload = function() {

    console.log(banana);
    

    this.data();
}