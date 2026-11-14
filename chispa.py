"""Chispa: la guía de Starwise, dibujada en SVG para poder animarla.

Estados (cambian la animación y el color de los destellos):
- "guia"      → flota suave (te está guiando)
- "pensando"  → se balancea y sus destellos laten: SIMULA QUE LA IA ESTÁ PENSANDO
- "giro"      → tiembla: cambió el escenario del caso
- "logro"     → salta: lo lograste
"""

ESTILOS = """
<style>
.chispa-wrap{display:flex;align-items:flex-end;gap:14px;margin:6px 0 14px 0}
.chispa-svg{flex:0 0 auto;overflow:visible}
.chispa-burbuja{background:#FFFFFF;border:2px solid #DDE5F2;border-radius:20px;padding:14px 18px;
  color:#13243F;font-size:1.05rem;font-weight:600;line-height:1.45;box-shadow:0 5px 0 #DDE5F2;position:relative;max-width:640px;
  animation:ch-burbuja .45s cubic-bezier(.2,1.3,.4,1) both;transform-origin:0 100%}
.chispa-burbuja b{color:#1E6BE6;font-weight:900}
.chispa-nombre{font-size:.78rem;font-weight:900;color:#1E6BE6;letter-spacing:.08em;text-transform:uppercase;margin-bottom:2px}
@keyframes ch-burbuja{from{opacity:0;transform:scale(.7) translateY(10px)}to{opacity:1;transform:none}}
@keyframes ch-llegar{0%{opacity:0;transform:translateY(30px) scale(.6) rotate(-15deg)}60%{opacity:1;transform:translateY(-8px) scale(1.08) rotate(5deg)}100%{transform:none}}
.chispa-svg{animation:ch-llegar .6s ease-out both}
@keyframes ch-flotar{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
@keyframes ch-pensar{0%,100%{transform:rotate(-7deg) scale(1)}50%{transform:rotate(7deg) scale(1.04)}}
@keyframes ch-temblar{0%,100%{transform:translateX(0)}20%{transform:translateX(-5px)}40%{transform:translateX(5px)}60%{transform:translateX(-4px)}80%{transform:translateX(4px)}}
@keyframes ch-saltar{0%,100%{transform:translateY(0) scale(1)}30%{transform:translateY(-18px) scale(1.06,0.95)}55%{transform:translateY(0) scale(0.96,1.04)}}
@keyframes ch-latir{0%,100%{opacity:.35}50%{opacity:1}}
.ch-guia .ch-cuerpo{animation:ch-flotar 2.6s ease-in-out infinite;transform-origin:150px 170px}
.ch-pensando .ch-cuerpo{animation:ch-pensar 0.9s ease-in-out infinite;transform-origin:150px 170px}
.ch-pensando .ch-destello{animation:ch-latir 0.6s ease-in-out infinite}
.ch-giro .ch-cuerpo{animation:ch-temblar 0.5s ease-in-out 3;transform-origin:150px 170px}
.ch-logro .ch-cuerpo{animation:ch-saltar 1.1s ease-in-out infinite;transform-origin:150px 300px}
@media (prefers-reduced-motion: reduce){.ch-cuerpo,.ch-destello{animation:none!important}}
</style>
"""

_COLOR_DESTELLO = {"guia": "#FFC93C", "pensando": "#FFC93C", "giro": "#F97316", "logro": "#22A06B"}

# Cuerpo: chispa de 4 puntas, simétrica, con tres puntitas abajo que sugieren "piecitos".
_CUERPO = (
    "M150 22 Q166 22 176 46 Q200 104 236 130 Q262 148 274 158 Q284 168 274 176 "
    "Q240 192 214 214 Q196 232 196 246 L208 268 Q214 282 200 282 Q186 278 176 266 "
    "L160 300 Q150 314 140 300 L124 266 Q114 278 100 282 Q86 282 92 268 L104 246 "
    "Q104 232 86 214 Q60 192 26 176 Q16 168 26 158 Q38 148 64 130 Q100 104 124 46 Q134 22 150 22 Z"
)


def svg(estado="guia", tam=120):
    d = _COLOR_DESTELLO.get(estado, "#FFC93C")
    return f"""
<svg class="chispa-svg ch-{estado}" width="{tam}" height="{int(tam*1.08)}" viewBox="0 0 300 324"
     role="img" aria-label="Chispa, la guía de Starwise">
  <defs>
    <linearGradient id="chG" x1="0.3" y1="0" x2="0.7" y2="1">
      <stop offset="0" stop-color="#FFD23F"/><stop offset="0.6" stop-color="#FFB703"/><stop offset="1" stop-color="#FB9A0B"/>
    </linearGradient>
    <clipPath id="chClip"><path d="{_CUERPO}"/></clipPath>
  </defs>
  <g class="ch-destello" fill="{d}">
    <rect x="34" y="40" width="20" height="46" rx="10" transform="rotate(-40 44 63)"/>
    <rect x="-6" y="98" width="42" height="18" rx="9" transform="rotate(14 15 107)"/>
    <rect x="246" y="40" width="20" height="46" rx="10" transform="rotate(40 256 63)"/>
    <rect x="264" y="98" width="42" height="18" rx="9" transform="rotate(-14 285 107)"/>
  </g>
  <g class="ch-cuerpo">
    <path d="{_CUERPO}" fill="url(#chG)"/>
    <g clip-path="url(#chClip)">
      <path d="M40 200 Q150 250 290 168 L300 330 L0 330 Z" fill="#F59E0B" opacity="0.55"/>
    </g>
    <rect x="112" y="70" width="24" height="54" rx="12" transform="rotate(35 124 97)" fill="#FFFFFF" opacity="0.4"/>
    <path d="M104 166 Q120 140 140 162 Q120 154 104 166 Z" fill="#6B3410" stroke="#6B3410" stroke-width="7" stroke-linejoin="round"/>
    <path d="M196 166 Q180 140 160 162 Q180 154 196 166 Z" fill="#6B3410" stroke="#6B3410" stroke-width="7" stroke-linejoin="round"/>
    <path d="M126 184 L174 184 Q170 222 150 224 Q130 222 126 184 Z" fill="#9A3412" stroke="#9A3412" stroke-width="4" stroke-linejoin="round"/>
    <path d="M134 210 Q150 196 166 210 Q160 222 150 223 Q140 222 134 210 Z" fill="#F97316"/>
  </g>
</svg>"""


def burbuja(texto, estado="guia", tam=110):
    """Chispa con un globo de diálogo. `texto` admite HTML simple (<b>, <br>)."""
    return (
        f'{ESTILOS}<div class="chispa-wrap">{svg(estado, tam)}'
        f'<div class="chispa-burbuja"><div class="chispa-nombre">Chispa</div>{texto}</div></div>'
    )


def sola(estado="guia", tam=160):
    return f'{ESTILOS}<div style="display:flex;justify-content:center">{svg(estado, tam)}</div>'
