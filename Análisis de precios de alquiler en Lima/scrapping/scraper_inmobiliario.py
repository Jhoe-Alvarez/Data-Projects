from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import pandas as pd # Importamos pandas para crear nuestra tabla tipo Excel
import importlib
import os
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse
try:
    uc = importlib.import_module("undetected_chromedriver")
except ImportError:
    uc = None




BASE_URL = "https://urbania.pe/buscar/alquiler-de-casas-o-departamentos-o-casas-condominio-o-condominio-de-edificios-en-lima"
N_PAGINAS = max(1, int(os.getenv("N_PAGINAS", "50")))
TIPO_CAMBIO_USD_PEN = float(os.getenv("TC_USD_PEN", "3.80"))
EXTRAER_MANTENIMIENTO_DETALLE = os.getenv("EXTRAER_MANTENIMIENTO_DETALLE", "1") == "1"
MAX_URLS_DETALLE = max(0, int(os.getenv("MAX_URLS_DETALLE", "0")))


def construir_url_pagina(base_url, numero_pagina):
    """Construye la URL de resultados para una pagina especifica."""
    if numero_pagina <= 1:
        return base_url

    url_parseada = urlparse(base_url)
    query = parse_qs(url_parseada.query)
    query["n_pg"] = [str(numero_pagina)]
    query_codificada = urlencode(query, doseq=True)
    return urlunparse(url_parseada._replace(query=query_codificada))


def extraer_texto_con_selectores(elemento, xpaths, valor_por_defecto):
    """Intenta extraer texto usando varios selectores XPath posibles."""
    for xpath in xpaths:
        try:
            texto = elemento.find_element(By.XPATH, xpath).text.strip()
            if texto:
                return texto
        except Exception:
            continue
    return valor_por_defecto


def extraer_lista_textos_con_selectores(elemento, xpaths, valor_por_defecto):
    """Extrae varios textos y los concatena para campos con multiples etiquetas."""
    for xpath in xpaths:
        try:
            nodos = elemento.find_elements(By.XPATH, xpath)
            textos = [nodo.text.strip() for nodo in nodos if nodo.text and nodo.text.strip()]
            if textos:
                # Conserva orden y evita duplicados repetidos.
                textos_unicos = list(dict.fromkeys(textos))
                return " | ".join(textos_unicos)
        except Exception:
            continue
    return valor_por_defecto


def extraer_url_anuncio(tarjeta, valor_por_defecto=""):
    """Extrae el enlace del anuncio desde la tarjeta."""
    xpaths = [
        ".//h2[@data-qa='POSTING_CARD_DESCRIPTION']//a",
        ".//a[contains(@href, '/inmueble/')]",
    ]
    for xpath in xpaths:
        try:
            enlace = tarjeta.find_element(By.XPATH, xpath).get_attribute("href")
            if enlace:
                return enlace.strip()
        except Exception:
            continue
    return valor_por_defecto


def limpiar_numero(texto_numero):
    """Convierte textos numericos con separadores de miles a float."""
    if not texto_numero:
        return None
    solo = re.sub(r"[^\d.,]", "", texto_numero)
    if not solo:
        return None
    if "," in solo and "." in solo:
        if solo.rfind(",") > solo.rfind("."):
            solo = solo.replace(".", "").replace(",", ".")
        else:
            solo = solo.replace(",", "")
    elif "," in solo:
        if solo.count(",") == 1 and len(solo.split(",")[-1]) <= 2:
            solo = solo.replace(",", ".")
        else:
            solo = solo.replace(",", "")
    try:
        return float(solo)
    except ValueError:
        return None


def extraer_distrito(ubicacion):
    """Devuelve un distrito limpio a partir de la ubicacion cruda."""
    if not ubicacion or ubicacion == "Sin ubicación":
        return "Sin distrito"

    candidatos = [parte.strip() for parte in ubicacion.split(",") if parte.strip()]
    if not candidatos:
        return "Sin distrito"

    ultimo = candidatos[-1].lower()
    if ultimo in {"lima", "peru", "perú"} and len(candidatos) > 1:
        return candidatos[-2]
    return candidatos[-1]


