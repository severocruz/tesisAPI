from typing import Union
from fastapi import FastAPI
from fastapi import File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import numpy as np
import joblib
# from pyAudioAnalysis import audioFeatureExtraction as aF
from pyAudioAnalysis import ShortTermFeatures as aF 
#from pyAudioAnalysis.audioFeatureExtraction import stFeatureExtraction as aF
from scipy.io import wavfile
import os

# Cargar modelo y umbrales
clf = joblib.load("modelo_svm.pkl")
optimal_thresholds = joblib.load("umbrales.pkl")
labels = list(optimal_thresholds.keys())
# creacion de una app de FastAPI
app = FastAPI(title="API de reconocimiento de generos musicales autoctonos")

# Definir esquema de entrada (features preprocesadas)
class AudioFeatures(BaseModel):
    X_new: list  # lista de listas [[feat1, feat2, ...], ...]

# Función para extraer solo las 8 primeras features
def extraer_8_features(wav_path):
    [Fs, x] = wavfile.read(wav_path)
    
    if x.dtype != np.float32:
        x = x.astype(np.float32)
        x /= np.max(np.abs(x))  # normalizar
    
    features, _ = aF.stFeatureExtraction(x, Fs, 0.1*Fs, 0.05*Fs)
    
    features_mean = np.mean(features, axis=1)
    
    # Tomar solo las primeras 8 características
    return features_mean[:8]

@app.post("/predict_audio")
async def predict_audio(file: UploadFile = File(...)):
    tmp_path = f"temp_{file.filename}"
    with open(tmp_path, "wb") as f:
        f.write(await file.read())
    
    try:
        # Extraer features reducidas
        X_new = extraer_8_features(tmp_path).reshape(1, -1)  # 1 muestra
        
        # Probabilidades
        y_score = clf.predict_proba(X_new)
        
        # Predicción con umbrales
        candidatos = [labels[i] for i, s in enumerate(y_score[0]) if s >= optimal_thresholds[labels[i]]]
        if candidatos:
            prediccion = candidatos[np.argmax([y_score[0][labels.index(c)] for c in candidatos])]
        else:
            prediccion = "Género no visto"
        
        return JSONResponse(content={"prediccion": prediccion})
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
    finally:
        os.remove(tmp_path)

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


# definicion de una ruta raiz
@app.get("/")
def read_root():
    return {"Hello": "Worldcito"}

# definicion de una ruta con un parametro
@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
