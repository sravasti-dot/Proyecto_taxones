import streamlit as st
from ultralytics import YOLO
from roboflow import Roboflow
from PIL import Image
st.set_page_config(page_title="Detector de taxones", layout="wide", page_icon="favicon.png")
st.image("mi_portada.png", use_container_width=True)
st.title("Sistema de monitoreo de macroinvertebrados")
st.write("Sube una foto del taxón que deseas identificar")
rf = Roboflow(api_key="SiR5RA2UDruTVpmqk5jF")
model_roboflow = rf.workspace("angie-oedt9").project("taxones").version(1).model
espacio= st.empty()
archivo = st.file_uploader("Elige una imagen...", type=["jpg", "jpeg", "png"])
activar_camara = st.checkbox("Encender cámara")
foto_camara = None
imagen_lista = False

if archivo is not None:
   imagen = Image.open(archivo)
   imagen.thumbnail((800, 800))
   with espacio:
      espacio=st.columns([1, 7])
   st.image(imagen, caption="Imagen cargada con éxito", width=90)
   if imagen.mode == "RGBA":
        imagen = imagen.convert("RGB")
        ruta_temporal = "temp_image.jpg"
        imagen.save(ruta_temporal)
   imagen.save("imagen.jpg")
   imagen_lista= True
if activar_camara:
   foto_camara=st.camera_input("Tomar una foto desde este dispositivo")
   if foto_camara is not None:
       imagen = Image.open(foto_camara)
       st.image(imagen, caption="Imagen capturada con éxito", width=90)
       imagen.save("imagen.jpg")
       imagen_lista= True
if st.button("Realizar predicción"):
   if imagen_lista:
       with st.spinner("Realizando predicción..."):
          prediccion = model_roboflow.predict("imagen.jpg", confidence=70, overlap=30)
          prediccion.save("resultado.jpg")
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
