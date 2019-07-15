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

async function indentifyImage(url) {

    $('#waitDialog').css('display', 'inline-block');

    try {
         let promise = new Promise((resolve) => {
            
            setTimeout(function() {

                getBoundedImage(url);
                
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

         for (var feature in result.features) {
           cards += "<div style='padding:10px;'> <div class='card-content' style='position:relative;'><img src='" + 
                    result.features[feature].properties.href + "?" + Date().toString() +
                    "' style='width:310px; height:200px; text-align:center;'/> " +
                    "<p> View: " + result.features[feature].properties.view + "</p>" +
                    "<p> Direction: " + result.features[feature].properties.direction + "</p>" +
                    "<p> Region: " + result.features[feature].properties.region + "</p>" +
                        "<div style='position:absolute; bottom:10px; right:30px'>" +
                            "<button id='button' onclick='$(this).Identify(\"" +  result.features[feature].properties.href + "\");'>" + 
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

function getBoundedImage(url) {
    var parameters = {url:url};
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

$.fn.Identify = function(url) {

    indentifyImage(url);

}

$(document).ready(function() {

    $('#mapViewerClose').on('click', function(e) {
        $('#mapDialog').css('display', 'none');
    });

    $('#boxViewerClose').on('click', function(e) {
        $('#boxDialog').css('display', 'none');
    });

    $('#waitDialog').css('display', 'inline-block');
    
    retrieveImages();

});

$('#retrieve').on('click', function(e) {

    retrieveImages();

    return false;

});
