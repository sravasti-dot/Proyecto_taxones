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

if "obras_guardadas" not in st.session_state:
    st.session_state.obras_guardadas = set()   

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0      

if "ultimo_batch_hashes" not in st.session_state:
    st.session_state.ultimo_batch_hashes = set()  

if "rutas_guardadas" not in st.session_state:
    st.session_state.rutas_guardadas = []

with tab1:
     st.write("Sube una imagen del taxón que deseas identificar")
     galeria = st.file_uploader("Elige una imagen...", type=["jpg", "jpeg", "png", "heic"], accept_multiple_files=True, key=f"uploader_{st.session_state.uploader_key}")

     if galeria is not None and len(galeria) <= 4:
         hashes_batch_actual = {hashlib.md5(obra.getvalue()).hexdigest() for obra in galeria} 
         if hashes_batch_actual == st.session_state.ultimo_batch_hashes:
             pass
         else:
          st.session_state.imagen_lista = False
          try:
           huellas_de_esta_tanda = set()
           for obra in galeria:  
             bytes_obra = obra.getvalue()
             resumen_bytes = hashlib.md5(bytes_obra).hexdigest()
             

             if resumen_bytes in st.session_state.obras_guardadas:
                 st.warning(f"La imagen {obra.name} ya ha sido procesada anteriormente.")
                 duplicado = True

             elif resumen_bytes in huellas_de_esta_tanda:
                     st.warning(f"La imagen {obra.name} está repetida dentro de tu selección actual. Elimínala para continuar.")
                     duplicado = True   

             else:
                     huellas_de_esta_tanda.add(resumen_bytes)         
            
           if duplicado:
                st.stop()

           for obra in galeria:
                 resumen_bytes = hashlib.md5(obra.getvalue()).hexdigest()
                 ruta = f"imagen_{resumen_bytes}.jpg"

                 st.session_state.obras_guardadas.add(resumen_bytes)
                 st.image(obra, caption=f"Imagen {obra.name} capturada con éxito", width=90)

                 descarga = Image.open(obra)
                 limpiar_imagen = descarga.convert('RGB')
                 limpiar_imagen.save(ruta)
                 st.session_state.rutas_guardadas.append(ruta)
           st.session_state.ultimo_batch_hashes = hashes_batch_actual
           st.session_state.imagen_lista = True      

          except Exception as e:
             st.error (f"No pudimos procesar el archivo: {e}") 
     else:
         st.error("Por favor, sube un máximo de 4 imágenes.")      

if "camera_key" not in st.session_state:
    st.session_state.camera_key = 0

with tab2:
    st.write("Usa la cámara dedicada de la web app para tomar una foto")

    if len(st.session_state.rutas_guardadas) >= 4:
      st.warning("Ya alcanzaste el máximo de 4 imágenes. Borra alguna para tomar otra.")
    else:
      pixeles = st.camera_input("Tomar una foto desde este dispositivo...", key=f"camera_{st.session_state.camera_key}")

      if pixeles is not None:
        try:
            bytes_foto = pixeles.getvalue()
            huella = hashlib.md5(bytes_foto).hexdigest()

            if huella in st.session_state.obras_guardadas:
                st.warning("Esta foto ya la habías tomado o subido antes.")
            else:
                ruta = f"imagen_{huella}.jpg"

                st.image(pixeles, caption="Imagen capturada con éxito", width=90)
                foto_camara = Image.open(pixeles)
                limpiar_imagen = foto_camara.convert('RGB')
                limpiar_imagen.save(ruta)

                st.session_state.obras_guardadas.add(huella)
                st.session_state.rutas_guardadas.append(ruta)
                st.session_state.imagen_lista = True

                st.session_state.camera_key += 1
                st.rerun()

        except Exception as e:
            st.error(f"No pudimos procesar la foto: {e}")  
    if st.session_state.rutas_guardadas:
     st.subheader("Imágenes listas para procesar:")
     columnas = st.columns(4)
     for i, ruta in enumerate(st.session_state.rutas_guardadas):
        with columnas[i % 4]:
            st.image(ruta, width=90, caption=os.path.basename(ruta))
            if st.button("Borrar", key=f"borrar_{ruta}"):
                huella = ruta.removeprefix("imagen_").removesuffix(".jpg")

                st.session_state.obras_guardadas.discard(huella)
                st.session_state.rutas_guardadas.remove(ruta)

                if os.path.exists(ruta):
                    os.remove(ruta)

                st.session_state.imagen_lista = bool(st.session_state.rutas_guardadas)
                st.rerun()   
         

with col2:
      if st.button("Borrar y empezar de nuevo"):
              st.session_state.obras_guardadas.clear()
              for ruta in st.session_state.rutas_guardadas:
                  if os.path.exists(ruta):
                      os.remove(ruta)
              st.session_state.rutas_guardadas = []
              st.session_state.ultimo_batch_hashes = set()
              st.session_state.imagen_lista = False
              st.session_state.uploader_key = st.session_state.get("uploader_key", 0) + 1
              st.session_state.camera_key = st.session_state.get("camera_key", 0) + 1
              st.rerun()
              

with col1:
 if st.button("Realizar predicción"):
     if st.session_state.imagen_lista and  st.session_state.rutas_guardadas:
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