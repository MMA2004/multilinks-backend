import os
import shutil
from config import TEMPLATES_DIR, USUARIOS_DIR
def generar_vcard(data, destino):
    nombre = data.get("nombre", "Contacto")
    telefono = data.get("telefono", "")
    correo = data.get("correo", "")
    nota = data.get("nota", "")

    vcard = "BEGIN:VCARD\r\nVERSION:3.0\r\n"
    vcard += f"FN:{nombre}\r\n"
    vcard += f"TEL:{telefono}\r\n"
    if correo:
        vcard += f"EMAIL;type=work:{correo.lower()}\r\n"
    if nota:
        vcard += f"NOTE:{nota}\r\n"
    vcard += "END:VCARD\r\n"

    vcf_path = os.path.join(destino, "contacto.vcf")
    with open(vcf_path, "w", encoding="utf-8") as f:
        f.write(vcard)






def generar_pagina(data, plantilla=None):
    if plantilla is None:
        plantilla = data.get("plantilla", "plantilla_comercial")
        
    base_path = os.path.join(TEMPLATES_DIR, plantilla)
    
    # Si la plantilla no existe (porque fue eliminada o renombrada), forzar plantilla_comercial
    if not os.path.exists(base_path):
        print(f"Advertencia: La plantilla '{plantilla}' no existe. Usando 'plantilla_comercial' por defecto.")
        plantilla = "plantilla_comercial"
        base_path = os.path.join(TEMPLATES_DIR, plantilla)

    destino = os.path.join(USUARIOS_DIR, data.get("url", "usuario").replace(" ", "-").lower())

    try:
        if not os.path.exists(base_path):
            print(f"Error Crítico: Ni siquiera la plantilla por defecto '{plantilla}' existe en: {base_path}")
            return False

        if os.path.exists(destino):
            shutil.rmtree(destino)
        shutil.copytree(base_path, destino)

        index_path = os.path.join(destino, "index.html")
        with open(index_path, "r", encoding="utf-8") as file:
            html = file.read()

        # Templates de bloques
        boton_template = '''
        <div class="boton rastreo" data-nombre="{texto}" onclick="window.open('{url}', '_blank')" style="{extra_style} color: {text_color}; margin-bottom: 15px;">
            {icono_html}
            <span>{texto}</span>
        </div>'''
        
        boton_circular_template = '''
        <div class="boton rastreo" data-nombre="{texto}" onclick="window.open('{url}', '_blank')" style="display: inline-flex; justify-content: center; align-items: center; width: 65px; height: 65px; border-radius: 50%; {extra_style} color: {text_color}; margin: 10px 8px; cursor: pointer;">
            <i class="bi {icono}" style="color: {icon_color}; font-size: 30px; margin: 0; position: static;"></i>
        </div>'''
        
        youtube_template = '''
        <div class="video-container" style="margin: 0 auto 15px auto; border-radius: {borde_grosor}px; overflow: hidden; border: {borde_grosor}px solid {borde_color}; width: {ancho_video}%; aspect-ratio: 16/9;">
            <iframe width="100%" height="100%" src="{url}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
        </div>'''
        
        mapa_template = '''
        <div class="mapa-container" style="margin: 0 auto 15px auto; border-radius: {borde_grosor}px; overflow: hidden; border: {borde_grosor}px solid {borde_color}; width: {ancho}%; height: {alto}px;">
            <iframe width="100%" height="100%" src="{url}" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
        </div>'''
        
        texto_template = '''
        <div class="texto-bloque" style="margin-bottom: 15px; text-align: {alineacion}; color: {text_color}; font-size: {tamano};">
            {contenido}
        </div>'''
        
        seccion_template = '''
        <div class="seccion-bloque" style="margin-bottom: 15px; text-align: left; color: {text_color}; font-size: 18px; font-weight: bold; border-bottom: 2px solid {borde_color}; padding-bottom: 5px;">
            {contenido}
        </div>'''
        
        imagen_template = '''
        <div class="imagen-bloque" style="margin-bottom: 15px; text-align: center;">
            <img src="{url}" alt="Imagen extra" style="max-width: 100%; border-radius: {borde_grosor}px; border: {borde_grosor}px solid {borde_color};">
        </div>'''

        boton_imagen_texto_template = '''
        <div class="boton-imagen-texto rastreo" data-nombre="{texto}" onclick="window.open('{url}', '_blank')" style="{extra_style} color: {text_color};">
            <img src="{imagen_url}" alt="{texto}" class="boton-imagen-texto-img">
            <div class="boton-imagen-texto-contenido">{texto}</div>
        </div>'''

        bloques_html = []
        for b in data.get("botones", []):
            tipo_original = b.get("tipo", "enlace")
            
            # Mapear los tipos que realmente son botones/enlaces
            if tipo_original in ["enlace", "normal", "whatsapp", "correo", "ResFormulario", ""]:
                tipo = "enlace"
            else:
                tipo = tipo_original
            
            if tipo == "enlace":
                forma = b.get("forma", "rectangular")
                is_glass = b.get("glassmorphism", False)
                if is_glass:
                    extra_style = f"background-color: color-mix(in srgb, {b.get('bg_color', 'white')} 25%, transparent); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); box-shadow: 0 8px 32px 0 rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.4);"
                else:
                    extra_style = f"background-color: {b.get('bg_color', 'white')}; border: {b.get('borde_grosor', '0')}px solid {b.get('borde_color', '#000000')};"

                if forma == "circular":
                    bloques_html.append(boton_circular_template.format(
                        url=b.get("url", "#"),
                        icono=b.get("icono", "bi-link-45deg"),
                        texto=b.get("texto", "Red Social"),
                        text_color=b.get("text_color", "#3aabd4"),
                        icon_color=b.get("icon_color", "#3aabd4"),
                        extra_style=extra_style
                    ))
                else:
                    icono_html = f'<i class="bi {b.get("icono")}" style="color: {b.get("icon_color", "#3aabd4")};"></i>' if b.get("icono") else ""
                    bloques_html.append(boton_template.format(
                        texto=b.get("texto", "Botón"),
                        url=b.get("url", "#"),
                        icono_html=icono_html,
                        text_color=b.get("text_color", "#3aabd4"),
                        extra_style=extra_style
                    ))
            elif tipo == "youtube":
                # Convertir URL normal a URL de embed si es necesario
                yt_url = b.get("url", "")
                if "watch?v=" in yt_url:
                    yt_url = yt_url.replace("watch?v=", "embed/")
                elif "youtu.be/" in yt_url:
                    yt_url = yt_url.replace("youtu.be/", "youtube.com/embed/")
                    
                bloques_html.append(youtube_template.format(
                    url=yt_url,
                    borde_color=b.get("borde_color", "transparent"),
                    borde_grosor=b.get("borde_grosor", "0"),
                    ancho_video=b.get("ancho_video", "100")
                ))
            elif tipo == "mapa":
                # Convertir iframe HTML a URL si es necesario
                map_url = b.get("url", "")
                if "<iframe" in map_url:
                    import re
                    match = re.search(r'src="([^"]+)"', map_url)
                    if match:
                        map_url = match.group(1)
                
                bloques_html.append(mapa_template.format(
                    url=map_url,
                    borde_color=b.get("borde_color", "transparent"),
                    borde_grosor=b.get("borde_grosor", "0"),
                    ancho=b.get("ancho_video", "100"),
                    alto=b.get("alto_mapa", "300")
                ))
            elif tipo == "texto":
                bloques_html.append(texto_template.format(
                    contenido=b.get("texto", ""),
                    alineacion=b.get("alineacion", "center"),
                    text_color=b.get("text_color", "#000000"),
                    tamano=b.get("tamano", "16px")
                ))
            elif tipo == "seccion":
                bloques_html.append(seccion_template.format(
                    contenido=b.get("texto", ""),
                    text_color=b.get("text_color", "#ffffff"),
                    borde_color=b.get("borde_color", "#ffffff")
                ))
            elif tipo == "imagen":
                bloques_html.append(imagen_template.format(
                    url=b.get("url", ""),
                    borde_color=b.get("borde_color", "transparent"),
                    borde_grosor=b.get("borde_grosor", "0")
                ))
            elif tipo == "boton_imagen_texto":
                is_glass = b.get("glassmorphism", False)
                if is_glass:
                    extra_style = f"background-color: color-mix(in srgb, {b.get('bg_color', 'white')} 25%, transparent); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); box-shadow: 0 8px 32px 0 rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.4);"
                else:
                    extra_style = f"background-color: {b.get('bg_color', 'white')}; border: {b.get('borde_grosor', '0')}px solid {b.get('borde_color', '#000000')};"

                bloques_html.append(boton_imagen_texto_template.format(
                    texto=b.get("texto", "Botón Img + Texto"),
                    url=b.get("url", "#"),
                    imagen_url=b.get("imagen_url", ""),
                    text_color=b.get("text_color", "#000000"),
                    extra_style=extra_style
                ))

        botones_html = "\n".join(bloques_html)

        if "titulo" not in data:
            data["titulo"] = ""
        if "subtitulo" not in data:
            data["subtitulo"] = ""
            
        if data.get("imagen_fondo"):
            data["fondo"] = f"url('{data['imagen_fondo']}') fixed center / cover"

        for clave, valor in data.items():
            if clave != "botones":
                html = html.replace(f"{{{{{clave}}}}}", str(valor))

        if data.get("mostrar_boton_contacto", False):
            contacto_bg = data.get("contacto_bg", "#3aabd4")
            contacto_color = data.get("contacto_color", "white")
            contacto_borde_grosor = data.get("contacto_borde_grosor", "0")
            contacto_borde_color = data.get("contacto_borde_color", "#000000")
            contacto_glass = data.get("contacto_glassmorphism", False)
            
            if contacto_glass:
                contacto_style = f"background-color: color-mix(in srgb, {contacto_bg} 25%, transparent); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); box-shadow: 0 8px 32px 0 rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.4);"
            else:
                contacto_style = f"background-color: {contacto_bg}; border: {contacto_borde_grosor}px solid {contacto_borde_color};"
                
            boton_contacto_html = (
                f'<a href="contacto.vcf" download>'
                f'<button style="{contacto_style} color: {contacto_color};">'
                f'Guardar Contacto</button></a>'
            )
            html = html.replace("{{boton_contacto}}", boton_contacto_html)

            # Generar el archivo .vcf
            generar_vcard(data, destino)
        else:
            html = html.replace("{{boton_contacto}}", "")

        html = html.replace("{{botones}}", botones_html)

        # Prevenir caché en el CSS
        import time
        html = html.replace('href="styles.css"', f'href="styles.css?v={int(time.time())}"')

        with open(index_path, "w", encoding="utf-8") as file:
            file.write(html)


        print(f"Pagina generada exitosamente en: {destino}")
        return True

    except Exception as e:
        import traceback
        with open("error_log.txt", "w") as f:
            f.write(traceback.format_exc())
        print("Error:", e)
        traceback.print_exc()
        return False
