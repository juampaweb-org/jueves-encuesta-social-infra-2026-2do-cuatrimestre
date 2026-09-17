# jueves-encuesta-social-infra-2026-2do-cuatrimestre
jueves-encuesta-social-infra-2026-2do-cuatrimestre

## Cómo generar los gráficos y la web

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python analizar_encuesta.py
```

Esto genera la carpeta `output/` con los gráficos (`output/graficos/*.png`) y
`output/index.html`, que se puede abrir directamente en el navegador (no
necesita servidor).

El código fuente está en `analizar_encuesta.py`, pensado para poder leerse
de punta a punta (solo usa la librería estándar de Python + matplotlib).
