import streamlit as st
from roboflow import Roboflow
from PIL import Image
st.set_page_config(page_title="Detector de taxones", layout="wide", page_icon="favicon.png")
st.image("mi_portada.png", use_container_width=True)
st.title("Sistema de monitoreo de macroinvertebrados")
st.write("Sube una foto del taxón que deseas identificar")
rf = Roboflow(api_key="SiR5RA2UDruTVpmqk5jF")
model_roboflow = rf.workspace("angie-oedt9").project("taxones").version(1).model

archivo = st.file_uploader("Elige una imagen...", type=["jpg", "jpeg", "png", "heic"])
activar_camara = st.checkbox("Encender cámara")

archivo = None
pixeles = None

if "imagen_lista" not in st.session_state:
     st.session_state.imagen_lista = False


if archivo is not None:
          st.session_state.imagen_lista = False  
          try:
                st.image(archivo, caption="Imagen capturada con éxito", width=90)
                descarga = Image.open(archivo)
                limpiar_imagen = descarga.convert('RGB')
                limpiar_imagen.save("imagen.jpg")
                st.session_state.imagen_lista = True
          except Exception as e:
              st.error (f"No pudimos procesar el archivo: {e}")  



if activar_camara:
     pixeles=st.camera_input("Tomar una foto desde este dispositivo...")
     if pixeles is not None:
         st.session_state.imagen_lista = False
         try:
             st.image(pixeles, caption="Imagen capturada con éxito", width=90)
             foto_camara = Image.open(pixeles)
             limpiar_imagen = foto_camara.convert('RGB')
             limpiar_imagen.save("imagen.jpg")
             st.session_state.imagen_lista = True
         except Exception as e:
             st.error (f"No pudimos procesar la foto: {e}")  

if st.button("Realizar predicción"):
     if st.session_state.imagen_lista:
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
