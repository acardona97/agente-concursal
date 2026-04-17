"""
mcp_server.py — Servidor MCP para el Agente Concursal
Permite integrar el agente como plugin en Claude.ai
"""

from flask import Blueprint, jsonify, request
import json

mcp = Blueprint("mcp", __name__)

# ─── Definición de herramientas MCP ──────────────────────────────────────────

TOOLS = [
    {
        "name": "consultar_agente_concursal",
        "description": (
            "Consulta al agente jurídico especializado en derecho concursal colombiano. "
            "Puede redactar escritos procesales, proyectos de calificación y graduación "
            "de créditos, proyectos de votos, objeciones, recursos y cualquier documento "
            "relacionado con procesos de reorganización y liquidación judicial bajo la "
            "Ley 1116 de 2006."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "consulta": {
                    "type": "string",
                    "description": (
                        "La solicitud del abogado. Puede ser una petición de redacción "
                        "de un escrito, una consulta normativa, o una solicitud de "
                        "proyecto de calificación con los datos del proceso."
                    )
                }
            },
            "required": ["consulta"]
        }
    },
    {
        "name": "generar_calificacion_excel",
        "description": (
            "Genera un archivo Excel de calificación y graduación de créditos con "
            "estilo Quarta Acompañamiento Legal. Requiere la lista de acreedores "
            "con sus clases, valores y garantías."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "nombre_proceso": {
                    "type": "string",
                    "description": "Nombre del deudor o proceso concursal"
                },
                "creditos": {
                    "type": "string",
                    "description": (
                        "Lista de créditos en formato: "
                        "N. Acreedor - Clase - Concepto - $Valor - Garantía. "
                        "Ejemplo: 1. Bancolombia - Primera clase - Capital - $150.000.000 - Hipoteca"
                    )
                }
            },
            "required": ["nombre_proceso", "creditos"]
        }
    }
]


# ─── Endpoints MCP ───────────────────────────────────────────────────────────

@mcp.route("/mcp", methods=["GET"])
def mcp_info():
    """Información del servidor MCP."""
    return jsonify({
        "name": "Agente Concursal — Quarta",
        "version": "1.0.0",
        "description": "Agente jurídico especializado en derecho concursal colombiano (Ley 1116 de 2006)",
        "tools": TOOLS
    })


@mcp.route("/mcp/tools", methods=["GET"])
def list_tools():
    """Lista las herramientas disponibles."""
    return jsonify({"tools": TOOLS})


@mcp.route("/mcp/tools/call", methods=["POST"])
def call_tool():
    """Ejecuta una herramienta del agente."""
    from agente import consultar_agente
    from generador import generar_excel_calificacion, generar_documento
    import os

    data = request.get_json()
    if not data:
        return jsonify({"error": "No se recibieron datos"}), 400

    tool_name = data.get("name")
    tool_input = data.get("input", {})

    if tool_name == "consultar_agente_concursal":
        consulta = tool_input.get("consulta", "")
        if not consulta:
            return jsonify({"error": "consulta requerida"}), 400

        try:
            respuesta, _, fuentes = consultar_agente(consulta)
            resultado = {
                "content": [
                    {
                        "type": "text",
                        "text": respuesta
                    }
                ],
                "fuentes": fuentes
            }

            # Intentar generar documento si aplica
            doc_info = generar_documento(consulta, respuesta, "Proceso")
            if doc_info["tipo"] != "texto":
                url_base = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "localhost:5000")
                resultado["content"].append({
                    "type": "text",
                    "text": f"\n\n📎 Documento generado: https://{url_base}/descargar/{doc_info['nombre_archivo']}"
                })

            return jsonify(resultado)

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif tool_name == "generar_calificacion_excel":
        nombre_proceso = tool_input.get("nombre_proceso", "Proceso")
        creditos = tool_input.get("creditos", "")

        if not creditos:
            return jsonify({"error": "creditos requeridos"}), 400

        try:
            from agente import consultar_agente
            solicitud = f"Proyecto de calificación y graduación de {nombre_proceso}:\n{creditos}"
            respuesta, _, _ = consultar_agente(solicitud)
            ruta = generar_excel_calificacion(solicitud, respuesta, nombre_proceso)

            from pathlib import Path
            nombre_archivo = Path(ruta).name
            url_base = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "localhost:5000")

            return jsonify({
                "content": [
                    {
                        "type": "text",
                        "text": f"✅ Excel generado con la calificación y graduación de créditos para {nombre_proceso}.\n\n📊 Descargar: https://{url_base}/descargar/{nombre_archivo}"
                    }
                ]
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    else:
        return jsonify({"error": f"Herramienta '{tool_name}' no encontrada"}), 404