def extraer_precio_info(precio_texto):
    """Extrae precio original, moneda y precio en soles."""
    if not precio_texto or precio_texto == "Sin precio":
        return precio_texto, "N/A", None

    precio_limpio = " ".join(precio_texto.split())

    match_soles = re.search(r"S/\s*([\d.,]+)", precio_limpio, flags=re.IGNORECASE)
    if match_soles:
        monto = limpiar_numero(match_soles.group(1))
        return precio_limpio, "PEN", monto

    match_usd = re.search(r"(?:USD|US\$|\$)\s*([\d.,]+)", precio_limpio, flags=re.IGNORECASE)
    if match_usd:
        monto_usd = limpiar_numero(match_usd.group(1))
        precio_soles = round(monto_usd * TIPO_CAMBIO_USD_PEN, 2) if monto_usd is not None else None
        return precio_limpio, "USD", precio_soles

    monto = limpiar_numero(precio_limpio)
    return precio_limpio, "N/A", monto


def extraer_m2(texto_fuente):
    """Extrae metraje total aproximado."""
    if not texto_fuente:
        return None
    match = re.search(r"(\d+[\d.,]*)\s*m²", texto_fuente, flags=re.IGNORECASE)
    if not match:
        match = re.search(r"(\d+[\d.,]*)\s*m2", texto_fuente, flags=re.IGNORECASE)
    valor = limpiar_numero(match.group(1)) if match else None
    return int(round(valor)) if valor is not None else None


def extraer_dormitorios(texto_fuente):
    """Extrae cantidad de dormitorios."""
    if not texto_fuente:
        return None
    match = re.search(r"(\d+)\s*dorm", texto_fuente, flags=re.IGNORECASE)
    if not match:
        match = re.search(r"(\d+)\s*habitaci", texto_fuente, flags=re.IGNORECASE)
    return int(match.group(1)) if match else None


def extraer_banos(texto_fuente):
    """Extrae cantidad de banos."""
    if not texto_fuente:
        return None
    match = re.search(r"(\d+)\s*bañ", texto_fuente, flags=re.IGNORECASE)
    if not match:
        match = re.search(r"(\d+)\s*ban", normalizar_para_busqueda(texto_fuente), flags=re.IGNORECASE)
    return int(match.group(1)) if match else None


def extraer_cocheras(texto_fuente):
    """Extrae cantidad de cocheras/estacionamientos."""
    if not texto_fuente:
        return None
    match = re.search(r"\b(\d{1,2})\s*estac\b", texto_fuente, flags=re.IGNORECASE)
    if not match:
        match = re.search(r"\b(\d{1,2})\s*coch", texto_fuente, flags=re.IGNORECASE)
    if not match:
        return None
    valor = int(match.group(1))
    # Filtro de sanidad: en residencial, mas de 10 cocheras suele ser error de parseo.
    return valor if valor <= 10 else None


def extraer_mantenimiento(tarjeta):
    """Extrae mantenimiento solo cuando el texto lo indica de forma explicita."""
    if tarjeta is None:
        return None

    candidatos = []
    xpaths = [
        ".//*[contains(translate(normalize-space(.), 'MANTENIMIENTO', 'mantenimiento'), 'mantenimiento')]",
        ".//*[contains(translate(normalize-space(.), 'MANTEN.', 'manten.'), 'manten')]",
    ]
    for xpath in xpaths:
        try:
            nodos = tarjeta.find_elements(By.XPATH, xpath)
            for nodo in nodos:
                txt = " ".join((nodo.text or "").split())
                if txt and txt not in candidatos and len(txt) <= 120:
                    candidatos.append(txt)
        except Exception:
            continue

    for texto in candidatos:
        patron_1 = re.search(r"(?:mantenimiento|manten\.?)[^\d]*(S/|USD|US\$|\$)\s*([\d.,]+)", texto, flags=re.IGNORECASE)
        patron_2 = re.search(r"\+\s*(S/|USD|US\$|\$)\s*([\d.,]+)\s*(?:de\s*)?(?:mantenimiento|manten\.?)", texto, flags=re.IGNORECASE)
        patron_3 = re.search(r"(?:mantenimiento|manten\.?)\s*[:\-]?\s*([\d.,]+)", texto, flags=re.IGNORECASE)
        match = patron_1 or patron_2 or patron_3
        if not match:
            continue

        if match.lastindex == 2:
            moneda = (match.group(1) or "S/").upper()
            monto = limpiar_numero(match.group(2))
        else:
            moneda = "S/"
            monto = limpiar_numero(match.group(1))

        if monto is None:
            continue
        if moneda in {"USD", "US$", "$"}:
            monto = round(monto * TIPO_CAMBIO_USD_PEN, 2)

        # Filtro de sanidad para evitar confundir metraje u otros campos con mantenimiento.
        if 10 <= monto <= 5000:
            return monto

    return None


