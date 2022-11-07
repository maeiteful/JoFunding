const keys = document.getElementById("main").getAttribute("value");
data = $.getJSON("./static/mydata.json", function ( data ){
    var items = [];
    string = ""
    $.each( data, function( key, val ) {
        if (key === keys){
            string = `
          <img src="data:;base64,${val[1]}" class="card-img-top" width="500" height="700">
            <p class="card-text">${val[2]}</p>
            <p class="card-text"></p>`;
            document.getElementById('test').innerHTML = string;
            document.getElementById('header').innerText = val[0];
        }
    });
    document.getElementById('objects').innerHTML = string;
  });