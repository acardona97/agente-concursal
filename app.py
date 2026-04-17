"""
app.py v3 — Agente Concursal con generación de documentos
"""

import os
from pathlib import Path
from flask import Flask, request, jsonify, render_template_string, send_file
from flask_cors import CORS
from agente import consultar_agente, estado_base_vectorial, indexar_documento_nuevo
from generador import generar_documento
import tempfile

app = Flask(__name__)
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

from mcp_server import mcp
app.register_blueprint(mcp)

_historial = []
_nombre_proceso_actual = "Proceso"
EXTENSIONES_PERMITIDAS = {".pdf", ".docx", ".txt"}

HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Agente Concursal · Ley 1116</title>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:wght@400;500&family=Fraunces:ital,wght@0,300;0,700;1,300&display=swap" rel="stylesheet">
<style>
  :root {
    --bg:#0d0f0e;--surface:#131615;--border:#1e2420;
    --gold:#c9a84c;--gold-dim:#7a6230;
    --green:#2d4a3e;--green-lit:#3d6b58;
    --text:#e8e4d9;--text-dim:#7a7568;
    --user-bg:#101c16;--agent-bg:#0f1411;
    --red:#8b3a3a;--blue:#1e3a5f;--blue-lit:#2a5285;
  }
  *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
  body{background:var(--bg);color:var(--text);font-family:'Cormorant Garamond',Georgia,serif;font-size:17px;line-height:1.65;height:100vh;display:flex;flex-direction:column;overflow:hidden}
  header{display:flex;align-items:center;justify-content:space-between;padding:14px 28px;border-bottom:1px solid var(--border);background:var(--surface);flex-shrink:0}
  .header-left{display:flex;align-items:center;gap:14px}
  .logo-mark{width:38px;height:38px;background:linear-gradient(135deg,var(--gold) 0%,var(--gold-dim) 100%);border-radius:6px;display:flex;align-items:center;justify-content:center;font-family:'Fraunces',serif;font-size:20px;font-weight:700;color:#0d0f0e}
  .header-title{font-family:'Fraunces',serif;font-size:18px;font-weight:300;letter-spacing:.04em}
  .header-title span{color:var(--gold);font-style:italic}
  .header-right{display:flex;align-items:center;gap:10px}
  .status-pill{font-family:'JetBrains Mono',monospace;font-size:11px;padding:4px 12px;border-radius:20px;border:1px solid;transition:all .3s}
  .status-pill.ok{color:#5db88a;border-color:#2d6b4a;background:#0a1f14}
  .status-pill.error{color:#c97070;border-color:var(--red);background:#1a0d0d}
  .btn-header{font-family:'JetBrains Mono',monospace;font-size:11px;padding:6px 14px;background:rgba(201,168,76,.1);border:1px solid var(--gold-dim);color:var(--gold);border-radius:6px;cursor:pointer;transition:all .2s;display:flex;align-items:center;gap:6px}
  .btn-header:hover{background:rgba(201,168,76,.2)}

  /* Panel docs */
  .docs-panel{background:var(--surface);border-bottom:1px solid var(--border);padding:0 28px;max-height:0;overflow:hidden;transition:max-height .3s ease,padding .3s ease;flex-shrink:0}
  .docs-panel.open{max-height:200px;padding:12px 28px}
  .docs-panel-title{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--text-dim);text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px}
  .docs-list{display:flex;flex-wrap:wrap;gap:6px}
  .doc-tag{font-family:'JetBrains Mono',monospace;font-size:10px;padding:3px 10px;border-radius:4px;border:1px solid;display:flex;align-items:center;gap:6px}
  .doc-tag.base{color:var(--gold-dim);border-color:#3a2e10;background:rgba(201,168,76,.04)}
  .doc-tag.nuevo{color:#5db88a;border-color:#2d6b4a;background:rgba(93,184,138,.06)}
  .doc-tag.cargando{color:var(--text-dim);border-color:var(--border)}
  .doc-tag .remove{cursor:pointer;color:var(--text-dim);font-size:12px;transition:color .2s}
  .doc-tag .remove:hover{color:#c97070}
  .drop-zone{border:2px dashed var(--border);border-radius:8px;padding:14px;text-align:center;cursor:pointer;transition:all .2s;margin-top:8px;font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--text-dim)}
  .drop-zone:hover,.drop-zone.dragover{border-color:var(--gold-dim);color:var(--gold);background:rgba(201,168,76,.04)}

  /* Quick bar */
  .quick-bar{display:flex;gap:8px;padding:10px 28px;border-bottom:1px solid var(--border);background:var(--surface);overflow-x:auto;flex-shrink:0}
  .quick-bar::-webkit-scrollbar{height:3px}
  .quick-bar::-webkit-scrollbar-thumb{background:var(--border)}
  .quick-btn{font-family:'JetBrains Mono',monospace;font-size:11px;padding:5px 14px;border:1px solid var(--border);background:transparent;color:var(--text-dim);border-radius:4px;cursor:pointer;white-space:nowrap;transition:all .2s}
  .quick-btn:hover{border-color:var(--gold-dim);color:var(--gold);background:rgba(201,168,76,.05)}
  .quick-btn.excel{border-color:#2d4a2d;color:#5db88a}
  .quick-btn.excel:hover{background:rgba(93,184,138,.05)}
  .quick-btn.word{border-color:#1e3a5f;color:#7ab3e0}
  .quick-btn.word:hover{background:rgba(122,179,224,.05)}

  /* Chat */
  #chat{flex:1;overflow-y:auto;padding:28px;display:flex;flex-direction:column;gap:24px;scroll-behavior:smooth}
  #chat::-webkit-scrollbar{width:4px}
  #chat::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px}
  .msg{display:flex;gap:14px;animation:fadeUp .3s ease}
  @keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
  .avatar{width:34px;height:34px;border-radius:6px;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:600;font-family:'JetBrains Mono',monospace}
  .avatar.user{background:var(--green);color:#8ecfb0;border:1px solid var(--green-lit)}
  .avatar.agent{background:rgba(201,168,76,.1);color:var(--gold);border:1px solid var(--gold-dim)}
  .avatar.system{background:var(--blue);color:#7ab3e0;border:1px solid var(--blue-lit)}
  .bubble{flex:1;padding:16px 20px;border-radius:8px;border:1px solid var(--border);max-width:820px;line-height:1.7}
  .bubble.user{background:var(--user-bg);border-color:var(--green)}
  .bubble.agent{background:var(--agent-bg)}
  .bubble.system{background:#0a1220;border-color:var(--blue-lit)}
  .bubble-meta{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--text-dim);margin-bottom:8px;text-transform:uppercase;letter-spacing:.08em}
  .bubble-text{white-space:pre-wrap;font-size:16px}

  /* Tarjeta de documento generado */
  .doc-card{margin-top:14px;padding:14px 16px;background:#0a1a0f;border:1px solid #2d6b4a;border-radius:8px;display:flex;align-items:center;gap:14px}
  .doc-card-icon{font-size:28px;flex-shrink:0}
  .doc-card-info{flex:1}
  .doc-card-name{font-family:'JetBrains Mono',monospace;font-size:12px;color:#5db88a;font-weight:500}
  .doc-card-sub{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--text-dim);margin-top:2px}
  .btn-download{font-family:'JetBrains Mono',monospace;font-size:11px;padding:8px 18px;background:linear-gradient(135deg,#2d6b4a,#1e4a33);border:1px solid #3d8b5a;color:#8ecfb0;border-radius:6px;cursor:pointer;text-decoration:none;transition:all .2s;display:inline-flex;align-items:center;gap:6px}
  .btn-download:hover{background:linear-gradient(135deg,#3d8b5a,#2d6b4a);color:#b8f0d0}
  .btn-download.word-btn{background:linear-gradient(135deg,#1e3a5f,#152a45);border-color:#2a5285;color:#7ab3e0}
  .btn-download.word-btn:hover{background:linear-gradient(135deg,#2a5285,#1e3a5f);color:#a8d0f0}

  .sources{margin-top:12px;padding-top:10px;border-top:1px solid var(--border);font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--text-dim)}
  .sources span{display:inline-block;margin:2px 4px 2px 0;padding:2px 8px;background:rgba(201,168,76,.06);border:1px solid var(--gold-dim);border-radius:3px;color:var(--gold-dim)}
  .sources span.nuevo{background:rgba(93,184,138,.06);border-color:#2d6b4a;color:#5db88a}

  .typing{display:flex;gap:5px;align-items:center;padding:8px 0}
  .typing-dot{width:6px;height:6px;border-radius:50%;background:var(--gold-dim);animation:bounce 1.2s infinite}
  .typing-dot:nth-child(2){animation-delay:.2s}
  .typing-dot:nth-child(3){animation-delay:.4s}
  @keyframes bounce{0%,60%,100%{transform:translateY(0);opacity:.4}30%{transform:translateY(-6px);opacity:1}}

  .welcome{text-align:center;padding:48px 20px;color:var(--text-dim)}
  .welcome h2{font-family:'Fraunces',serif;font-size:28px;font-weight:300;font-style:italic;color:var(--gold);margin-bottom:10px}
  .welcome p{font-size:15px;max-width:500px;margin:0 auto}

  .input-area{padding:18px 28px 20px;border-top:1px solid var(--border);background:var(--surface);flex-shrink:0}
  .input-wrapper{display:flex;gap:10px;align-items:flex-end;max-width:900px;margin:0 auto}
  textarea{flex:1;background:var(--bg);border:1px solid var(--border);border-radius:8px;color:var(--text);font-family:'Cormorant Garamond',Georgia,serif;font-size:16px;padding:12px 16px;resize:none;min-height:52px;max-height:160px;line-height:1.5;transition:border-color .2s}
  textarea:focus{outline:none;border-color:var(--gold-dim)}
  textarea::placeholder{color:var(--text-dim)}
  .btn-send{width:52px;height:52px;flex-shrink:0;background:linear-gradient(135deg,var(--gold) 0%,var(--gold-dim) 100%);border:none;border-radius:8px;cursor:pointer;color:#0d0f0e;font-size:20px;display:flex;align-items:center;justify-content:center;transition:opacity .2s,transform .1s}
  .btn-send:hover{opacity:.9}
  .btn-send:active{transform:scale(.96)}
  .btn-send:disabled{opacity:.3;cursor:not-allowed}
  .btn-clear{width:52px;height:52px;flex-shrink:0;background:transparent;border:1px solid var(--border);border-radius:8px;cursor:pointer;color:var(--text-dim);font-size:18px;display:flex;align-items:center;justify-content:center;transition:all .2s}
  .btn-clear:hover{border-color:var(--red);color:#c97070}
  .input-hint{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--text-dim);text-align:center;margin-top:8px}

  .progress-bar{height:2px;background:var(--border);position:fixed;top:0;left:0;right:0;z-index:100;display:none}
  .progress-bar.active{display:block}
  .progress-fill{height:100%;background:var(--gold);width:0%;transition:width .3s ease;animation:progress-pulse 1.5s infinite}
  @keyframes progress-pulse{0%,100%{opacity:1}50%{opacity:.6}}

  /* Modal nombre proceso */
  .modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:200;display:none;align-items:center;justify-content:center}
  .modal-overlay.open{display:flex}
  .modal{background:var(--surface);border:1px solid var(--gold-dim);border-radius:12px;padding:28px;width:440px;max-width:90vw}
  .modal h3{font-family:'Fraunces',serif;font-size:20px;font-weight:300;color:var(--gold);margin-bottom:8px}
  .modal p{font-size:14px;color:var(--text-dim);margin-bottom:18px}
  .modal input{width:100%;background:var(--bg);border:1px solid var(--border);border-radius:6px;color:var(--text);font-family:'Cormorant Garamond',serif;font-size:15px;padding:10px 14px;margin-bottom:14px}
  .modal input:focus{outline:none;border-color:var(--gold-dim)}
  .modal-btns{display:flex;gap:8px;justify-content:flex-end}
  .btn-modal-ok{font-family:'JetBrains Mono',monospace;font-size:11px;padding:8px 20px;background:linear-gradient(135deg,var(--gold),var(--gold-dim));border:none;border-radius:6px;color:#0d0f0e;cursor:pointer;font-weight:500}
  .btn-modal-cancel{font-family:'JetBrains Mono',monospace;font-size:11px;padding:8px 16px;background:transparent;border:1px solid var(--border);border-radius:6px;color:var(--text-dim);cursor:pointer}
</style>
</head>
<body>

<div class="progress-bar" id="progressBar"><div class="progress-fill" id="progressFill"></div></div>

<!-- Modal nombre proceso -->
<div class="modal-overlay" id="modalNombre">
  <div class="modal">
    <h3>Nombre del proceso</h3>
    <p>Para el nombre del archivo generado, indica el nombre del deudor o proceso.</p>
    <input type="text" id="inputNombreProceso" placeholder="Ej: Nombre del deudor o proceso" />
    <div class="modal-btns">
      <button class="btn-modal-cancel" onclick="cerrarModal()">Cancelar</button>
      <button class="btn-modal-ok" onclick="confirmarNombre()">Continuar</button>
    </div>
  </div>
</div>

<header>
  <div class="header-left">
    <div class="logo-mark">§</div>
    <div class="header-title">Agente Concursal · <span>Ley 1116 de 2006</span></div>
  </div>
  <div class="header-right">
    <button class="btn-header" onclick="toggleDocs()">📎 Cargar documento</button>
    <div id="status" class="status-pill">cargando...</div>
  </div>
</header>

<div class="docs-panel" id="docsPanel">
  <div class="docs-panel-title">Documentos de contexto activos</div>
  <div class="docs-list" id="docsList">
    <div class="doc-tag cargando">Cargando documentos base...</div>
  </div>
  <div class="drop-zone" id="dropZone"
    onclick="document.getElementById('fileInput').click()"
    ondragover="event.preventDefault();this.classList.add('dragover')"
    ondragleave="this.classList.remove('dragover')"
    ondrop="handleDrop(event)">
    📄 Arrastra aquí un PDF o Word del proceso, o haz clic para seleccionar
  </div>
  <input type="file" id="fileInput" style="display:none" accept=".pdf,.docx,.txt" onchange="subirArchivo(this.files[0])">
</div>

<div class="quick-bar">
  <button class="quick-btn excel" onclick="insertar('Redacta el proyecto de calificación y graduación de créditos para el proceso de [DEUDOR], con los siguientes créditos reconocidos: [LISTA DE ACREEDORES, CLASES Y VALORES]')">📊 Calificación (Excel)</button>
  <button class="quick-btn word" onclick="insertar('Redacta un memorial objetando el crédito de [ACREEDOR] por valor de [MONTO] como [CLASE], argumentando que debe graduarse como [NUEVA CLASE] por [ARGUMENTO]')">📝 Objeción a crédito</button>
  <button class="quick-btn excel" onclick="insertar('Redacta un proyecto de votos para la deliberación del acuerdo de reorganización de [DEUDOR]. Los créditos votantes son: [LISTA]')">📊 Proyecto de votos (Excel)</button>
  <button class="quick-btn word" onclick="insertar('Redacta recurso de reposición contra el auto que [DECISIÓN] en el proceso de reorganización de [DEUDOR], radicado [NÚMERO]')">📝 Recurso de reposición</button>
  <button class="quick-btn word" onclick="insertar('Redacta memorial solicitando apertura de liquidación judicial de [DEUDOR] por incumplimiento del acuerdo de reorganización')">📝 Apertura liquidación</button>
  <button class="quick-btn" onclick="insertar('¿Cuál es el término para presentar objeciones al proyecto de calificación y graduación de créditos bajo la Ley 1116?')">Consulta normativa</button>
</div>

<div id="chat">
  <div class="welcome" id="welcome">
    <h2>Buenas, abogado.</h2>
    <p>Indícame qué necesitas. Los botones <span style="color:#5db88a">📊 verdes</span> generan Excel, los <span style="color:#7ab3e0">📝 azules</span> generan Word. Puedes cargar documentos del proceso con 📎.</p>
  </div>
</div>

<div class="input-area">
  <div class="input-wrapper">
    <textarea id="input" placeholder="Ej: Redacta el proyecto de calificación y graduación del proceso de [DEUDOR]…" rows="1"
      onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();enviar()}"
      oninput="this.style.height='auto';this.style.height=Math.min(this.scrollHeight,160)+'px'"></textarea>
    <button class="btn-clear" onclick="limpiarChat()" title="Nueva conversación">↺</button>
    <button class="btn-send" id="btnSend" onclick="enviar()">➤</button>
  </div>
  <div class="input-hint">📊 Excel para calificaciones y votos · 📝 Word para escritos · Enter para enviar</div>
</div>

<script>
const chat=document.getElementById('chat'),input=document.getElementById('input'),btnSend=document.getElementById('btnSend');
let docsAbiertos=false,documentosNuevos=[],pendingMensaje=null;

fetch('/status').then(r=>r.json()).then(d=>{
  const el=document.getElementById('status');
  el.textContent=d.ok?`● ${d.fragmentos} fragmentos`:'● Sin base vectorial';
  el.className=`status-pill ${d.ok?'ok':'error'}`;
  document.getElementById('docsList').innerHTML=`<div class="doc-tag base">📚 Base normativa · ${d.fragmentos||0} fragmentos</div>`;
});

function toggleDocs(){
  docsAbiertos=!docsAbiertos;
  document.getElementById('docsPanel').classList.toggle('open',docsAbiertos);
}
function handleDrop(e){
  e.preventDefault();
  document.getElementById('dropZone').classList.remove('dragover');
  if(e.dataTransfer.files[0])subirArchivo(e.dataTransfer.files[0]);
}
async function subirArchivo(file){
  if(!file)return;
  const ext='.'+file.name.split('.').pop().toLowerCase();
  if(!['.pdf','.docx','.txt'].includes(ext)){agregarSistema(`⚠️ Formato no soportado: ${file.name}`);return;}
  const pb=document.getElementById('progressBar'),pf=document.getElementById('progressFill');
  pb.classList.add('active');pf.style.width='30%';
  const lista=document.getElementById('docsList');
  const tagTemp=document.createElement('div');
  tagTemp.className='doc-tag cargando';tagTemp.id='tag-cargando';
  tagTemp.textContent=`⏳ ${file.name}`;lista.appendChild(tagTemp);
  agregarSistema(`📄 Cargando: ${file.name}...`);
  const fd=new FormData();fd.append('file',file);
  try{
    pf.style.width='60%';
    const res=await fetch('/cargar-documento',{method:'POST',body:fd});
    const data=await res.json();pf.style.width='100%';
    setTimeout(()=>{pb.classList.remove('active');pf.style.width='0%'},500);
    document.getElementById('tag-cargando')?.remove();
    if(data.ok){
      documentosNuevos.push(file.name);
      const tag=document.createElement('div');tag.className='doc-tag nuevo';
      tag.innerHTML=`✅ ${file.name} <span class="remove" onclick="this.parentElement.remove()">×</span>`;
      lista.appendChild(tag);
      const st=document.getElementById('status');
      st.textContent=`● ${data.fragmentos_total} fragmentos`;st.className='status-pill ok';
      agregarSistema(`✅ ${file.name} cargado (${data.fragmentos_nuevos} fragmentos). Listo para usarlo.`);
    }else{agregarSistema(`⚠️ Error: ${data.error}`);}
  }catch(e){document.getElementById('tag-cargando')?.remove();pb.classList.remove('active');agregarSistema('⚠️ Error de conexión.');}
}
function insertar(t){input.value=t;input.style.height='auto';input.style.height=Math.min(input.scrollHeight,160)+'px';input.focus();}
function agregarSistema(texto){
  const w=document.getElementById('welcome');if(w)w.style.display='none';
  const msg=document.createElement('div');msg.className='msg';
  const av=document.createElement('div');av.className='avatar system';av.textContent='i';
  const bu=document.createElement('div');bu.className='bubble system';
  const me=document.createElement('div');me.className='bubble-meta';me.textContent='Sistema';
  const co=document.createElement('div');co.className='bubble-text';co.textContent=texto;
  bu.appendChild(me);bu.appendChild(co);msg.appendChild(av);msg.appendChild(bu);
  chat.appendChild(msg);chat.scrollTop=chat.scrollHeight;
}
function agregarMensaje(rol,texto,fuentes=[],docInfo=null){
  const w=document.getElementById('welcome');if(w)w.style.display='none';
  const msg=document.createElement('div');msg.className='msg';
  const av=document.createElement('div');av.className=`avatar ${rol}`;av.textContent=rol==='user'?'AB':'§';
  const bu=document.createElement('div');bu.className=`bubble ${rol}`;
  const me=document.createElement('div');me.className='bubble-meta';me.textContent=rol==='user'?'Abogado':'Agente Concursal';
  const co=document.createElement('div');co.className='bubble-text';co.textContent=texto;
  bu.appendChild(me);bu.appendChild(co);
  if(fuentes.length>0){
    const src=document.createElement('div');src.className='sources';
    src.innerHTML='Fuentes: '+fuentes.map(f=>`<span class="${documentosNuevos.includes(f)?'nuevo':''}">${f}</span>`).join('');
    bu.appendChild(src);
  }
  if(docInfo){
    const card=document.createElement('div');card.className='doc-card';
    const isExcel=docInfo.tipo==='excel';
    const ext=isExcel?'xlsx':'docx';
    card.innerHTML=`
      <div class="doc-card-icon">${isExcel?'📊':'📝'}</div>
      <div class="doc-card-info">
        <div class="doc-card-name">${docInfo.nombre_archivo}</div>
        <div class="doc-card-sub">Generado por Agente Concursal · Quarta</div>
      </div>
      <a href="/descargar/${encodeURIComponent(docInfo.nombre_archivo)}" class="btn-download ${isExcel?'':'word-btn'}" download>
        ⬇ Descargar .${ext}
      </a>`;
    bu.appendChild(card);
  }
  msg.appendChild(av);msg.appendChild(bu);
  chat.appendChild(msg);chat.scrollTop=chat.scrollHeight;
}
function mostrarTyping(){
  const msg=document.createElement('div');msg.className='msg';msg.id='typing-msg';
  const av=document.createElement('div');av.className='avatar agent';av.textContent='§';
  const bu=document.createElement('div');bu.className='bubble agent';
  const me=document.createElement('div');me.className='bubble-meta';me.textContent='Agente Concursal · redactando…';
  const ty=document.createElement('div');ty.className='typing';
  ty.innerHTML='<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';
  bu.appendChild(me);bu.appendChild(ty);msg.appendChild(av);msg.appendChild(bu);
  chat.appendChild(msg);chat.scrollTop=chat.scrollHeight;
}
function quitarTyping(){document.getElementById('typing-msg')?.remove();}

// Modal nombre proceso
let _cbNombre=null;
function pedirNombreProceso(cb){
  _cbNombre=cb;
  document.getElementById('modalNombre').classList.add('open');
  document.getElementById('inputNombreProceso').focus();
}
function cerrarModal(){document.getElementById('modalNombre').classList.remove('open');_cbNombre=null;}
function confirmarNombre(){
  const n=document.getElementById('inputNombreProceso').value.trim()||'Proceso';
  document.getElementById('modalNombre').classList.remove('open');
  if(_cbNombre)_cbNombre(n);
  document.getElementById('inputNombreProceso').value='';
}
document.getElementById('inputNombreProceso').addEventListener('keydown',e=>{if(e.key==='Enter')confirmarNombre();});

async function enviar(){
  const texto=input.value.trim();if(!texto)return;
  agregarMensaje('user',texto);
  input.value='';input.style.height='auto';
  btnSend.disabled=true;mostrarTyping();
  try{
    const res=await fetch('/consultar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mensaje:texto})});
    const data=await res.json();quitarTyping();
    if(data.error){agregarMensaje('agent','⚠️ Error: '+data.error);return;}
    // Si hay documento adjunto, mostrar con tarjeta
    if(data.documento){
      agregarMensaje('agent',data.respuesta,data.fuentes||[],data.documento);
    }else{
      agregarMensaje('agent',data.respuesta,data.fuentes||[]);
    }
  }catch(e){quitarTyping();agregarMensaje('agent','⚠️ Error de conexión.');}
  finally{btnSend.disabled=false;input.focus();}
}
async function limpiarChat(){
  await fetch('/limpiar',{method:'POST'});
  chat.innerHTML='';documentosNuevos=[];
  const w=document.createElement('div');w.className='welcome';w.id='welcome';
  w.innerHTML='<h2>Nueva conversación</h2><p>Historial borrado. Base normativa disponible.</p>';
  chat.appendChild(w);
}
</script>
</body>
</html>"""


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/status")
def status():
    return jsonify(estado_base_vectorial())


@app.route("/cargar-documento", methods=["POST"])
def cargar_documento():
    if "file" not in request.files:
        return jsonify({"ok": False, "error": "No se recibió archivo"}), 400
    file = request.files["file"]
    ext = Path(file.filename).suffix.lower()
    if ext not in EXTENSIONES_PERMITIDAS:
        return jsonify({"ok": False, "error": f"Formato {ext} no soportado"}), 400
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name
    try:
        resultado = indexar_documento_nuevo(tmp_path, file.filename)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        os.unlink(tmp_path)


@app.route("/consultar", methods=["POST"])
def consultar():
    global _historial, _nombre_proceso_actual
    data = request.get_json()
    if not data or not data.get("mensaje"):
        return jsonify({"error": "mensaje vacío"}), 400

    mensaje = data["mensaje"]
    nombre_proceso = data.get("nombre_proceso", _nombre_proceso_actual)

    try:
        respuesta, _historial, fuentes = consultar_agente(mensaje, _historial)

        # Intentar generar documento
        doc_info = generar_documento(mensaje, respuesta, nombre_proceso)

        resultado = {"respuesta": respuesta, "fuentes": fuentes}
        if doc_info["tipo"] != "texto":
            resultado["documento"] = doc_info

        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/descargar/<nombre_archivo>")
def descargar(nombre_archivo):
    ruta = Path("./documentos_generados") / nombre_archivo
    if not ruta.exists():
        return "Archivo no encontrado", 404
    return send_file(str(ruta), as_attachment=True, download_name=nombre_archivo)


@app.route("/limpiar", methods=["POST"])
def limpiar():
    global _historial
    _historial = []
    return jsonify({"ok": True})


if __name__ == "__main__":
    Path("./documentos_generados").mkdir(exist_ok=True)
    port = int(os.environ.get("PORT", 5000))
    print("\n⚖️  Agente Concursal v3 — con generación de documentos")
    print("────────────────────────────────────────────────────────")
    print(f"🌐 Corriendo en puerto {port}\n")
    app.run(debug=False, port=port, host="0.0.0.0")