def extraer_mantenimiento_desde_texto(texto):
    """Extrae monto de mantenimiento desde texto libre."""
    if not texto:
        return None

    texto_limpio = " ".join(texto.split())
    patrones = [
        r"(?:mantenimiento|manten\.?)[^\d]*(S/|USD|US\$|\$)\s*([\d.,]+)",
        r"\+\s*(S/|USD|US\$|\$)\s*([\d.,]+)\s*(?:de\s*)?(?:mantenimiento|manten\.?)",
        r"(?:mantenimiento|manten\.?)\s*[:\-]?\s*([\d.,]+)",
    ]

    for patron in patrones:
        match = re.search(patron, texto_limpio, flags=re.IGNORECASE)
        if not match:
            continue

        if match.lastindex == 2:
            moneda = (match.group(1) or "S/").upper()
            monto = limpiar_numero(match.group(2))
        else:
            moneda = "S/"
            monto = limpiar_numero(match.group(1))

        if monto is None:
            continue
        if moneda in {"USD", "US$", "$"}:
            monto = round(monto * TIPO_CAMBIO_USD_PEN, 2)
        if 10 <= monto <= 5000:
            return monto

    return None


def extraer_mantenimiento_detalle(driver_actual, url_anuncio):
    """Visita la ficha de detalle y busca mantenimiento en bloques de texto probables."""
    if not url_anuncio:
        return None

    try:
        driver_actual.get(url_anuncio)
        wait = WebDriverWait(driver_actual, 20)
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    except Exception:
        return None

    if detectar_bloqueo_cloudflare(driver_actual):
        return None

    xpaths_texto = [
        "//*[contains(translate(normalize-space(.), 'MANTENIMIENTO', 'mantenimiento'), 'mantenimiento')]",
        "//*[contains(translate(normalize-space(.), 'MANTEN.', 'manten.'), 'manten')]",
    ]

    candidatos = []
    for xpath in xpaths_texto:
        try:
            nodos = driver_actual.find_elements(By.XPATH, xpath)
            for nodo in nodos:
                txt = " ".join((nodo.text or "").split())
                if txt and txt not in candidatos and len(txt) <= 200:
                    candidatos.append(txt)
        except Exception:
            continue

    for texto in candidatos:
        monto = extraer_mantenimiento_desde_texto(texto)
        if monto is not None:
            return monto

    # Fallback en toda la página si no se encontró en nodos específicos.
    return extraer_mantenimiento_desde_texto(driver_actual.page_source or "")


def normalizar_para_busqueda(texto):
    """Normaliza texto para busquedas simples sin acentos."""
    reemplazos = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ñ": "n",
    }
    resultado = texto.lower()
    for origen, destino in reemplazos.items():
        resultado = resultado.replace(origen, destino)
    return resultado


def extraer_amenities(texto_fuente):
    """Detecta amenities principales para modelado binario."""
    base = normalizar_para_busqueda(texto_fuente or "")
    return {
        "Seguridad_24_7": 1 if ("seguridad" in base or "vigilancia" in base or "guardiania" in base) else 0,
        "Piscina": 1 if "piscina" in base else 0,
        "Gym": 1 if ("gimnasio" in base or "gym" in base) else 0,
        "Parrilla": 1 if ("parrilla" in base or "bbq" in base) else 0,
        "Mascotas": 1 if ("mascota" in base or "pet friendly" in base) else 0,
    }


def extraer_antiguedad(texto_fuente):
    """Extrae antiguedad aproximada desde texto libre."""
    if not texto_fuente:
        return "No especifica"
    base = normalizar_para_busqueda(texto_fuente)
    if "a estrenar" in base:
        return "A estrenar"
    match = re.search(r"(\d+)\s*anos?\s*de\s*antiguedad", base, flags=re.IGNORECASE)
    if match:
        return f"{match.group(1)} anos"
    return "No especifica"


