function switchLanguage(lang) {
    let data = new FormData()
    data.append("lang", lang)
    fetch("/switch_lang", {
        "method": "POST",
        "body": data,
    }).then(response => {
        if (response.status === 200) {
            return response.json();
        } else {
            // handle this somehow
        }
    }).then(json => {
        let rb = document.getElementById("rb_" + lang)
        rb.checked = true;
        loadControlPanel(json, "", g_lang=lang);
        console.log('Success! ')
    }).catch(error => {
        console.log('error with access token req!')
    })
    return true;
}

function disableOption(elem, auth_msg, clr = "rgba(0, 0, 0, 0.6)") {
    let maskTxt = `<div class="mask" style="background-color: ${clr}">\n` +
        "<div class=\"d-flex justify-content-center align-items-center h-100\">\n" +
        `<p class=\"text-white mb-0\">${auth_msg}</p>` +
        "</div></div>"
    let container = document.getElementById(elem.id);
    if (!container) {
        console.log("Didn't find the container")
        return false;
    }

    container.innerHTML = elem.html + maskTxt;

    let a_elem = document.getElementById("a_" + elem.id);
    a_elem.classList.add("disabled");

}