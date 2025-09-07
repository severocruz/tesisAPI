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
from schemas.generosmusicales import GenerosMusicalesCreate, GenerosMusicalesOut
# from crud.generosmusicales import get_by_nombre_prediccion
from fastapi import HTTPException
from schemas.generosmusicales import GenerosMusicalesOut
from crud.generosmusicales import get_by_nombre_prediccion
import models as models

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
    return features_mean[:8]

# @app.post("/predict_audio")
# async def predict_audio(file: UploadFile = File(...), db: Session = Depends(get_db)):
#     tmp_path = f"temp_{file.filename}"
#     with open(tmp_path, "wb") as f:
#         f.write(await file.read())
    
#     try:
#         # Extraer features reducidas
#         X_new = extraer_8_features(tmp_path).reshape(1, -1)  # 1 muestra
        
#         # Probabilidades
#         y_score = clf.predict_proba(X_new)
        
#         optimal_thresholds2 = {
#             "atiku": 0.90,
#             "jula": 0.95,
#             "kantus": 0.70,
#             "macheteros": 0.70,
#             "pujllay": 0.90
#         }

#         labels = list(optimal_thresholds.keys())
#         # Predicción con umbrales
#         candidatos = [labels[i] for i, s in enumerate(y_score[0]) if s >= optimal_thresholds2[labels[i]]]
#         if candidatos:
#             nombre_prediccion = candidatos[np.argmax([y_score[0][labels.index(c)] for c in candidatos])]
#             resultado = get_by_nombre_prediccion(db, nombre_prediccion)
#             # resultado = nombre_prediccion

#             if resultado:
#                 prediccion = GenerosMusicalesOut.from_orm(resultado)
#             else:
#                 prediccion = "Género no visto"
#         else:
#             prediccion = "Género no visto"
        
#         return JSONResponse(content={"prediccion": prediccion})
    
#     except Exception as e:
#         return JSONResponse(content={"error": str(e)}, status_code=500)
    
#     finally:
#         os.remove(tmp_path)

@app.post("/predict_audio", response_model=GenerosMusicalesOut)
async def predict_audio(file: UploadFile = File(...), db: Session = Depends(get_db)):
    tmp_path = f"temp_{file.filename}"
    with open(tmp_path, "wb") as f:
        f.write(await file.read())
    
    try:
        # Extraer features reducidas
        X_new = extraer_8_features(tmp_path).reshape(1, -1)  # 1 muestra
        
        # Probabilidades
        y_score = clf.predict_proba(X_new)
        
        optimal_thresholds2 = {
            "atiku": 0.61,
            "jula": 0.47,
            "kantus": 0.44,
            "macheteros": 0.61,
            "pujllay": 0.79
            # "atiku": 0.87,
            # "jula": 0.74,
            # "kantus": 0.74,
            # "macheteros": 0.69,
            # "pujllay": 0.95
        }

        labels = list(optimal_thresholds2.keys())

        # Predicción con umbrales
        candidatos = [labels[i] for i, s in enumerate(y_score[0]) if s >= optimal_thresholds2[labels[i]]]
        if candidatos:
            prediccion = candidatos[np.argmax([y_score[0][labels.index(c)] for c in candidatos])]
            resultado = get_by_nombre_prediccion(db, prediccion)
            if resultado:
                return resultado  #FastAPI lo convierte automáticamente a JSON
            else:
                raise HTTPException(status_code=404, detail="Género no visto")
        else:
            raise HTTPException(status_code=404, detail="Género no visto")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
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