def inferir_tipo_operacion(url_anuncio):
    """Infiere si el aviso es de alquiler o venta a partir de la URL."""
    if not url_anuncio:
        return "Desconocido"
    base = url_anuncio.lower()
    if "alquiler" in base or "/alcl" in base:
        return "Alquiler"
    if "venta" in base or "/vecl" in base:
        return "Venta"
    return "Desconocido"


def inferir_tipo_inmueble(url_anuncio):
    """Infiere tipo de inmueble a partir de la URL."""
    if not url_anuncio:
        return "No especifica"
    base = url_anuncio.lower()
    if "/proyecto/" in base:
        return "Proyecto"
    if "departamento" in base:
        return "Departamento"
    if "casa" in base:
        return "Casa"
    if "condominio" in base:
        return "Condominio"
    return "No especifica"


def extraer_id_anuncio(url_anuncio):
    """Extrae un identificador numerico del aviso desde la URL."""
    if not url_anuncio:
        return ""
    match = re.search(r"-(\d+)(?:\?|$)", url_anuncio)
    return match.group(1) if match else ""


def calcular_precio_total_soles(precio_soles, mantenimiento):
    """Calcula costo mensual total en soles."""
    if precio_soles is None:
        return None
    if mantenimiento is None:
        return precio_soles
    return round(precio_soles + mantenimiento, 2)


def calcular_precio_m2(precio_soles, m2):
    """Calcula precio por metro cuadrado en soles."""
    if precio_soles is None or m2 is None or m2 <= 0:
        return None
    return round(precio_soles / m2, 2)


def obtener_url_siguiente(driver_actual):
    """Obtiene la URL de la siguiente pagina desde el paginador visible."""
    xpaths = [
        "//a[@rel='next']",
        "//a[contains(@aria-label, 'Siguiente') or contains(@aria-label, 'siguiente') or contains(@aria-label, 'Next')]",
        "//li[contains(@class, 'next')]/a[@href]",
        "//a[contains(@class, 'next') and @href]",
    ]
    for xpath in xpaths:
        try:
            candidatos = driver_actual.find_elements(By.XPATH, xpath)
            for enlace in candidatos:
                href = enlace.get_attribute("href")
                if href and not href.startswith("javascript"):
                    return urljoin(BASE_URL, href)
        except Exception:
            continue
    return ""


def detectar_bloqueo_cloudflare(driver_actual):
    """Detecta la pantalla de verificacion de Cloudflare."""
    html = (driver_actual.page_source or "").lower()
    patrones = [
        "verificacion de seguridad en curso",
        "cf-turnstile-response",
        "enable javascript and cookies to continue",
        "cloudflare",
    ]
    return any(patron in html for patron in patrones)


def obtener_tarjetas(driver_actual):
    """Construye contenedores de avisos evitando subfilas tipo 'posting-card-row'."""

    def agregar_si_nuevo(candidato, coleccion, vistos):
        if candidato is not None and candidato.id not in vistos:
            coleccion.append(candidato)
            vistos.add(candidato.id)

    tarjetas_encontradas = []
    ids_vistos = set()

    # 1) Ancla principal: la descripcion suele existir una vez por anuncio.
    descripciones = driver_actual.find_elements(By.XPATH, "//h2[@data-qa='POSTING_CARD_DESCRIPTION']")
    for descripcion in descripciones:
        ancestro = descripcion.find_elements(
            By.XPATH,
            "ancestor::div[.//*[@data-qa='POSTING_CARD_PRICE'] and (.//*[@data-qa='POSTING_CARD_LOCATION'] or .//*[@data-qa='POSTING_CARD_FEATURES'])][1]",
        )
        if ancestro:
            agregar_si_nuevo(ancestro[0], tarjetas_encontradas, ids_vistos)

    # 2) Fallback: tarjetas por clase conocida (si existe en la version actual del DOM).
    if not tarjetas_encontradas:
        por_clase = driver_actual.find_elements(
            By.XPATH,
            "//div[contains(@class, 'postingCard-module__posting-card') and not(contains(@class, 'posting-card-row'))]",
        )
        for tarjeta in por_clase:
            agregar_si_nuevo(tarjeta, tarjetas_encontradas, ids_vistos)

    # 3) Fallback final: contenedores article con al menos precio/ubicacion/descripcion.
    if not tarjetas_encontradas:
        por_article = driver_actual.find_elements(
            By.XPATH,
            "//article[.//*[@data-qa='POSTING_CARD_PRICE'] or .//*[@data-qa='POSTING_CARD_LOCATION'] or .//h2[@data-qa='POSTING_CARD_DESCRIPTION']]",
        )
        for tarjeta in por_article:
            agregar_si_nuevo(tarjeta, tarjetas_encontradas, ids_vistos)

    return tarjetas_encontradas


