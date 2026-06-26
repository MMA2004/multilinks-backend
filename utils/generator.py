import os
import shutil

BASE_DIR = "/var/www/multilinks"


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






def generar_pagina(data, plantilla="default"):
    base_path = os.path.join(BASE_DIR, "templates", plantilla)
    destino = os.path.join(BASE_DIR, "usuarios", data.get("url", "usuario").replace(" ", "-").lower())

    try:
        if not os.path.exists(base_path):
            print(f"❌ La plantilla '{plantilla}' no existe en: {base_path}")
            return False

        if os.path.exists(destino):
            shutil.rmtree(destino)
        shutil.copytree(base_path, destino)

        index_path = os.path.join(destino, "index.html")
        with open(index_path, "r", encoding="utf-8") as file:
            html = file.read()

        boton_template = '''
        <div class="boton rastreo" data-nombre="{texto}" onclick="window.open('{url}', '_blank')" style="background-color: {bg_color}; color: {text_color}; border: {borde_grosor}px solid {borde_color};">
            <i class="bi {icono}" style="color: {icon_color};"></i>
            <span>{texto}</span>
        </div>'''

        botones_html = "\n".join([
            boton_template.format(
                url=b.get("url", "#"),
                icono=b.get("icono", "bi-link-45deg"),
                texto=b.get("texto", ""),
                bg_color=b.get("bg_color", "white"),
                text_color=b.get("text_color", "#3aabd4"),
                icon_color=b.get("icon_color", "#3aabd4"),
		borde_color=b.get("borde_color", "#000000"),
                borde_grosor=b.get("borde_grosor", "0")
            ) for b in data.get("botones", [])
        ])

        if "titulo" not in data:
            data["titulo"] = ""
        if "subtitulo" not in data:
            data["subtitulo"] = ""

        for clave, valor in data.items():
            if clave != "botones":
                html = html.replace(f"{{{{{clave}}}}}", str(valor))

        if data.get("mostrar_boton_contacto", False):
            contacto_bg = data.get("contacto_bg", "#3aabd4")
            contacto_color = data.get("contacto_color", "white")
            contacto_borde_grosor = data.get("contacto_borde_grosor", "0")
            contacto_borde_color = data.get("contacto_borde_color", "#000000")
            boton_contacto_html = (
                f'<a href="contacto.vcf" download>'
                f'<button style="background-color: {contacto_bg}; color: {contacto_color}; border: {contacto_borde_grosor}px solid {contacto_borde_color};">'
                f'Guardar Contacto</button></a>'
            )
            html = html.replace("{{boton_contacto}}", boton_contacto_html)

            # Generar el archivo .vcf
            generar_vcard(data, destino)
        else:
            html = html.replace("{{boton_contacto}}", "")

        html = html.replace("{{botones}}", botones_html)

        with open(index_path, "w", encoding="utf-8") as file:
            file.write(html)


        print(f"✅ Página generada exitosamente en: {destino}")
        return True

    except Exception as e:
        import traceback
        print("❌ Error:", e)
        traceback.print_exc()
        return False
