const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("audioFile");
const uploadBtn = document.getElementById("uploadBtn");
const dropText = document.getElementById("dropText");

dropZone.addEventListener("click", () => fileInput.click());

dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("dragover");
});

dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
    if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        dropText.textContent = `Archivo listo: ${fileInput.files[0].name}`;
    }
});

fileInput.addEventListener("change", () => {
    if (fileInput.files.length) {
        dropText.textContent = `Archivo listo: ${fileInput.files[0].name}`;
    } else {
        dropText.textContent = "Arrastra tu archivo aquí";
    }
});

uploadBtn.addEventListener("click", uploadAudio);

async function uploadAudio() {
    if (!fileInput.files.length) return alert("Selecciona un archivo WAV");

    const loader = document.getElementById("loader");
    loader.style.display = "block";

    // Desactivar botón mientras predice
    uploadBtn.disabled = true;
    uploadBtn.textContent = "Prediciendo...";

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {
        const res = await fetch("/predict_audio", {
            method: "POST",
            body: formData
        });
        const data = await res.json();
        renderResultCard(data);
    } catch (err) {
        alert("Error al procesar el archivo.");
        console.error(err);
    } finally {
        // Ocultar loader y reactivar botón
        loader.style.display = "none";
        uploadBtn.disabled = false;
        uploadBtn.textContent = "Subir y predecir";
    }
}

function renderResultCard(data) {
    const container = document.getElementById("resultadoContainer");
    container.innerHTML = `
        <div class="card fade-in">
            <div class="image-container">
                <img src="/static/${data.imagen}" alt="${data.nombre}">
            </div>
            <div class="card-content">
            <h2 class="subtitle">Predicción: ${capitalize(data.nombre_prediccion)}</h2>
            <p class="confidence">Confianza: ${data.porcentaje.toFixed(2)}%</p>
            <h1 class="title">${data.nombre}</h1>
                <p class="description">${data.descripcion}</p>
                <div class="video">
                    <a href="${data.video_link}" target="_blank"> Ver video relacionado</a>
                </div>
                
            </div>
        </div>
    `;
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}
