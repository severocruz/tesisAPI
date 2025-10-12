from typing import Union
from fastapi import FastAPI, Depends, HTTPException
from fastapi import File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import numpy as np
import joblib
from pyAudioAnalysis import ShortTermFeatures
from scipy.io import wavfile
import os
from sqlmodel import create_engine, Field, Session, SQLModel, select
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from crud.generosmusicales import get_all as get_all_generos, create as create_genero
from crud.caracteristicasculturales import get_caracteristicas_by_genero
from crud.instrumentos import get_instrumentos_by_genero
from crud.origenesgeograficos import get_origenes_by_genero
from schemas.generosmusicales import GenerosMusicalesOut
from schemas.instrumentos import  InstrumentosOut
from schemas.origenesgeograficos import OrigenesGeograficosOut
# from crud.generosmusicales import get_by_nombre_prediccion
from fastapi import HTTPException
from schemas.generosmusicales import GenerosMusicalesOut
from crud.generosmusicales import get_by_nombre_prediccion
from schemas.caracteristicasculturales import CaracteristicasCulturalesOut
import models as models
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import noisereduce as nr
import soundfile as sf
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


import pydub
from pydub.utils import which

# Forzar rutas exactas de FFmpeg
pydub.AudioSegment.converter = r"D:\ffmpeg\bin\ffmpeg.exe"
pydub.AudioSegment.ffprobe   = r"D:\ffmpeg\bin\ffprobe.exe"

# Verificar que pydub los reconoce
print("ffmpeg:", which("ffmpeg"))
print("ffprobe:", which("ffprobe"))

from pydub.silence import detect_nonsilent
from pydub import AudioSegment, effects



# Cargar modelo y umbrales
clf = joblib.load("modelo_svm.pkl")
optimal_thresholds = joblib.load("umbrales.pkl")
labels = list(optimal_thresholds.keys())


# url_connection = "mysql+pymysql://root:12345@localhost:3306/db_autoctono"
# engine = create_engine(url_connection)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# creacion de una app de FastAPI
app = FastAPI(title="API de reconocimiento de generos musicales autoctonos")

# Aquí sí usas Jinja2Templates, ya no da warning
templates = Jinja2Templates(directory="templates")
# Montar carpeta "static"
app.mount("/static", StaticFiles(directory="static"), name="static")
# Definir esquema de entrada (features preprocesadas)
class AudioFeatures(BaseModel):
    X_new: list  # lista de listas [[feat1, feat2, ...], ...]

# Función para extraer solo las 8 primeras features
def extraer_8_features(wav_path):
    [Fs, x] = wavfile.read(wav_path)
    
    if x.dtype != np.float32:
        x = x.astype(np.float32)
        x /= np.max(np.abs(x))  # normalizar
    
    features, _ = ShortTermFeatures.feature_extraction(x, Fs, 0.1*Fs, 0.05*Fs)
    
    features_mean = np.mean(features, axis=1)
    
    # Tomar solo las primeras 8 características
    # return features_mean[:8]
    return features_mean[:21]  # Cambiado a 21 para incluir más características
from pydub import AudioSegment, effects
from pydub.silence import detect_nonsilent

def process_audio(file_path: str, output_path: str):
    """
    Normaliza y prepara el audio para el modelo:
    - Mono
    - 16-bit PCM
    - 44.1 kHz
    - Volumen normalizado
    - Recorte de silencios al inicio y final
    """
    audio = AudioSegment.from_file(file_path)

    audio = audio.set_channels(1)
    audio = audio.set_sample_width(2)  # 16 bits PCM
    audio = audio.set_frame_rate(44100)

    audio = effects.normalize(audio)

        # Detectar y recortar silencios
    nonsilent_ranges = detect_nonsilent(audio, min_silence_len=200, silence_thresh=audio.dBFS-16)
    
    # nonsilent_ranges = detect_nonsilent(audio, min_silence_len=200, silence_thresh=-40)
    
    if nonsilent_ranges:
        start = nonsilent_ranges[0][0]
        end = nonsilent_ranges[-1][1]
        # Deja un pequeño margen
        audio = audio[max(0, start-200):min(len(audio), end+200)]
    # === 3. Filtro pasa-altos (100 Hz) ===
    audio = audio.high_pass_filter(100)

    # === 4. Reducción de ruido (usando noisereduce) ===
    samples = np.array(audio.get_array_of_samples()).astype(np.float32)
    samples /= np.max(np.abs(samples))  # normalizar a -1.0 / 1.0
      # === 5. Reducción de ruido ===
    reduced_noise = nr.reduce_noise(y=samples, sr=audio.frame_rate, prop_decrease=0.8)
    # === 6. Normalizar de nuevo antes de guardar ===
    reduced_noise /= np.max(np.abs(reduced_noise))
    # === 5. Guardar como WAV limpio ===
    sf.write(output_path, reduced_noise, audio.frame_rate, subtype="PCM_16")
    # Exportar en formato compatible
    # audio.export(output_path, format="wav")
    

