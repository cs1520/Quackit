function reportInfo(vars, showType = false) {
    if (showType === true) console.log(typeof vars);
    console.log(vars);
}

function addImg(ele, content) {
    var myDIV = document.querySelector(ele);
    var newContent = document.createElement('div');
    newContent.innerHTML = content;

    while (newContent.firstChild) {
        myDIV.appendChild(newContent.firstChild);
    }
}

var feedback = function(res) {
    reportInfo(res, true);
    if (res.success === true) {
        var get_link = res.data.link.replace(/^http:\/\//i, 'https://');
        document.querySelector('.status').classList.add('bg-success');
        var content =
            'Copy URL to share image: ' + '<br><input class="image-url" id = imgurUrl value=\"'
             + get_link + '\"/>'  + '<img class="img" alt="Imgur-Upload" src=\"'
             + get_link + '\"/>';
        addImg('.status', content);
    }
};

new Imgur({
    clientid: '91457b1495312a6', 
    callback: feedback
});