def crear_driver():
    """Crea el navegador con fallback si undetected_chromedriver no esta disponible."""
    if uc is not None:
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-blink-features=AutomationControlled")
        return uc.Chrome(options=options)

    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )


driver = crear_driver()

try:
    # 1. Creamos lista de filas para guardar todo lo encontrado.
    datos_departamentos = []
    urls_para_detalle = []
    fecha_extraccion = datetime.now().strftime("%Y-%m-%d")
    
    # Contadores para depuración
    contadores = {
        "avisos_totales_encontrados": 0,
        "sin_datos_minimos": 0,
        "url_duplicada": 0,
        "fila_duplicada": 0,
        "avisos_validos": 0,
        "ventas_excluidas": 0,
        "consultar_precio_eliminadas": 0,
        "sin_url_eliminadas": 0,
        "duplicados_url_eliminados": 0,
        "cocheras_ajustadas": 0,
    }

    for pagina in range(1, N_PAGINAS + 1):
        # Forzamos la URL de cada página para no depender del paginador del sitio.
        url_pagina = construir_url_pagina(BASE_URL, pagina)
        print(f"\nProcesando pagina {pagina}: {url_pagina}")
        driver.get(url_pagina)

        # Si aparece desafio anti-bot, permite resolverlo manualmente.
        if detectar_bloqueo_cloudflare(driver):
            print("Se detecto verificacion de Cloudflare.")
            print("Resuelvela en la ventana del navegador y luego presiona Enter para continuar...")
            try:
                input()
            except EOFError:
                pass

        # 2. Esperamos hasta que aparezcan elementos base (sitio dinámico)
        try:
            wait = WebDriverWait(driver, 25)
            wait.until(
                lambda d: len(d.find_elements(By.XPATH, "//*[@data-qa='POSTING_CARD_PRICE'] | //h2[@data-qa='POSTING_CARD_DESCRIPTION']")) > 0
            )
        except TimeoutException:
            carpeta_script = Path(__file__).resolve().parent
            ruta_screenshot = carpeta_script / f"debug_timeout_p{pagina}.png"
            ruta_html = carpeta_script / f"debug_timeout_p{pagina}.html"
            driver.save_screenshot(str(ruta_screenshot))
            ruta_html.write_text(driver.page_source, encoding="utf-8")
            print(f"Timeout en pagina {pagina}. Revisa: {ruta_screenshot.name} y {ruta_html.name}")
            if detectar_bloqueo_cloudflare(driver):
                print("No se pudo continuar por bloqueo anti-bot en esta pagina.")
            continue

        # 3. Buscamos tarjetas de esta página
        tarjetas = obtener_tarjetas(driver)
        print(f"Se encontraron {len(tarjetas)} anuncios en esta página.")

        # Si no encuentra tarjetas, guardamos evidencia para depuración
        if len(tarjetas) == 0:
            carpeta_script = Path(__file__).resolve().parent
            ruta_screenshot = carpeta_script / f"debug_urbania_p{pagina}.png"
            ruta_html = carpeta_script / f"debug_urbania_p{pagina}.html"
            driver.save_screenshot(str(ruta_screenshot))
            ruta_html.write_text(driver.page_source, encoding="utf-8")
            print(f"No se detectaron anuncios en pagina {pagina}. Revisa: {ruta_screenshot.name} y {ruta_html.name}")
            continue

        # 4. Recorremos cada tarjeta, una por una
        for tarjeta in tarjetas:
            contadores["avisos_totales_encontrados"] += 1
            texto_tarjeta = " ".join((tarjeta.text or "").split())
            
            precio = extraer_texto_con_selectores(
                tarjeta,
                [
                    ".//h2[@data-qa='POSTING_CARD_PRICE']",
                    ".//*[@data-qa='posting-card-price']",
                    ".//*[contains(@class, 'postingPrices-module__price') and not(contains(@class, 'price-from'))]",
                ],
                "Sin precio",
            )

            ubicacion = extraer_texto_con_selectores(
                tarjeta,
                [
                    ".//*[@data-qa='POSTING_CARD_LOCATION']",
                    ".//*[@data-qa='posting-card-location']",
                    ".//h4[contains(@class, 'postingLocations-module__location-text')]",
                    ".//*[contains(@class, 'location')]",
                ],
                "Sin ubicación",
            )

            direccion = extraer_texto_con_selectores(
                tarjeta,
                [
                    ".//h4[contains(@class, 'postingLocations-module__location-address')]",
                ],
                "",
            )

            caracteristicas = extraer_lista_textos_con_selectores(
                tarjeta,
                [
                    ".//*[@data-qa='POSTING_CARD_FEATURES']//span",
                    ".//*[@data-qa='POSTING_CARD_FEATURES']",
                    ".//*[contains(@class, 'postingMainFeatures-module__posting-main-features-span')]",
                    ".//*[contains(@class, 'postingCard-module__pill-item-feature')]",
                ],
                "Sin características",
            )

            url_anuncio = extraer_url_anuncio(tarjeta)

            if precio != "Sin precio":
                precio = " ".join(precio.split())
            if ubicacion != "Sin ubicación":
                ubicacion = " ".join(ubicacion.split())
            elif direccion:
                ubicacion = " ".join(direccion.split())

            fila = {
                "Ubicación": ubicacion,
                "Distrito": extraer_distrito(ubicacion),
                "Precio": precio,
                "Características": caracteristicas,
                "URL": url_anuncio,
                "Página": pagina,
            }

            precio_original, moneda, precio_soles = extraer_precio_info(precio)
            fila["Precio_Original"] = precio_original
            fila["Moneda"] = moneda
            fila["Precio_Soles"] = precio_soles
            fila["m2"] = extraer_m2(caracteristicas)
            fila["Dormitorios"] = extraer_dormitorios(caracteristicas)
            fila["Banos"] = extraer_banos(caracteristicas)
            fila["Cocheras"] = extraer_cocheras(caracteristicas)
            fila["Mantenimiento"] = extraer_mantenimiento(tarjeta)
            fila["Antiguedad"] = extraer_antiguedad(texto_tarjeta)
            fila["Tipo_Operacion"] = inferir_tipo_operacion(url_anuncio)
            fila["Tipo_Inmueble"] = inferir_tipo_inmueble(url_anuncio)
            fila["ID_Anuncio"] = extraer_id_anuncio(url_anuncio)
            fila["Fecha_Extraccion"] = fecha_extraccion
            fila.update(extraer_amenities(f"{caracteristicas} {texto_tarjeta}"))

            if fila["Tipo_Operacion"] == "Venta":
                contadores["ventas_excluidas"] += 1
                print(f"  [p{pagina}] [SKIP] VENTA EXCLUIDA: {fila['Distrito']} | {fila['Precio_Original']}")
                continue

            datos_departamentos.append(fila)
            if fila["URL"]:
                urls_para_detalle.append(fila["URL"])
            contadores["avisos_validos"] += 1
            print(f"  [p{pagina}] [OK] GUARDADO: {fila['Distrito']} | {fila['Precio_Original']}")

    # 5. Convertimos la lista en una tabla (DataFrame)
    df = pd.DataFrame(datos_departamentos)
    urls_para_detalle = []

    if not df.empty:
        df["URL"] = df["URL"].fillna("").astype(str).str.strip()
        df["Precio_Original"] = df["Precio_Original"].fillna("").astype(str).str.strip()
        df["Precio_Soles"] = pd.to_numeric(df["Precio_Soles"], errors="coerce")
        df["Cocheras"] = pd.to_numeric(df["Cocheras"], errors="coerce")

        mascara_consultar_precio = (
            df["Precio_Original"].str.contains("consultar precio", case=False, na=False)
            | df["Precio_Soles"].isna()
        )
        contadores["consultar_precio_eliminadas"] = int(mascara_consultar_precio.sum())
        if contadores["consultar_precio_eliminadas"]:
            df = df.loc[~mascara_consultar_precio].copy()

        mascara_sin_url = df["URL"].eq("")
        contadores["sin_url_eliminadas"] = int(mascara_sin_url.sum())
        if contadores["sin_url_eliminadas"]:
            df = df.loc[~mascara_sin_url].copy()

        mascara_duplicados_url = df.duplicated(subset="URL", keep="first")
        contadores["duplicados_url_eliminados"] = int(mascara_duplicados_url.sum())
        if contadores["duplicados_url_eliminados"]:
            df.drop_duplicates(subset="URL", keep="first", inplace=True)

        mascara_cocheras_outlier = df["Cocheras"].notna() & (df["Cocheras"] > 5)
        contadores["cocheras_ajustadas"] = int(mascara_cocheras_outlier.sum())
        if contadores["cocheras_ajustadas"]:
            df.loc[mascara_cocheras_outlier, "Cocheras"] = 5

        urls_para_detalle = list(dict.fromkeys([u for u in df["URL"].tolist() if u]))

    if EXTRAER_MANTENIMIENTO_DETALLE:
        urls_unicas = list(dict.fromkeys([u for u in urls_para_detalle if u]))
        if MAX_URLS_DETALLE > 0:
            urls_unicas = urls_unicas[:MAX_URLS_DETALLE]

        print(f"\nIniciando extraccion de mantenimiento desde detalle para {len(urls_unicas)} URL(s)...")
        mantenimiento_por_url = {}
        for i, url in enumerate(urls_unicas, start=1):
            monto = extraer_mantenimiento_detalle(driver, url)
            if monto is not None:
                mantenimiento_por_url[url] = monto
            if i % 20 == 0 or i == len(urls_unicas):
                print(f"  Progreso detalle: {i}/{len(urls_unicas)}")

        if mantenimiento_por_url:
            df["Mantenimiento"] = df.apply(
                lambda fila: mantenimiento_por_url.get(fila["URL"], fila["Mantenimiento"]),
                axis=1,
            )
            print(f"Mantenimiento completado desde detalle en {len(mantenimiento_por_url)} URL(s).")
        else:
            print("No se detecto mantenimiento en las fichas de detalle visitadas.")

    df["Precio_Total_Soles"] = df.apply(
        lambda fila: calcular_precio_total_soles(fila["Precio_Soles"], fila["Mantenimiento"]),
        axis=1,
    )
    df["Precio_m2"] = df.apply(
        lambda fila: calcular_precio_m2(fila["Precio_Soles"], fila["m2"]),
        axis=1,
    )

    columnas_salida = [
        "ID_Anuncio",
        "Tipo_Operacion",
        "Tipo_Inmueble",
        "Fecha_Extraccion",
        "Ubicación",
        "Distrito",
        "Precio_Original",
        "Moneda",
        "Precio_Soles",
        "Mantenimiento",
        "Precio_Total_Soles",
        "Precio_m2",
        "m2",
        "Dormitorios",
        "Banos",
        "Cocheras",
        "Piscina",
        "Gym",
        "Parrilla",
        "Seguridad_24_7",
        "Mascotas",
        "Antiguedad",
        "Características",
        "URL",
        "Página",
    ]
    df = df.reindex(columns=columnas_salida)

    print("\n" + "="*70)
    print("RESUMEN DE SCRAPING:")
    print("="*70)
    print(f"Avisos totales encontrados: {contadores['avisos_totales_encontrados']}")
    print(f"  - Sin datos mínimos: {contadores['sin_datos_minimos']}")
    print(f"  - URL duplicada (entre páginas): {contadores['url_duplicada']}")
    print(f"  - Fila completa duplicada (sin URL): {contadores['fila_duplicada']}")
    print(f"  - Ventas excluidas: {contadores['ventas_excluidas']}")
    print(f"  - 'Consultar precio' eliminadas: {contadores['consultar_precio_eliminadas']}")
    print(f"  - Sin URL eliminadas: {contadores['sin_url_eliminadas']}")
    print(f"  - Duplicados por URL eliminados: {contadores['duplicados_url_eliminados']}")
    print(f"  - Cocheras ajustadas a maximo 5: {contadores['cocheras_ajustadas']}")
    print(f"  - Avisos válidos guardados: {contadores['avisos_validos']}")
    print("="*70)
    print("\nVista previa de la Base de Datos:")
    print(df.head())
    print(f"\nTotal de avisos consolidados: {len(df)}")

    # Opcional: guardar CSV en la misma carpeta del script
    salida_csv = Path(__file__).resolve().parent / "alquileres_lima_crudo.csv"
    df.to_csv(salida_csv, index=False, encoding="utf-8-sig")
    print(f"\nArchivo guardado con éxito en: {salida_csv}")
finally:
    driver.quit()