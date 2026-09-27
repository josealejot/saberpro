"""
Simulador Pruebas Saber 5° - ICFES Colombia
Desarrollado para: Isaías Tangarife (Grado 5°)
Apegado a las matrices de referencia y estándares oficiales del ICFES y MEN Colombia.
"""

import json
import os
import sys
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "saber5_isaias_tangarife_oficial_2026"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PREGUNTAS_FILE = os.path.join(BASE_DIR, "data", "preguntas.json")

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
    elif area_filtrada and area_filtrada in AREAS_INFO:
        preguntas = [p for p in todas if p.get("area") == area_filtrada]
        titulo_modo = f"Módulo de Entrenamiento: {area_filtrada}"
        tiempo_sugerido_min = 25
        modo_codigo = f"area_{area_filtrada}"
    else:
        preguntas = todas
        titulo_modo = "Simulacro General Oficial Saber 5° (4 Áreas)"
        tiempo_sugerido_min = 90
        modo_codigo = "completo"

    if not preguntas:
        return redirect(url_for("index"))

    return render_template(
        "simulador.html",
        preguntas=preguntas,
        titulo_modo=titulo_modo,
        modo_codigo=modo_codigo,
        tiempo_sugerido_min=tiempo_sugerido_min,
        areas_info=AREAS_INFO,
        estudiante_nombre="Isaías Tangarife"
    )

@app.route("/calificar", methods=["POST"])
def calificar():
    """Motor de calificación oficial del ICFES con desglose de competencias y componentes."""
    todas_preguntas = cargar_preguntas()
    mapa_preguntas = {p["id"]: p for p in todas_preguntas}

    if request.is_json:
        data = request.get_json()
        respuestas_usuario = data.get("respuestas", {})
        tiempo_segundos = data.get("tiempo", 0)
    else:
        respuestas_usuario = {}
        tiempo_segundos = int(request.form.get("tiempo_segundos", 0))
        for key, value in request.form.items():
            if key.startswith("preg_"):
                qid = key.replace("preg_", "")
                respuestas_usuario[qid] = value

    stats_areas = {}
    stats_componentes = {}
    detalle_preguntas = []

    for qid, p_info in mapa_preguntas.items():
        # Procesar solo las preguntas que se encontraban en el formulario
        if qid not in respuestas_usuario and f"preg_{qid}" not in request.form and not request.is_json:
            continue

        resp_elegida = respuestas_usuario.get(qid, None)
        es_correcta = (resp_elegida == p_info["respuesta_correcta"])
        area = p_info["area"]
        componente = p_info.get("componente", "General")
        competencia = p_info.get("competencia", "General")

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

        detalle_preguntas.append({
            "id": qid,
            "area": area,
            "componente": componente,
            "competencia": competencia,
            "pregunta": p_info["pregunta"],
            "contexto": p_info.get("contexto", ""),
            "opciones": p_info["opciones"],
            "respuesta_elegida": resp_elegida,
            "respuesta_correcta": p_info["respuesta_correcta"],
            "es_correcta": es_correcta,
            "explicacion": p_info.get("explicacion", "")
        })

    if not stats_areas:
        return redirect(url_for("index"))

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

    puntaje_global = round(total_puntajes / len(reporte_areas)) if reporte_areas else 100
    nivel_global = obtener_nivel_desempeno(puntaje_global)
    diferencia_global_media = puntaje_global - MEDIA_NACIONAL_ICFES

    mins = tiempo_segundos // 60
    segs = tiempo_segundos % 60
    tiempo_formateado = f"{mins} min {segs} s" if mins > 0 else f"{segs} s"

    fecha_examen = datetime.now().strftime("%d de %B de %Y - %I:%M %p")
    codigo_registro = f"AC-20265-ISAIAS-{datetime.now().strftime('%H%M%S')}"

    session["resultado"] = {
        "estudiante": "Isaías Tangarife",
        "codigo_registro": codigo_registro,
        "fecha_examen": fecha_examen,
        "puntaje_global": puntaje_global,
        "media_nacional": MEDIA_NACIONAL_ICFES,
        "diferencia_global_media": diferencia_global_media,
        "nivel_global": nivel_global,
        "reporte_areas": reporte_areas,
        "reporte_componentes": reporte_componentes,
        "detalle_preguntas": detalle_preguntas,
        "tiempo_formateado": tiempo_formateado,
        "total_preguntas": sum(a["total"] for a in reporte_areas),
        "total_correctas": sum(a["correctas"] for a in reporte_areas)
    }

    if request.is_json:
        return jsonify({"status": "ok", "redirect": url_for("resultados")})

    return redirect(url_for("resultados"))

@app.route("/resultados")
def resultados():
    """Boletín Oficial de Resultados ICFES para Isaías."""
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
    app.run(debug=False, use_reloader=False, host="0.0.0.0", port=port)

