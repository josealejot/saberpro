"""
Simulador Pruebas Saber 5° - ICFES Colombia
Desarrollado para: Isaías Tangarife (Grado 5°)
Apegado a las matrices de referencia y estándares oficiales del ICFES y MEN Colombia.
"""

import json
import os
import sys
import secrets
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "saber5_isaias_tangarife_oficial_2026"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PREGUNTAS_FILE = os.path.join(BASE_DIR, "data", "preguntas.json")
RESULTS_DIR = os.path.join(BASE_DIR, "data", "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# Almacén en servidor de resultados (en memoria y disco para compatibilidad con gunicorn en Render)
RESULTADOS_STORE = {}

def guardar_resultado(res_id, data):
    RESULTADOS_STORE[res_id] = data
    RESULTADOS_STORE["latest"] = data
    try:
        filepath = os.path.join(RESULTS_DIR, f"{res_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception as e:
        pass

def obtener_resultado(res_id):
    if res_id and res_id in RESULTADOS_STORE:
        return RESULTADOS_STORE[res_id]
    if res_id:
        filepath = os.path.join(RESULTS_DIR, f"{res_id}.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    RESULTADOS_STORE[res_id] = data
                    return data
            except Exception:
                pass
    if "latest" in RESULTADOS_STORE:
        return RESULTADOS_STORE["latest"]
    try:
        files = [os.path.join(RESULTS_DIR, f) for f in os.listdir(RESULTS_DIR) if f.endswith(".json")]
        if files:
            files.sort(key=os.path.getmtime, reverse=True)
            with open(files[0], "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return None

# Media nacional histórica estándar del ICFES en la escala 100-500
MEDIA_NACIONAL_ICFES = 300

AREAS_INFO = {
    "Matemáticas": {
        "icono": "📐",
        "color": "#0284c7",
        "color_light": "#e0f2fe",
        "descripcion": "Pensamiento numérico, espacial-geométrico, métrico, variacional y aleatorio.",
        "componentes": ["Numérico - Variacional", "Geométrico - Métrico", "Aleatorio (Estadística)"]
    },
    "Lenguaje": {
        "icono": "📚",
        "color": "#16a34a",
        "color_light": "#dcfce7",
        "descripcion": "Comprensión lectora de textos continuos, discontinuos, literarios e informativos.",
        "componentes": ["Semántico / Comprensión lectora", "Sintáctico / Estructura del texto", "Pragmático / Propósito comunicativo"]
    },
    "Ciencias Naturales": {
        "icono": "🔬",
        "color": "#d97706",
        "color_light": "#fef3c7",
        "descripcion": "Entorno vivo (cuerpo y ecosistemas), entorno físico (materia y energía) y ciencia/sociedad.",
        "componentes": ["Entorno vivo", "Entorno físico (Materia y Energía)", "Ciencia, Tecnología y Sociedad"]
    },
    "Competencias Ciudadanas": {
        "icono": "🤝",
        "color": "#9333ea",
        "color_light": "#f3e8ff",
        "descripcion": "Convivencia y paz, participación democrática y valoración de la pluralidad y diversidad.",
        "componentes": ["Convivencia y Paz", "Participación y Responsabilidad Democrática", "Pluralidad, Identidad y Valoración de las Diferencias"]
    }
}

def cargar_preguntas():
    """Carga el banco completo de preguntas desde preguntas.json."""
    if not os.path.exists(PREGUNTAS_FILE):
        return []
    with open(PREGUNTAS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def calcular_puntaje_icfes(correctas, total):
    """
    Calcula el puntaje en la escala oficial ICFES de 100 a 500 puntos.
    Puntaje = 100 + round((correctas / total) * 400)
    """
    if total <= 0:
        return 100
    puntaje = 100 + round((correctas / total) * 400)
    return max(100, min(500, puntaje))

def obtener_nivel_desempeno(puntaje):
    """
    Clasificación en los 4 Niveles Oficiales de Desempeño Saber 5°:
    - Nivel 4: Avanzado (450 - 500)
    - Nivel 3: Satisfactorio (350 - 449)
    - Nivel 2: Mínimo (250 - 349)
    - Nivel 1: Insuficiente (100 - 249)
    """
    if puntaje >= 450:
        return {
            "nivel": "Avanzado",
            "rango": "Nivel 4",
            "color": "#10b981",
            "badge_class": "badge-avanzado",
            "mensaje": "¡Dominio sobresaliente! Isaías demuestra un manejo profundo y ejemplar de las competencias.",
            "icono": "🏆",
            "estado_meta": "Meta Superada con Honores"
        }
    elif puntaje >= 350:
        return {
            "nivel": "Satisfactorio",
            "rango": "Nivel 3",
            "color": "#0284c7",
            "badge_class": "badge-satisfactorio",
            "mensaje": "¡Desempeño adecuado! Cumple a cabalidad con los aprendizajes esperados para quinto de primaria.",
            "icono": "⭐",
            "estado_meta": "Competencia Alcanzada"
        }
    elif puntaje >= 250:
        return {
            "nivel": "Mínimo",
            "rango": "Nivel 2",
            "color": "#f59e0b",
            "badge_class": "badge-minimo",
            "mensaje": "¡Nivel básico alcanzado! Maneja los conceptos elementales y está a un paso del nivel satisfactorio.",
            "icono": "🌱",
            "estado_meta": "En Consolidación"
        }
    else:
        return {
            "nivel": "Insuficiente",
            "rango": "Nivel 1",
            "color": "#ef4444",
            "badge_class": "badge-insuficiente",
            "mensaje": "¡Zona de oportunidad! Requiere acompañamiento y práctica focalizada para afianzar los conceptos clave.",
            "icono": "💪",
            "estado_meta": "Por Reforzar"
        }

# Criterios oficiales de evaluación del Ministerio de Educación Nacional de Colombia (MEN - Decreto 1290 de 2009)
PORCENTAJE_MINIMO_APROBATORIO_MEN = 60  # Umbral mínimo de aprobación nacional (60%)
PUNTAJE_MINIMO_APROBATORIO_ICFES = 250   # 250 puntos (Nivel Mínimo / Desempeño Básico)

def evaluar_resultado_men(porcentaje_aciertos, puntaje_icfes):
    """
    Evalúa si el estudiante aprueba o no el test según los estándares oficiales del Ministerio
    de Educación Nacional de Colombia (MEN - Decreto 1290 de 2009) y los niveles ICFES Saber 5°.
    
    Escala Nacional de Desempeño MEN:
    - Desempeño Superior: 90% a 100% (Puntaje ICFES 450-500) -> APROBADO CON EXCELENCIA
    - Desempeño Alto: 75% a 89% (Puntaje ICFES 350-449) -> APROBADO CON ALTO DESEMPEÑO
    - Desempeño Básico: 60% a 74% (Puntaje ICFES 250-349) -> APROBADO (MÍNIMO REQUERIDO POR EL MEN)
    - Desempeño Bajo: 0% a 59% (Puntaje ICFES 100-249) -> NO APROBADO / REPROBADO (REQUIERE REFUERZO)
    """
    aprobado = (porcentaje_aciertos >= PORCENTAJE_MINIMO_APROBATORIO_MEN) or (puntaje_icfes >= PUNTAJE_MINIMO_APROBATORIO_ICFES)

    if porcentaje_aciertos >= 90 or puntaje_icfes >= 450:
        escala_men = "Desempeño Superior"
        estado_texto = "¡Prueba Aprobada con Honores!"
        badge_class = "badge-men-superior"
        icono = "🏆"
        color = "#10b981"
        mensaje = "¡Extraordinario, Isaías! Has superado con maestría las competencias evaluadas, alcanzando el nivel Superior del Ministerio de Educación Nacional."
    elif porcentaje_aciertos >= 75 or puntaje_icfes >= 350:
        escala_men = "Desempeño Alto"
        estado_texto = "¡Prueba Aprobada con Éxito!"
        badge_class = "badge-men-alto"
        icono = "⭐"
        color = "#0284c7"
        mensaje = "¡Muy bien hecho, Isaías! Demuestras un dominio sólido y sobresaliente de los aprendizajes exigidos para 5° de primaria."
    elif aprobado:
        escala_men = "Desempeño Básico"
        estado_texto = "¡Prueba Aprobada!"
        badge_class = "badge-men-basico"
        icono = "🎉"
        color = "#16a34a"
        mensaje = "¡Felicitaciones, Isaías! Has alcanzado el porcentaje mínimo aprobatorio del MEN (60% / 250 puntos). Cumples con los aprendizajes básicos esperados."
    else:
        escala_men = "Desempeño Bajo"
        estado_texto = "Prueba No Aprobada (Por Reforzar)"
        badge_class = "badge-men-bajo"
        icono = "⚠️"
        color = "#ef4444"
        mensaje = f"Isaías, según el estándar del Ministerio de Educación Nacional (Decreto 1290), se requiere al menos un {PORCENTAJE_MINIMO_APROBATORIO_MEN}% (o {PUNTAJE_MINIMO_APROBATORIO_ICFES} puntos ICFES) para aprobar la prueba. Tu resultado fue {porcentaje_aciertos}% ({puntaje_icfes} pts). ¡No te rindas! Esta prueba sirve para identificar tus fallas y reforzarlas antes del examen oficial."

    return {
        "aprobado": aprobado,
        "escala_men": escala_men,
        "estado_texto": estado_texto,
        "porcentaje_minimo_exigido": PORCENTAJE_MINIMO_APROBATORIO_MEN,
        "puntaje_minimo_exigido": PUNTAJE_MINIMO_APROBATORIO_ICFES,
        "mensaje": mensaje,
        "icono": icono,
        "color": color,
        "badge_class": badge_class
    }

@app.route("/")
def index():
    """Pantalla inicial con opciones de simulacro real por sesiones o materias."""
    todas_preguntas = cargar_preguntas()
    
    conteos_por_area = {}
    for area in AREAS_INFO.keys():
        conteos_por_area[area] = sum(1 for p in todas_preguntas if p.get("area") == area)

    preguntas_s1 = [p for p in todas_preguntas if p.get("sesion") == 1]
    preguntas_s2 = [p for p in todas_preguntas if p.get("sesion") == 2]

    return render_template(
        "index.html",
        areas_info=AREAS_INFO,
        conteos=conteos_por_area,
        total_preguntas=len(todas_preguntas),
        total_sesion_1=len(preguntas_s1),
        total_sesion_2=len(preguntas_s2),
        media_nacional=MEDIA_NACIONAL_ICFES,
        estudiante_nombre="Isaías Tangarife"
    )

@app.route("/protocolo")
def protocolo():
    """Muestra el protocolo oficial de instrucciones del ICFES previo al examen."""
    modo = request.args.get("modo", "completo")
    sesion_val = request.args.get("sesion")
    area_val = request.args.get("area")
    
    return render_template(
        "protocolo.html",
        modo=modo,
        sesion_val=sesion_val,
        area_val=area_val,
        estudiante_nombre="Isaías Tangarife"
    )

@app.route("/simulador")
def simulador():
    """Entorno del examen con las preguntas correspondientes al modo elegido."""
    area_filtrada = request.args.get("area", "").strip()
    sesion_filtrada = request.args.get("sesion", "").strip()
    todas = cargar_preguntas()

    if sesion_filtrada in ["1", "2"]:
        s_num = int(sesion_filtrada)
        preguntas = [p for p in todas if p.get("sesion") == s_num]
        if s_num == 1:
            titulo_modo = "Sesión 1 Oficial ICFES: Matemáticas y Lenguaje"
            tiempo_sugerido_min = 45
        else:
            titulo_modo = "Sesión 2 Oficial ICFES: Ciencias Naturales y Competencias Ciudadanas"
            tiempo_sugerido_min = 45
        modo_codigo = f"sesion_{s_num}"
        url_reintento = url_for("simulador", sesion=s_num)
    elif area_filtrada and area_filtrada in AREAS_INFO:
        preguntas = [p for p in todas if p.get("area") == area_filtrada]
        titulo_modo = f"Módulo de Entrenamiento: {area_filtrada}"
        tiempo_sugerido_min = 25
        modo_codigo = f"area_{area_filtrada}"
        url_reintento = url_for("simulador", area=area_filtrada)
    else:
        preguntas = todas
        titulo_modo = "Simulacro General Oficial Saber 5° (4 Áreas)"
        tiempo_sugerido_min = 90
        modo_codigo = "completo"
        url_reintento = url_for("simulador")

    if not preguntas:
        return redirect(url_for("index"))

    preguntas_ids_str = ",".join([str(p["id"]) for p in preguntas])

    return render_template(
        "simulador.html",
        preguntas=preguntas,
        preguntas_ids=preguntas_ids_str,
        url_reintento=url_reintento,
        titulo_modo=titulo_modo,
        modo_codigo=modo_codigo,
        tiempo_sugerido_min=tiempo_sugerido_min,
        areas_info=AREAS_INFO,
        estudiante_nombre="Isaías Tangarife"
    )

@app.route("/calificar", methods=["POST"])
def calificar():
    """Motor de calificación oficial del ICFES y MEN con desglose de competencias y componentes."""
    todas_preguntas = cargar_preguntas()
    mapa_preguntas = {str(p["id"]): p for p in todas_preguntas}

    if request.is_json:
        data = request.get_json() or {}
        respuestas_usuario = data.get("respuestas", {})
        tiempo_segundos = data.get("tiempo", 0)
        preguntas_ids_raw = data.get("preguntas_ids", "")
        url_reintento = data.get("url_reintento", url_for("simulador"))
        titulo_modo = data.get("titulo_modo", "Simulacro Saber 5°")
        modo_codigo = data.get("modo_codigo", "completo")
    else:
        respuestas_usuario = {}
        tiempo_segundos = int(request.form.get("tiempo_segundos", 0) or 0)
        preguntas_ids_raw = request.form.get("preguntas_ids", "")
        url_reintento = request.form.get("url_reintento") or url_for("simulador")
        titulo_modo = request.form.get("titulo_modo") or "Simulacro Saber 5°"
        modo_codigo = request.form.get("modo_codigo") or "completo"

        for key, value in request.form.items():
            if key.startswith("preg_"):
                qid = key.replace("preg_", "")
                respuestas_usuario[qid] = value

    # Determinar qué preguntas pertenecían a la prueba presentada
    if preguntas_ids_raw:
        lista_ids = [q.strip() for q in preguntas_ids_raw.split(",") if q.strip()]
        preguntas_evaluar = [mapa_preguntas[qid] for qid in lista_ids if qid in mapa_preguntas]
    elif respuestas_usuario:
        preguntas_evaluar = [mapa_preguntas[qid] for qid in respuestas_usuario if qid in mapa_preguntas]
    else:
        preguntas_evaluar = todas_preguntas

    if not preguntas_evaluar:
        preguntas_evaluar = todas_preguntas

    stats_areas = {}
    stats_componentes = {}
    detalle_preguntas = []
    preguntas_falladas = []
    preguntas_acertadas = []

    total_correctas = 0
    total_incorrectas = 0
    total_sin_responder = 0

    for p_info in preguntas_evaluar:
        qid = str(p_info["id"])
        resp_elegida = respuestas_usuario.get(qid, None)
        sin_responder = (resp_elegida is None or str(resp_elegida).strip() == "")
        es_correcta = False if sin_responder else (str(resp_elegida).strip().upper() == str(p_info["respuesta_correcta"]).strip().upper())

        area = p_info["area"]
        componente = p_info.get("componente", "General")
        competencia = p_info.get("competencia", "General")

        if es_correcta:
            total_correctas += 1
        else:
            total_incorrectas += 1
            if sin_responder:
                total_sin_responder += 1

        # Stats por Área
        if area not in stats_areas:
            stats_areas[area] = {"total": 0, "correctas": 0}
        stats_areas[area]["total"] += 1
        if es_correcta:
            stats_areas[area]["correctas"] += 1

        # Stats por Componente
        comp_key = f"{area} - {componente}"
        if comp_key not in stats_componentes:
            stats_componentes[comp_key] = {"area": area, "componente": componente, "total": 0, "correctas": 0}
        stats_componentes[comp_key]["total"] += 1
        if es_correcta:
            stats_componentes[comp_key]["correctas"] += 1

        # Textos de opciones
        texto_elegida = ""
        texto_correcta = ""
        for opt in p_info.get("opciones", []):
            if opt["key"] == resp_elegida:
                texto_elegida = opt["texto"]
            if opt["key"] == p_info["respuesta_correcta"]:
                texto_correcta = opt["texto"]

        item_pregunta = {
            "id": qid,
            "area": area,
            "componente": componente,
            "competencia": competencia,
            "pregunta": p_info["pregunta"],
            "contexto": p_info.get("contexto", ""),
            "opciones": p_info["opciones"],
            "respuesta_elegida": resp_elegida,
            "texto_elegida": texto_elegida,
            "respuesta_correcta": p_info["respuesta_correcta"],
            "texto_correcta": texto_correcta,
            "es_correcta": es_correcta,
            "sin_responder": sin_responder,
            "explicacion": p_info.get("explicacion", "")
        }

        detalle_preguntas.append(item_pregunta)
        if es_correcta:
            preguntas_acertadas.append(item_pregunta)
        else:
            preguntas_falladas.append(item_pregunta)

    # Calcular puntajes por área (escala 100-500)
    reporte_areas = []
    total_puntajes = 0

    for area, info in stats_areas.items():
        puntaje = calcular_puntaje_icfes(info["correctas"], info["total"])
        total_puntajes += puntaje
        nivel_info = obtener_nivel_desempeno(puntaje)

        # Comparación frente a la Media Nacional (300)
        diferencia_media = puntaje - MEDIA_NACIONAL_ICFES

        reporte_areas.append({
            "area": area,
            "icono": AREAS_INFO.get(area, {}).get("icono", "📝"),
            "color": AREAS_INFO.get(area, {}).get("color", "#0284c7"),
            "correctas": info["correctas"],
            "total": info["total"],
            "puntaje": puntaje,
            "diferencia_media": diferencia_media,
            "porcentaje": round((info["correctas"] / info["total"]) * 100 if info["total"] > 0 else 0),
            "nivel": nivel_info
        })

    # Desglose de Componentes
    reporte_componentes = []
    for comp_data in stats_componentes.values():
        pct = round((comp_data["correctas"] / comp_data["total"]) * 100) if comp_data["total"] > 0 else 0
        reporte_componentes.append({
            "area": comp_data["area"],
            "componente": comp_data["componente"],
            "correctas": comp_data["correctas"],
            "total": comp_data["total"],
            "porcentaje": pct
        })

    total_preguntas = len(preguntas_evaluar)
    porcentaje_global = round((total_correctas / total_preguntas) * 100) if total_preguntas > 0 else 0
    puntaje_global = calcular_puntaje_icfes(total_correctas, total_preguntas)
    nivel_global = obtener_nivel_desempeno(puntaje_global)
    evaluacion_men = evaluar_resultado_men(porcentaje_global, puntaje_global)
    diferencia_global_media = puntaje_global - MEDIA_NACIONAL_ICFES

    mins = tiempo_segundos // 60
    segs = tiempo_segundos % 60
    tiempo_formateado = f"{mins} min {segs} s" if mins > 0 else f"{segs} s"

    fecha_examen = datetime.now().strftime("%d de %B de %Y - %I:%M %p")
    codigo_registro = f"AC-20265-ISAIAS-{datetime.now().strftime('%H%M%S')}"

    resultado_id = f"res_{secrets.token_hex(8)}"
    resultado_data = {
        "id": resultado_id,
        "estudiante": "Isaías Tangarife",
        "codigo_registro": codigo_registro,
        "fecha_examen": fecha_examen,
        "titulo_modo": titulo_modo,
        "modo_codigo": modo_codigo,
        "url_reintento": url_reintento,
        "puntaje_global": puntaje_global,
        "media_nacional": MEDIA_NACIONAL_ICFES,
        "diferencia_global_media": diferencia_global_media,
        "nivel_global": nivel_global,
        "evaluacion_men": evaluacion_men,
        "aprobado": evaluacion_men["aprobado"],
        "porcentaje_global": porcentaje_global,
        "total_preguntas": total_preguntas,
        "total_correctas": total_correctas,
        "total_incorrectas": total_incorrectas,
        "total_sin_responder": total_sin_responder,
        "reporte_areas": reporte_areas,
        "reporte_componentes": reporte_componentes,
        "detalle_preguntas": detalle_preguntas,
        "preguntas_falladas": preguntas_falladas,
        "preguntas_acertadas": preguntas_acertadas,
        "tiempo_formateado": tiempo_formateado
    }

    # Guardar en almacén del servidor (memoria y disco para Render y gunicorn)
    guardar_resultado(resultado_id, resultado_data)
    session["resultado_id"] = resultado_id

    if request.is_json:
        return jsonify({"status": "ok", "redirect": url_for("resultados", id=resultado_id)})

    return redirect(url_for("resultados", id=resultado_id))

@app.route("/resultados")
def resultados():
    """Boletín Oficial de Resultados ICFES para Isaías."""
    res_id = request.args.get("id") or session.get("resultado_id") or "latest"
    resultado = obtener_resultado(res_id)

    if not resultado:
        resultado = session.get("resultado")

    if not resultado:
        return redirect(url_for("index"))

    return render_template(
        "resultados.html",
        res=resultado,
        estudiante_nombre="Isaías Tangarife"
    )

@app.route("/api/preguntas")
def api_preguntas():
    """API para obtener preguntas por sesión o área."""
    area = request.args.get("area")
    sesion_val = request.args.get("sesion")
    todas = cargar_preguntas()

    if sesion_val:
        todas = [p for p in todas if str(p.get("sesion")) == str(sesion_val)]
    if area and area in AREAS_INFO:
        todas = [p for p in todas if p.get("area") == area]

    return jsonify(todas)

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    port = int(os.environ.get("PORT", 5000))
    print(f"[OK] Servidor Oficial Saber 5 iniciado con exito en puerto {port}.")
    print(f"[URL] Abre en tu navegador: http://127.0.0.1:{port}")
    app.run(debug=True, use_reloader=True, host="0.0.0.0", port=port)

