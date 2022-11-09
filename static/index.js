  data = JSON.parse(document.getElementById("data").innerText);
  console.log(data)
  var items = [];
  string = ""
  $.each( data, function( key, val ) {
      string += `<div class="col">
            <div class="card shadow-sm">
              <img src="data:;base64,${val[1]}" class="card-img-top" width="300" height="400">
              <div class="card-body">
                <p class="card-text">${val[2]}</p>
                <div class="d-flex justify-content-between align-items-center">
                  <form action="/view" method="get">
                    <div class="btn-group">
                      <select hidden name="key">
                        <option value="${key}">${key}</option> 
                      </select>
                      <button name="view" type="submit" class="btn btn-sm btn-outline-secondary">View</button>
                    </div>
                    <small class="text-muted">9 mins</small>
                  </form>
                </div>
              </div>
            </div>
           </div>`
  });
  document.getElementById('objects').innerHTML = string;
