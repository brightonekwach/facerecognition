// script.js
document.getElementById("upload-form").addEventListener("submit", function(event) {
    event.preventDefault(); // Prevent default form submission

    // Collect form data
    let formData = new FormData();
    formData.append("student_id", document.getElementById("student-id").value);
    formData.append("name", document.getElementById("name").value);
    formData.append("course", document.getElementById("course").value);
    formData.append("starting_year", document.getElementById("starting-year").value);
    formData.append("total_attendance", document.getElementById("total-attendance").value);
    formData.append("year", document.getElementById("year").value);
    formData.append("last_attendance_time", document.getElementById("last-attendance-time").value);
//    formData.append("image", document.getElementById("image").files[0]);

    // Send form data to server
    fetch("/upload", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        alert("Data uploaded successfully!");
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Error uploading data.");
    });
});
