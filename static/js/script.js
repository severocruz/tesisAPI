async function upload() {
  const fileInput = document.getElementById("fileInput");
  if (!fileInput.files.length) {
    alert("Selecciona un archivo primero");
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  const res = await fetch("/predict_audio", {
    method: "POST",
    body: formData
  });

  const data = await res.json();
  document.getElementById("resultado").innerText = "Predicción: " + data.nombre+" con un porcentaje de "+(data.porcentaje).toFixed(2)+"%";

  // Mostrar imagen asociada
  const imgGenero = document.getElementById("imagenGenero");
 imgGenero.src = "/static/" + data.imagen;
 console.log('data.nombre', data);
  imgGenero.style.display = "block";
}
