# 🌟 Simulador Saber 5° - ICFES (Isaías Tangarife)

Aplicación web educativa interactiva desarrollada en **Python (Flask)**, **HTML5**, **CSS3** y **JavaScript Vanilla**, diseñada especialmente para **Isaías Tangarife** para su entrenamiento en las **Pruebas Saber 5° del ICFES** en Colombia.

---

## 🎯 Características Principales

1. **4 Áreas Oficiales del ICFES Grado 5°**:
   - 📐 **Matemáticas** (resolución de problemas, operaciones, geometría y medidas).
   - 📚 **Lenguaje** (comprensión lectora, textos informativos, literarios y carteles).
   - 🔬 **Ciencias Naturales** (ecosistemas, cambios de estado de la materia, seres vivos).
   - 🤝 **Competencias Ciudadanas** (convivencia pacífica, resolución de conflictos, democracia).

2. **Escala Oficial ICFES 100 - 500 Puntos**:
   - Calificación por área y puntaje global promedio.
   - Clasificación en los 4 niveles de desempeño:
     - 🏆 **Avanzado** (450 - 500 pts)
     - ⭐ **Satisfactorio** (350 - 449 pts)
     - 🌱 **Mínimo** (250 - 349 pts)
     - 💪 **Insuficiente** (100 - 249 pts)

3. **Interfaz Dinámica e Infantil**:
   - Paleta de colores estimulante (azul cielo, verde manzana y amarillo sol).
   - Cronómetro amigable y barra de avance en tiempo real.
   - Opciones interactivas con tarjetas grandes (A, B, C, D) de fácil lectura.
   - Reporte con confeti, medallas de reconocimiento, desglose por materia y explicación didáctica por cada pregunta.

---

## 🚀 Cómo Iniciar el Simulador

1. Abre tu terminal en esta carpeta.
2. Asegúrate de tener instaladas las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecuta el servidor de desarrollo:
   ```bash
   python app.py
   ```
4. Abre tu navegador web en:
   👉 **http://127.0.0.1:5000**

---

## 📝 Cómo Agregar Más Preguntas

Solo abre el archivo [`data/preguntas.json`](file:///c:/Users/josea/OneDrive/Documentos/Desarrollos/saber%20pro/data/preguntas.json) y agrega nuevos bloques con la siguiente estructura:

```json
{
  "id": "mat_03",
  "area": "Matemáticas",
  "competencia": "Resolución de problemas",
  "contexto": "Situación cotidiana o lectura breve...",
  "pregunta": "¿Cuál es la pregunta?",
  "opciones": [
    { "key": "A", "texto": "Primera opción" },
    { "key": "B", "texto": "Segunda opción" },
    { "key": "C", "texto": "Tercera opción" },
    { "key": "D", "texto": "Cuarta opción" }
  ],
  "respuesta_correcta": "A",
  "explicacion": "Explicación cariñosa y pedagógica para Isaías..."
}
```
El sistema detectará automáticamente las nuevas preguntas sin necesidad de reiniciar el servidor.
