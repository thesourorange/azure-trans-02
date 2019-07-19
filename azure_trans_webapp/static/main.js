/**
 * 
 * Retrieves the Data from Traffic Cameras
 * 
 * 
 */

var map = null;

async function retrieveImages() {

    $('#waitDialog').css('display', 'inline-block');

    try {
         let promise = new Promise((resolve) => {
            
            setTimeout(function() {

                getTrafficImages();

            }, 3000);

        });

        await promise;

    } catch(e) {
        alert(e);
    }

}

async function indentifyImage(id) {

    $('#waitDialog').css('display', 'inline-block');

    try {
         let promise = new Promise((resolve) => {
            
            setTimeout(function() {

                getBoundedImage(id);
                
            }, 3000);

        });

        await promise;

    } catch(e) {
        alert(e);
    }

}

function getTrafficImages() {
    
    var parameters = {format:'JSON'};
    $.get('/retrieve', parameters, function(data) {  
        var result = JSON.parse(data);
        var cards = "";
        var d = new Date();

        for (var feature in result.features) {
           cards += "<div style='padding:10px;'> <div class='card-content' style='position:relative;'>" +
                    `<img id=${result.features[feature].id} src='`+ 
                    `/get?id=${result.features[feature].id}&timestamp=${d.getTime()}` +
                    "' style='width:310px; height:200px; text-align:center;'/> " +
                    "<p> View: " + result.features[feature].properties.view + "</p>" +
                    "<p> Direction: " + result.features[feature].properties.direction + "</p>" +
                    "<p> Region: " + result.features[feature].properties.region + "</p>" +

                        "<div style='position:absolute; bottom:10px; right:50px'>" +
                            "<button id='button' onclick='$(this).Download(\"" +  result.features[feature].id + "\");'>" + 
                                `<img src='${downloadImage}' style='padding-top:2px; width:18px; height:18px; text-align:center;'/> ` +
                             "</button>" +
                        "</div>" +  


                        "<div style='position:absolute; bottom:10px; right:30px'>" +
                            "<button id='button' onclick='$(this).Identify(\"" +  result.features[feature].id + "\");'>" + 
                                `<img src='${boundingBox}' style='padding-top:2px; width:18px; height:18px; text-align:center;'/> ` +
                            "</button>" +
                        "</div>" +  
                        "<div style='position:absolute; bottom:10px; right:10px'>" +
                            "<button id='button' onclick='$(this).Show(\"" + result.features[feature].geometry.coordinates[0] + "\",\"" +  
                                                                             result.features[feature].geometry.coordinates[1] + "\");'>" + 
                                `<img src='${placeHolder}' style='padding-top:2px; width:18px; height:18px; text-align:center;'/> ` +
                            "</button>" +
                         "</div>" +    
  
                    "</div></div>";
         }

        $('#mainbox').html(cards);
        $('#waitDialog').css('display', 'none');
        $('.status').html('<p>Processed - ' + Date().toString() + '</p>');
 
    });  
}

function getBoundedImage(id) {
    var parameters = {id:id};
    $.get('/identify', parameters, function(data) {  
        $("#boxImage").attr("src", `data:image/png;base64,${data}`);
        $('#boxImage').css('display', 'inline-block');
        $('#boxDialog').css('display', 'inline-block');
        $('#waitDialog').css('display', 'none');
    });

}

$.fn.Show = function(long, lat) {
                
    if (map != null) {

        map.off();
        map.remove();
    }
    
    map = L.map('map').setView([lat, long], 40);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 17,
        minZoom: 9,
        noWrap:true
    }).addTo(map);

    setTimeout(function() {
        map.invalidateSize()
        $('#map').css('display', 'inline-block');

    }, 100);

    $('.leaflet-control-attribution').hide();

    $('#mapDialog').css('display', 'inline-block');
  
}

$.fn.Identify = function(id) {

    indentifyImage(id);

}

$.fn.Download = function(id) {
    console.log(`Saving - ${id}.png`);
    var saveLink = document.createElement("a");

    var click = function(node) {
        var event = new MouseEvent("click");

        node.dispatchEvent(event);

    }

    saveLink.href = `/get?id=${id}`;
    saveLink.download = `${id}.png`;
    
    click(saveLink);

}

$(document).ready(function() {

    $('#mapViewerClose').on('click', function(e) {
        $('#mapDialog').css('display', 'none');
    });

    $('#boxViewerClose').on('click', function(e) {
        $('#boxDialog').css('display', 'none');
    });

    
    $('#refresh').on('click', function(e) {
        var parameters = {};

        $('#waitDialog').css('display', 'inline-block');

        $.get('/refresh', parameters, function(data) {
            var date = new Date().getTime();
            var result = JSON.parse(data);

            for (var image in result.images) {
                var id = result.images[image];
                console.log(`Updating: ${image} - ${id}`);
                $(`#${id}`).attr("src", `/get?id=${id}&timestamp=${date}`)
            }

            $('#mainbox').html($('#mainbox').html());
            $('#waitDialog').css('display', 'none');

        } );
    
        return false;

    });

    $('#waitDialog').css('display', 'inline-block');

    retrieveImages();

});
