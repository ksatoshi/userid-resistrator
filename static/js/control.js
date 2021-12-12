async function onClock() {
    var verify_code = document.getElementById("verify_code").value;
    verify_code = String(verify_code)

    var control_form = document.getElementById("form");
    var xhr = new XMLHttpRequest();

    //verify_codeをハッシュ化する処理
    var hash = await doHash(verify_code);

    alert("hash:" + hash);

    //formデータを作成する処理
    var form = new FormData(control_form);
    form.set('hash', hash);

    //POSTする処理
    xhr.open("POST", "/control/form", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
}

async function doHash(text) {
    const text_utf8 = new TextEncoder().encode(text);
    const hash = await crypto.subtle.digest('SHA-256', text_utf8);

    return hash
}