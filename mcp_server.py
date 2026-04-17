"""
mcp_server.py — Servidor MCP para el Agente Concursal
Formato compatible con Claude.ai
"""

from flask import Blueprint, jsonify, request
import json
import os

mcp = Blueprint("mcp", __name__)

TOOLS = [
    {
        "name": "consultar_agente_concursal",
        "description": (
            "Consulta al agente jurídico especializado en derecho concursal colombiano. "
            "Redacta escritos procesales, proyectos de calificación y graduación de créditos, "
            "proyectos de votos, objeciones y recursos bajo la Ley 1116 de 2006."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "consulta": {
                    "type": "string",
                    "description": "La solicitud del abogado — escrito, consulta normativa o proyecto de calificación."
                }
            },
            "required": ["consulta"]
        }
    }
]


@mcp.route("/mcp", methods=["GET", "POST"])
def mcp_endpoint():
    """Endpoint principal MCP compatible con Claude.ai."""

    if request.method == "GET":
        return jsonify({
            "name": "Agente Concursal — Quarta",
            "version": "1.0.0",
            "description": "Agente jurídico especializado en derecho concursal colombiano (Ley 1116 de 2006)",
            "tools": TOOLS
        })

    # POST — llamada a herramienta
    data = request.get_json(force=True) or {}
    method = data.get("method", "")
    params = data.get("params", {})
    req_id = data.get("id", 1)

    # ── tools/list ──
    if method == "tools/list":
        return jsonify({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": TOOLS}
        })

    # ── tools/call ──
    if method == "tools/call":
        tool_name  = params.get("name", "")
        tool_input = params.get("arguments", {})

        if tool_name == "consultar_agente_concursal":
            consulta = tool_input.get("consulta", "")
            if not consulta:
                return jsonify({
                    "jsonrpc": "2.0", "id": req_id,
                    "error": {"code": -32602, "message": "consulta requerida"}
                })
            try:
                from agente import consultar_agente
                from generador import generar_documento
                respuesta, _, fuentes = consultar_agente(consulta)

                texto_respuesta = respuesta
                doc_info = generar_documento(consulta, respuesta, "Proceso")
                if doc_info["tipo"] != "texto":
                    dominio = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "web-production-b3c34.up.railway.app")
                    texto_respuesta += f"\n\n📎 Documento: https://{dominio}/descargar/{doc_info['nombre_archivo']}"

                return jsonify({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": texto_respuesta}]
                    }
                })
            except Exception as e:
                return jsonify({
                    "jsonrpc": "2.0", "id": req_id,
                    "error": {"code": -32603, "message": str(e)}
                })

        return jsonify({
            "jsonrpc": "2.0", "id": req_id,
            "error": {"code": -32601, "message": f"Herramienta '{tool_name}' no encontrada"}
        })

    # ── initialize ──
    if method == "initialize":
        return jsonify({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "Agente Concursal — Quarta",
                    "version": "1.0.0"
                }
            }
        })

    return jsonify({
        "jsonrpc": "2.0", "id": req_id,
        "error": {"code": -32601, "message": f"Método '{method}' no soportado"}
    })
