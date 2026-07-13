import streamlit as st
import sys
from unittest.mock import MagicMock
sys.modules["cv2"] = MagicMock()
from ultralytics import YOLO
from roboflow import Roboflow
from PIL import Image
import os
st.set_page_config(page_title="Detector de taxones", layout="wide", page_icon="favicon.png")
st.image("mi_portada.png", use_container_width=True)
rf = Roboflow(api_key="SiR5RA2UDruTVpmqk5jF")
model_roboflow = rf.workspace("angie-oedt9").project("taxones").version(1).model
st.title("Sistema de monitoreo de macroinvertebrados")
tab1, tab2 = st.tabs(["Subir archivo", "Cámara dedicada"])
imagen_final = None
imagen_lista= False

with tab1:
   st.write("Sube una foto del taxón que deseas identificar")
   archivo = st.file_uploader("Selecciona una imagen...", type=["jpg", "jpeg", "png"], key="uploader1")
   if archivo is not None:
      imagen_final = Image.open(archivo)
      st.image(imagen_final, caption="Imagen cargada con éxito", width=90)
      if imagen_final.mode == "RGBA":
        imagen = imagen_final.convert("RGB")
        ruta_temporal = "temp_image.jpg"
        imagen.save(ruta_temporal)
      imagen_final.save("imagen.jpg")
      imagen_lista= True

with tab2:
   st.write("Usa la cámara dedicada de la web app para tomar una foto...")
   foto_camara = st.camera_input("Tomar una foto desde este dispositivo...", key="camera1") 
   if foto_camara is not None:
      imagen_final = Image.open(foto_camara)
      imagen_final.save("imagen.jpg")
      st.image(imagen_final, caption="Imagen capturada con éxito", width=90)
      imagen_lista=True
if st.button("Realizar predicción"):
    if imagen_lista:
       with st.spinner("Realizando predicción..."):
          prediccion = model_roboflow.predict("imagen.jpg", confidence=70, overlap=30)
          prediccion.save("resultado.jpg")
          if os.path.exists("resultado.jpg"):
              datos = prediccion.json()
              st.image("resultado.jpg", caption="Resultado de la predicción", width=400)
    
         
              st.subheader("Taxones detectados en la muestra:")
              if "predictions" in datos and len(datos["predictions"])>0:
                  for taxon in datos["predictions"]:
                      nombre_taxon= taxon["class"]
                      certeza = taxon["confidence"]*100
                      st.write(f"**{nombre_taxon}** con una certeza de **{certeza:.2f}%**")
              else:
                 st.write("No se detectaron taxones en la imagen.")
          else:
              st.error("Hubo un error al generar la imagen de resultado. Por favor, intenta nuevamente.")      
    else:
         st.warning("Por favor, sube una imagen o toma una foto para realizar la predicción.")