@app.post("/predict_audio", response_model=GenerosMusicalesOut)
async def predict_audio(file: UploadFile = File(...), db: Session = Depends(get_db)):
    tmp_path = f"temp_{file.filename}"
    processed_path = f"processed_{file.filename}"

    with open(tmp_path, "wb") as f:
        f.write(await file.read())
    
    try:

        # Normalizar y procesar el audio
        process_audio(tmp_path, processed_path)
        # Extraer features reducidas
        X_new = extraer_8_features(tmp_path).reshape(1, -1)  # 1 muestra
        # X_new = extraer_8_features(processed_path).reshape(1, -1)
        # Probabilidades
        y_score = clf.predict_proba(X_new)
        
        optimal_thresholds2 = {
            # "atiku": 0.52,
            # "jula": 0.72,
            # "kantus": 0.34,
            # "macheteros": 0.53,
            # "pujllay": 0.93
            "atiku": 0.21,
            "jula": 0.51,
            "kantus": 0.85,
            "macheteros": 0.75,
            "pujllay": 0.10
        }

        labels = list(optimal_thresholds.keys())
        # labels = list(optimal_thresholds.keys()) # Usar las etiquetas del modelo cargado

        # Predicción con umbrales
        candidatos = [labels[i] for i, s in enumerate(y_score[0]) if s >= optimal_thresholds[labels[i]]]
        if candidatos:

            scores_candidatos = [y_score[0][labels.index(c)] for c in candidatos]
            prediccion = candidatos[np.argmax([y_score[0][labels.index(c)] for c in candidatos])]
            porcentaje_prediccion = float(np.max(scores_candidatos))  # <-- porcentaje como float 0-1

            resultado = get_by_nombre_prediccion(db, prediccion)
            
            if resultado:
                resultado.porcentaje = porcentaje_prediccion * 100.0  # Convertir a porcentaje 0-100
                return resultado  #FastAPI lo convierte automáticamente a JSON
            else:
                raise HTTPException(status_code=404, detail="Género no visto")
        else:
            raise HTTPException(status_code=404, detail="Género no visto")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Limpiar archivos temporales
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        if os.path.exists(processed_path):
            os.remove(processed_path)

@app.post("/predict")
def predecir(audio: AudioFeatures):
    X_new = np.array(audio.X_new)
    # Probabilidades
    y_scores = clf.predict_proba(X_new)
     # Predicción con umbrales
    predicciones = []
    for scores in y_scores:
        candidatos = [labels[i] for i, s in enumerate(scores) if s >= optimal_thresholds[labels[i]]]
        if candidatos:
            predicciones.append(candidatos[np.argmax([scores[labels.index(c)] for c in candidatos])])
        else:
            predicciones.append("Género no visto")
    
    return {"predicciones": predicciones}

@app.get("/imagen/{image_name}")
async def get_image(image_name: str):
    try:
        # Verificar si el archivo existe
        file_path = os.path.join("static", image_name)
        if not os.path.isfile(file_path):
            raise HTTPException(status_code=404, detail="Imagen no encontrada")
        return FileResponse("static/"+image_name, media_type="image")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# definicion de una ruta raiz
# @app.get("/")
# def read_root():
#     return {"Hello": "Worldcito"}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# definicion de una ruta con un parametro
@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

# Endpoint para listar todos los géneros
@app.get("/generos/", response_model=list[GenerosMusicalesOut])
def listar_generos(db: Session = Depends(get_db)):
    return get_all_generos(db)

# Endpoint para obtener un género por ID
@app.get("/generos/{genero_id}", response_model=GenerosMusicalesOut)
def obtener_genero(genero_id: int, db: Session = Depends(get_db)):
    genero = db.get(models.GenerosMusicales, genero_id)
    if not genero:
        raise HTTPException(status_code=404, detail="Género no encontrado")
    return genero

# Endpoint para obtener un género por nombre
@app.get("/genero/{name}", response_model=GenerosMusicalesOut)
def obtener_genero_by_name(name: str, db: Session = Depends(get_db)):
    genero =  get_by_nombre_prediccion(db, name) 
    if not genero:
        raise HTTPException(status_code=404, detail="Género no encontrado")
    return genero


#obtener caracteristicas culturales, instrumentos y origenes geograficos por genero
@app.get("/generos/{genero_id}/caracteristicas", response_model=list[CaracteristicasCulturalesOut])
def read_caracteristicas(genero_id: int, db: Session = Depends(get_db)):
    caracteristicas = get_caracteristicas_by_genero(db, genero_id)
    if not caracteristicas:
        raise HTTPException(status_code=404, detail="No se encontraron características para este género")
    return caracteristicas

@app.get("/generos/{genero_id}/instrumentos", response_model=list[InstrumentosOut])
def read_caracteristicas(genero_id: int, db: Session = Depends(get_db)):
    instrumentos = get_instrumentos_by_genero(db, genero_id)
    if not instrumentos:
        raise HTTPException(status_code=404, detail="No se encontraron instrumentos musicales para este género")
    return instrumentos

@app.get("/generos/{genero_id}/ubicaciones", response_model=list[OrigenesGeograficosOut])
def read_caracteristicas(genero_id: int, db: Session = Depends(get_db)):
    ubicaciones = get_origenes_by_genero(db, genero_id)
    if not ubicaciones:
        raise HTTPException(status_code=404, detail="No se encontraron ubicaciones para este género")
    return ubicaciones