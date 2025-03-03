document
  .getElementById("audioFile")
  .addEventListener("change", function (event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function (e) {
      const audioContext = new (window.AudioContext ||
        window.webkitAudioContext)();
      audioContext.decodeAudioData(e.target.result, function (buffer) {
        drawWaveform(buffer);
      });
    };
    reader.readAsArrayBuffer(file);

    uploadFile(file);
  });

function drawWaveform(buffer) {
  const canvas = document.getElementById("waveform");
  const ctx = canvas.getContext("2d");
  const width = canvas.width;
  const height = canvas.height;
  ctx.clearRect(0, 0, width, height);

  const data = buffer.getChannelData(0);
  const step = Math.ceil(data.length / width);
  const amp = height / 2;

  ctx.beginPath();
  ctx.moveTo(0, amp);
  for (let i = 0; i < width; i++) {
    const min = Math.min(...data.slice(i * step, (i + 1) * step));
    const max = Math.max(...data.slice(i * step, (i + 1) * step));
    ctx.lineTo(i, (1 + min) * amp);
    ctx.lineTo(i, (1 + max) * amp);
  }
  ctx.strokeStyle = "#007bff";
  ctx.stroke();
}

function uploadFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  fetch("http://127.0.0.1:5000/analyze", {
    method: "POST",
    body: formData,
  })

    .then((response) => response.json())
    .then((data) => {
      alert("Hidden message: " + data.message);
    })
    .catch((error) => {
      console.error("Error uploading file:", error);
      alert("Error analyzing file");
    });
}
