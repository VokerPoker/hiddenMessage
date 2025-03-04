function uploadFile() {
  const fileInput = document.getElementById("audioFile");
  if (!fileInput.files.length) {
    alert("Please select a file first.");
    return;
  }

  const file = fileInput.files[0];
  const formData = new FormData();
  formData.append("file", file);

  fetch("/analyze", {
    method: "POST",
    body: formData,
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      document.getElementById("message").textContent =
        "Hidden message: " + data.message;
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("Error analyzing file");
    });
}
