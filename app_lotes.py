import streamlit as st
from roboflow import Roboflow
from PIL import Image
import hashlib

st.set_page_config(page_title="Detector de taxones", layout="wide", page_icon="favicon.png")
st.image("mi_portada.png", use_container_width=True)
st.title("Sistema automatizado para la identificación de macroinvertebrados")
st.write("Detección de macroinvertebrados")
rf = Roboflow(api_key="SiR5RA2UDruTVpmqk5jF")
model_roboflow = rf.workspace("angie-oedt9").project("taxones").version(1).model

tab1, tab2 = st.tabs(["Subir archivo", "Cámara dedicada"])
archivo = None
pixeles = None

if "imagen_lista" not in st.session_state:
     st.session_state.imagen_lista = False

if "hashes_procesados" not in st.session_state:
    st.session_state.hashes_procesados = set()     

with tab1:
     st.write("Sube una imagen del taxón que deseas identificar")
     archivo = st.file_uploader("Elige una imagen...", type=["jpg", "jpeg", "png", "heic"], accept_multiple_files=True)
     if st.button("Borrar y empezar de nuevo"):
              st.session_state.hashes_procesados.clear()
              st.session_state.imagen_lista = False
              st.rerun()
     if archivo is not None and len(archivo) <= 5:
         st.session_state.imagen_lista = False 

         try:
          hashes_actuales = set()

          for file in archivo:
             
             bytes_archivo = file.read()
             hash_md5 = hashlib.md5(bytes_archivo).hexdigest()

             if hash_md5 in st.session_state.hashes_procesados:
                st.warning(f"⚠️ El archivo '{file.name}' ya fue subido anteriormente.")

             elif hash_md5 in hashes_actuales:
                st.warning(f"⚠️ Estás intentando subir '{file.name}' por duplicado en este grupo.")
             else:
                hashes_actuales.add(hash_md5)
                st.session_state.hashes_procesados.add(hash_md5)

                st.image(file, caption="Se ha capturado con éxito", width=90)
                descarga = Image.open(file)
                limpiar_imagen = descarga.convert('RGB')
                limpiar_imagen.save("imagen.jpg")
                st.session_state.imagen_lista = True
         
         except Exception as e:
             st.error (f"No pudimos procesar el archivo: {e}")  
     else:
        st.error("Por favor, sube un máximo de 5 imágenes.")  


with tab2:
     st.write("Usa la cámara dedicada de la web app para tomar una foto")
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