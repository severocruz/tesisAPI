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
        // console.log('data', data)
        mostrarDatosGenero(data); // Cargar características e instrumentos del género predicho  
    } catch (err) {
        // alert("Error al procesar el archivo.");
        renderErrorCard()
        // console.error(err);
    } finally {
        // Ocultar loader y reactivar botón
        loader.style.display = "none";
        uploadBtn.disabled = false;
        uploadBtn.textContent = "Subir y predecir";
    }
}

function renderResultCard(data) {
    // console.log('data', data);
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
    // Scroll hacia la card
    container.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function renderErrorCard() {
    // console.log('data', data);
    const container = document.getElementById("resultadoContainer");
    container.innerHTML = `
        <div class="card fade-in">
            <div class="image-container">
                <img src="/static/advertencia.png">
            </div>
            <div class="card-content">
            <h2 class="subtitle">Predicción: Sin Predicción</h2>
            <h1 class="title">Desconocido</h1>
                <p class="description">No se reconoce el género o no esta incluido en el dataset</p>
                
            </div>
        </div>
    `;
    const contenedor = document.getElementById("caracteristicas-container");
    contenedor.innerHTML = "<p>Sin datos</p>";
    const contenedor2 = document.getElementById("instrumentos-container");
    contenedor2.innerHTML = "<p>Sin datos</p>";
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

const API_BASE = "http://127.0.0.1:8080"; // tu base URL

async function cargarCaracteristicas(generoId) {
  const contenedor = document.getElementById("caracteristicas-container");
  contenedor.innerHTML = "<p>Cargando características...</p>";

  try {
    const resp = await fetch(`/generos/${generoId}/caracteristicas`);
    if (!resp.ok) throw new Error("Error al obtener características");
    const data = await resp.json();

    contenedor.innerHTML = "";
    data.forEach(item => {
      const card = document.createElement("div");
      card.classList.add("card2");
      card.innerHTML = `
        <img src="/static/${item.imagen}" alt="${item.nombre}">
        <div class="card-content">
          <h3>${item.nombre}</h3>
          <p>${item.descripcion}</p>
        </div>
      `;
      contenedor.appendChild(card);
    });
  } catch (err) {
    contenedor.innerHTML = `<p style="color:red;">Error: ${err.message}</p>`;
  }
}

async function cargarInstrumentos(generoId) {
  const contenedor = document.getElementById("instrumentos-container");
  contenedor.innerHTML = "<p>Cargando instrumentos...</p>";

  try {
    const resp = await fetch(`/generos/${generoId}/instrumentos`);
    if (!resp.ok) throw new Error("Error al obtener instrumentos");
    const data = await resp.json();

    contenedor.innerHTML = "";
    data.forEach(item => {
      const card = document.createElement("div");
      card.classList.add("card2");
      card.innerHTML = `
        <img src="static/${item.imagen}" alt="${item.nombre}">
        <div class="card-content">
          <h3>${item.nombre}</h3>
          <p>${item.tipo}</p>
          <p>${item.descripcion}</p>
        </div>
      `;
      contenedor.appendChild(card);
    });
  } catch (err) {
    contenedor.innerHTML = `<p style="color:red;">Error: ${err.message}</p>`;
  }
}

// ejemplo: llama estas funciones cuando tengas el id del género
// por ejemplo, tras la predicción:
function mostrarDatosGenero(prediccion) {
  const generoId = prediccion.id || 1; // ejemplo
  cargarCaracteristicas(generoId);
  cargarInstrumentos(generoId);
}

