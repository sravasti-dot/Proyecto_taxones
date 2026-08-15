import streamlit as st
from roboflow import Roboflow
from PIL import Image
import hashlib
import os

st.set_page_config(page_title="Detector de taxones", layout="wide", page_icon="favicon.png")
st.image("mi_portada.png", use_container_width=True)
st.title("Sistema automatizado para la identificación de macroinvertebrados")
st.write("Detección de macroinvertebrados")
rf = Roboflow(api_key="SiR5RA2UDruTVpmqk5jF")
model_roboflow = rf.workspace("angie-oedt9").project("taxones").version(1).model


tab1, tab2 = st.tabs(["Subir archivo", "Cámara dedicada"])
galeria = None
pixeles = None
duplicado = False
col1, col2 = st.columns([6, 1])

if "imagen_lista" not in st.session_state:
     st.session_state.imagen_lista = False

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0    
if "rutas_guardadas" not in st.session_state:  
    st.session_state.rutas_guardadas = []

with tab1:
    st.write("Sube una imagen del taxón que deseas identificar")
    galeria = st.file_uploader("Elige una imagen...", type=["jpg", "jpeg", "png", "heic"], accept_multiple_files=True, key=f"uploader_{st.session_state.uploader_key}")

    if galeria is not None:
         if len(galeria) > 4:
              st.error("Por favor, sube un máximo de 4 imágenes.")
              st.stop()

         st.session_state.imagen_lista = False
         duplicado_encontrado = False
         hashes_lote = set()

         for obra in galeria:
                bytes_obra = obra.getvalue()
                hashlib_obra= hashlib.md5(bytes_obra).hexdigest()

                if (hashlib_obra in hashes_lote):
                    st.warning(f"La imagen '{obra.name}' está repetida dentro de tu selección actual. Elimínala para continuar.")
                    duplicado_encontrado = True
                    break
                hashes_lote.add(hashlib_obra)

         if duplicado_encontrado:
             st.stop()

         try:    
                 for obra in galeria:                      
                    bytes_obra = obra.getvalue()
                    hashlib_obra = hashlib.md5(bytes_obra).hexdigest()
                    ruta = f"imagen_{hashlib_obra}.jpg"
                    st.image(obra, caption=f"Imagen {obra.name} capturada con éxito", width=90)

                    descarga = Image.open(obra)
                    limpiar_imagen = descarga.convert('RGB')
                    limpiar_imagen.save(ruta)
                    st.session_state.rutas_guardadas.append(ruta)     
                 st.session_state.imagen_lista = True
         except Exception as e:
                     st.error(f"No pudimos procesar el archivo: {e}")

with tab2:
     st.write("Usa la cámara dedicada de la web app para tomar una foto")
     pixeles=st.camera_input("Tomar una foto desde este dispositivo...", key=f"camara_{st.session_state.uploader_key}")
     if pixeles is not None:
         bytes_foto = pixeles.getvalue()
         hashlib_foto = hashlib.md5(bytes_foto).hexdigest()
         ruta_foto = f"imagen_{hashlib_foto}.jpg"

         if ruta_foto not in st.session_state.rutas_guardadas:
          if len(st.session_state.rutas_guardadas) >= 4:
                st.error("Ya alcanzaste el máximo de 4 imágenes.")
                st.stop()
         
          st.session_state.imagen_lista = False
          try:
             st.image(pixeles, caption="Imagen capturada con éxito", width=90)
             foto_camara = Image.open(pixeles)
             limpiar_imagen = foto_camara.convert('RGB')
             limpiar_imagen.save(ruta_foto)
             st.session_state.rutas_guardadas.append(ruta_foto)
             st.session_state.imagen_lista = True
          except Exception as e:
             st.error (f"No pudimos procesar la foto: {e}")  

with col2:
      if st.button("Borrar y empezar de nuevo"):
              for ruta in st.session_state.rutas_guardadas:
                  if os.path.exists(ruta):
                      os.remove(ruta)
              st.session_state.imagen_lista = False
              st.session_state.uploader_key = st.session_state.get("uploader_key", 0) + 1
              st.session_state.rutas_guardadas = []
              st.rerun()

with col1:
 if st.button("Realizar predicción"):
     if st.session_state.imagen_lista:
       with st.spinner("Realizando predicción..."):
         for ruta in st.session_state.rutas_guardadas:
          prediccion = model_roboflow.predict(ruta, confidence=70, overlap=30)
          nombre_resultado = f"resultado_{ruta}"
          prediccion.save(nombre_resultado)
          datos = prediccion.json()
          st.image(nombre_resultado, caption="Resultado de la predicción", width=400)
          st.write(f"Macroinvertebrados detectados en {ruta}:")
          if "predictions" in datos and len(datos["predictions"])>0:
             for taxon in datos["predictions"]:
                nombre_taxon= taxon["class"]
                certeza = taxon["confidence"]*100
                st.write(f"**{nombre_taxon}** con una certeza de **{certeza:.2f}%**")
          else:
            st.write("No se detectaron macroinvertebrados en la imagen.")

     else:
         st.warning("Primero sube imágenes válidas antes de predecir.")      