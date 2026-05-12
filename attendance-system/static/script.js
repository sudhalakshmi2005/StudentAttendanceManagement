function validateForm() {
    let user = document.getElementById("username").value;
    let pwd = document.getElementById("password").value;
    let mac = document.getElementById("mac").value;

    if (user === "" || pwd === "" || mac === "") {
        alert("All fields are required!");
        return false;
    }
    return true;
}

// Generate fake MAC (for demo)
function generateMAC() {
    let mac = "AA:BB:CC:" + Math.floor(Math.random() * 100);
    document.getElementById("mac").value = mac;
}