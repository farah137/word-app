
var mod = document.querySelector("#myModal");
var span = document.getElementsByClassName("close")[0];

async function main(elem) {
  var word = elem.textContent;
    let p = await getDef(word);
    console.log(p);
  document.querySelector("#popuptext").innerHTML =
    "<span class='word'>" + word + "</span>" + "  "
    + "<span class='fl'>" + p[0].fl + "</span>" + "<br><br>" + p[0].shortdef;
}
async function getDef(word) {
      let init = {
          mode: 'cors',
          method: 'GET',
      }
      let resp = await fetch("/defintions/" + word, init);
      return resp.json();
  }
  function popup() {
		mod.style.display = "block";
	}

span.onclick = function() {
 	mod.style.display = "none";
}

window.onclick = function(event) {
	if (event.target == mod) {
   		mod.style.display = "none";
  	}
}
