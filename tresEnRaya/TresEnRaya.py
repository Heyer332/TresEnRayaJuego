import pygame
import sys
import math

#  CONSTANTES 
ANCHO_JUEGO  = 600    
ANCHO_ARBOL  = 520    
ANCHO_TOTAL  = ANCHO_JUEGO + ANCHO_ARBOL
ALTO         = 780
CELDA        = 180
MARGEN       = 30
FPS          = 60


MAX_P = "X"
MIN_P = "O"
VACIA = None


FONDO        = ( 15,  15,  25)
FONDO_PANEL  = ( 10,  10,  20)
LINEA        = ( 60,  60,  90)
COLOR_X      = (230,  80,  80)
COLOR_O      = ( 80, 180, 230)
DORADO       = (255, 215,   0)
TEXTO        = (220, 220, 230)
BTN_NORMAL   = ( 40,  40,  65)
BTN_HOVER    = ( 70,  70, 110)
BTN_BORDE    = ( 90,  90, 130)
GRIS         = (100, 100, 130)
PANEL_BORDE  = ( 50,  50,  80)


NODO_MAX     = ( 60,  20,  20)   
NODO_MIN     = ( 10,  30,  60)  
NODO_ELEGIDO = ( 80,  60,   0)   
NODO_PODADO  = ( 30,  30,  30)  
RAMA_NORMAL  = ( 50,  50,  80)
RAMA_ELEGIDA = (255, 200,   0)
BORDE_MAX    = (230,  80,  80)
BORDE_MIN    = ( 80, 180, 230)
BORDE_ELEG   = (255, 215,   0)
BORDE_PODADO = ( 60,  60,  60)

PANTALLA_MENU  = "menu"
PANTALLA_JUEGO = "juego"



#  LÓGICA DEL JUEGO
# ──────────────────────────────────────────────────────────────

def S0():
    return {"tablero": [VACIA] * 9, "turno": MAX_P}

def PLAYER(s):
    return s["turno"]

def ACTIONS(s):
    return [i for i, v in enumerate(s["tablero"]) if v is VACIA]

def RESULT(s, a):
    nuevo = s["tablero"][:]
    nuevo[a] = PLAYER(s)
    return {"tablero": nuevo, "turno": MIN_P if PLAYER(s) == MAX_P else MAX_P}

def _linea_ganadora(tablero):
    combos = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    for a, b, c in combos:
        if tablero[a] is not VACIA and tablero[a] == tablero[b] == tablero[c]:
            return tablero[a], [a, b, c]
    return None, None

def TERMINAL(s):
    g, _ = _linea_ganadora(s["tablero"])
    return g is not None or all(v is not VACIA for v in s["tablero"])

def UTILITY(s):
    g, _ = _linea_ganadora(s["tablero"])
    if g == MAX_P: return  1
    if g == MIN_P: return -1
    return 0

class Nodo:
    _id_counter = 0

    def __init__(self, estado, accion=None, profundidad=0, podado=False):
        Nodo._id_counter += 1
        self.id         = Nodo._id_counter
        self.estado     = estado
        self.accion     = accion       
        self.profundidad= profundidad
        self.valor      = None        
        self.alfa       = None
        self.beta       = None
        self.podado     = podado
        self.elegido    = False       
        self.hijos      = []
        self.x          = 0
        self.y          = 0


#  MINIMAX CONSTRUCCIÓN DE ÁRBOL

MAX_PROF = 4   
def MAX_VALUE_arbol(s, alfa, beta, nodo_padre, prof):
    nodo = Nodo(s, profundidad=prof)
    if nodo_padre:
        nodo_padre.hijos.append(nodo)

    if TERMINAL(s):
        nodo.valor = UTILITY(s)
        nodo.alfa  = alfa
        nodo.beta  = beta
        return nodo.valor, nodo

    v = -2
    for a in ACTIONS(s):
        hijo_s = RESULT(s, a)
        if prof < MAX_PROF:
            val, hijo_nodo = MIN_VALUE_arbol(hijo_s, alfa, beta, nodo, prof+1)
            hijo_nodo.accion = a
        else:
            val = MIN_VALUE_simple(hijo_s, alfa, beta)
            hijo_nodo = Nodo(hijo_s, accion=a, profundidad=prof+1)
            hijo_nodo.valor = val
            nodo.hijos.append(hijo_nodo)

        if val > v:
            v = val
        if v >= beta:
            for rest_a in ACTIONS(s)[ACTIONS(s).index(a)+1:]:
                pod = Nodo(RESULT(s, rest_a), accion=rest_a,
                           profundidad=prof+1, podado=True)
                pod.valor = None
                nodo.hijos.append(pod)
            break
        alfa = max(alfa, v)

    nodo.valor = v
    nodo.alfa  = alfa
    nodo.beta  = beta
    return v, nodo


def MIN_VALUE_arbol(s, alfa, beta, nodo_padre, prof):
    nodo = Nodo(s, profundidad=prof)
    if nodo_padre:
        nodo_padre.hijos.append(nodo)

    if TERMINAL(s):
        nodo.valor = UTILITY(s)
        nodo.alfa  = alfa
        nodo.beta  = beta
        return nodo.valor, nodo

    v = 2
    for a in ACTIONS(s):
        hijo_s = RESULT(s, a)
        if prof < MAX_PROF:
            val, hijo_nodo = MAX_VALUE_arbol(hijo_s, alfa, beta, nodo, prof+1)
            hijo_nodo.accion = a
        else:
            val = MAX_VALUE_simple(hijo_s, alfa, beta)
            hijo_nodo = Nodo(hijo_s, accion=a, profundidad=prof+1)
            hijo_nodo.valor = val
            nodo.hijos.append(hijo_nodo)

        if val < v:
            v = val
        if v <= alfa:
            for rest_a in ACTIONS(s)[ACTIONS(s).index(a)+1:]:
                pod = Nodo(RESULT(s, rest_a), accion=rest_a,
                           profundidad=prof+1, podado=True)
                pod.valor = None
                nodo.hijos.append(pod)
            break
        beta = min(beta, v)

    nodo.valor = v
    nodo.alfa  = alfa
    nodo.beta  = beta
    return v, nodo

def MAX_VALUE_simple(s, alfa, beta):
    if TERMINAL(s): return UTILITY(s)
    v = -2
    for a in ACTIONS(s):
        v = max(v, MIN_VALUE_simple(RESULT(s, a), alfa, beta))
        if v >= beta: return v
        alfa = max(alfa, v)
    return v

def MIN_VALUE_simple(s, alfa, beta):
    if TERMINAL(s): return UTILITY(s)
    v = 2
    for a in ACTIONS(s):
        v = min(v, MAX_VALUE_simple(RESULT(s, a), alfa, beta))
        if v <= alfa: return v
        beta = min(beta, v)
    return v


def MINIMAX_con_arbol(s):

    Nodo._id_counter = 0
    raiz = Nodo(s, profundidad=0)

    mejor_val, mejor_acc = 2, None
    for a in ACTIONS(s):
        hijo_s = RESULT(s, a)
        val, hijo_nodo = MAX_VALUE_arbol(hijo_s, -2, 2, raiz, 1)
        hijo_nodo.accion = a
        if val < mejor_val:
            mejor_val = val
            mejor_acc = a

    raiz.valor = mejor_val

    def marcar_elegida(nodo, acc_objetivo):
        for h in nodo.hijos:
            if h.accion == acc_objetivo:
                h.elegido = True
                return
    marcar_elegida(raiz, mejor_acc)

    return mejor_acc, raiz


R_NODO    = 16   
SEP_Y     = 70 
PANEL_X   = ANCHO_JUEGO + 10   

def calcular_posiciones(nodo, x_min, x_max, y):
    nodo.x = (x_min + x_max) / 2
    nodo.y = y
    if not nodo.hijos:
        return
    n = len(nodo.hijos)
    ancho = x_max - x_min
    paso  = ancho / n
    for i, h in enumerate(nodo.hijos):
        calcular_posiciones(h, x_min + i*paso, x_min + (i+1)*paso, y + SEP_Y)

#  DIBUJO DEL ÁRBOL

def dibujar_arbol_nodos(pantalla, nodo, fuente_nodo, offset_y, scroll_y=0):
    ny = nodo.y + offset_y - scroll_y

    for hijo in nodo.hijos:
        hy = hijo.y + offset_y - scroll_y

        if hijo.elegido:
            color_rama = RAMA_ELEGIDA
            grosor     = 3
        elif hijo.podado:
            color_rama = (50, 50, 60)
            grosor     = 1
        else:
            color_rama = RAMA_NORMAL
            grosor     = 1

        pygame.draw.line(pantalla, color_rama,
                         (int(nodo.x), int(ny)),
                         (int(hijo.x), int(hy)), grosor)

        dibujar_arbol_nodos(pantalla, hijo, fuente_nodo, offset_y, scroll_y)

    es_max = (PLAYER(nodo.estado) == MAX_P)
    if nodo.podado:
        fondo_n, borde_n = NODO_PODADO, BORDE_PODADO
    elif nodo.elegido:
        fondo_n, borde_n = NODO_ELEGIDO, BORDE_ELEG
    elif es_max:
        fondo_n, borde_n = NODO_MAX, BORDE_MAX
    else:
        fondo_n, borde_n = NODO_MIN, BORDE_MIN

    pygame.draw.circle(pantalla, fondo_n,  (int(nodo.x), int(ny)), R_NODO)
    pygame.draw.circle(pantalla, borde_n,  (int(nodo.x), int(ny)), R_NODO, 2)

    if nodo.valor is not None and not nodo.podado:
        val_str = ("+1" if nodo.valor == 1
                   else "-1" if nodo.valor == -1
                   else " 0")
        color_val = (COLOR_X if nodo.valor == 1
                     else COLOR_O if nodo.valor == -1
                     else DORADO)
        sv = fuente_nodo.render(val_str, True, color_val)
        pantalla.blit(sv, sv.get_rect(center=(int(nodo.x), int(ny))))
    elif nodo.podado:
        sx = fuente_nodo.render("X", True, (80, 80, 80))
        pantalla.blit(sx, sx.get_rect(center=(int(nodo.x), int(ny))))

    if nodo.accion is not None and not nodo.podado:
        fila_a, col_a = divmod(nodo.accion, 3)
        lbl = f"[{fila_a},{col_a}]"
        sa  = fuente_nodo.render(lbl, True, GRIS)
        pantalla.blit(sa, sa.get_rect(centerx=int(nodo.x), bottom=int(ny)-R_NODO-2))


def dibujar_panel_arbol(pantalla, fuentes, raiz, scroll_y):
    _, f_sub, _, f_chica = fuentes
    f_nodo = pygame.font.SysFont("segoeui", 11, bold=True)

    panel_rect = pygame.Rect(ANCHO_JUEGO, 0, ANCHO_ARBOL, ALTO)
    pygame.draw.rect(pantalla, FONDO_PANEL, panel_rect)
    pygame.draw.line(pantalla, PANEL_BORDE, (ANCHO_JUEGO, 0), (ANCHO_JUEGO, ALTO), 2)

    titulo_surf = f_sub.render("Árbol de decisión — Minimax", True, TEXTO)
    pantalla.blit(titulo_surf, titulo_surf.get_rect(
        centerx=ANCHO_JUEGO + ANCHO_ARBOL//2, top=8))

    leyenda_y = 34
    items = [
        (BORDE_MAX,    "Nodo MAX (X)"),
        (BORDE_MIN,    "Nodo MIN / IA (O)"),
        (BORDE_ELEG,   "Rama elegida"),
        (BORDE_PODADO, "Podado (α-β)"),
    ]
    lx = ANCHO_JUEGO + 12
    for color, txt in items:
        pygame.draw.circle(pantalla, color, (lx + 6, leyenda_y + 6), 6)
        s = f_chica.render(txt, True, GRIS)
        pantalla.blit(s, (lx + 16, leyenda_y))
        lx += 130
        if lx > ANCHO_TOTAL - 80:
            lx  = ANCHO_JUEGO + 12
            leyenda_y += 18

    sep_y = leyenda_y + 20
    pygame.draw.line(pantalla, PANEL_BORDE,
                     (ANCHO_JUEGO + 10, sep_y),
                     (ANCHO_TOTAL  - 10, sep_y), 1)

    if raiz is None:
        msg = f_sub.render("(esperando movimiento de la IA...)", True, GRIS)
        pantalla.blit(msg, msg.get_rect(
            centerx=ANCHO_JUEGO + ANCHO_ARBOL//2, top=sep_y + 20))
        return

    area_arbol = pygame.Rect(ANCHO_JUEGO, sep_y + 4, ANCHO_ARBOL, ALTO - sep_y - 4)
    pantalla.set_clip(area_arbol)

    offset_x = ANCHO_JUEGO + 20
    x_min    = offset_x
    x_max    = ANCHO_TOTAL - 20
    offset_y = sep_y + R_NODO + 14

    calcular_posiciones(raiz, x_min, x_max, 0)
    dibujar_arbol_nodos(pantalla, raiz, f_nodo, offset_y, scroll_y)

    pantalla.set_clip(None)

    # Indicador de scroll
    s_scroll = f_chica.render("↑↓ scroll  |  rueda del ratón", True, GRIS)
    pantalla.blit(s_scroll, s_scroll.get_rect(
        centerx=ANCHO_JUEGO + ANCHO_ARBOL//2, bottom=ALTO - 4))


#panel del juego

def texto_centrado_en(pantalla, fuente, texto, y, color, cx):
    surf = fuente.render(texto, True, color)
    rect = surf.get_rect(centerx=cx, top=y)
    pantalla.blit(surf, rect)

def dibujar_boton(pantalla, fuente, rect, label, hover):
    color = BTN_HOVER if hover else BTN_NORMAL
    pygame.draw.rect(pantalla, color, rect, border_radius=12)
    pygame.draw.rect(pantalla, BTN_BORDE, rect, 2, border_radius=12)
    txt = fuente.render(label, True, TEXTO)
    pantalla.blit(txt, txt.get_rect(center=rect.center))

#  PANTALLA: MENÚ

def pantalla_menu(pantalla, fuentes, mouse, click):
    f_titulo, f_sub, f_btn, f_chica = fuentes
    cx = ANCHO_TOTAL // 2

    pantalla.fill(FONDO)

    a = pygame.Surface((ANCHO_TOTAL, ALTO), pygame.SRCALPHA)
    for i in (1, 2):
        x = MARGEN + i * CELDA
        pygame.draw.rect(a, (60,60,90,30), (x-3, 0, 6, ALTO))
        y = 220 + i * CELDA
        pygame.draw.rect(a, (60,60,90,30), (0, y-3, ANCHO_TOTAL, 6))
    pantalla.blit(a, (0, 0))

    t = f_titulo.render("3 EN RAYA", True, TEXTO)
    pantalla.blit(t, t.get_rect(centerx=cx, top=80))
    s = f_sub.render("Minimax  +  Poda Alfa-Beta", True, GRIS)
    pantalla.blit(s, s.get_rect(centerx=cx, top=136))

    pygame.draw.rect(pantalla, DORADO, (cx-55, 178, 110, 3))

    s2 = f_sub.render("Elige un modo de juego", True, TEXTO)
    pantalla.blit(s2, s2.get_rect(centerx=cx, top=200))

    r_ia = pygame.Rect(cx - 175, 258, 350, 68)
    h_ia = r_ia.collidepoint(mouse)
    dibujar_boton(pantalla, f_btn, r_ia, "Jugador  vs  IA  (con árbol)", h_ia)
    d1 = f_chica.render("Tu = X  |  IA = O  +  visualización del árbol Minimax", True, GRIS)
    pantalla.blit(d1, d1.get_rect(centerx=cx, top=335))

    r_2j = pygame.Rect(cx - 175, 385, 350, 68)
    h_2j = r_2j.collidepoint(mouse)
    dibujar_boton(pantalla, f_btn, r_2j, "Jugador  vs  Jugador", h_2j)
    d2 = f_chica.render("X y O se turnan en el mismo equipo", True, GRIS)
    pantalla.blit(d2, d2.get_rect(centerx=cx, top=462))

    bx, by, d = cx-220, 320, 26
    pygame.draw.line(pantalla, (*COLOR_X,100),(bx-d,by-d),(bx+d,by+d),9)
    pygame.draw.line(pantalla, (*COLOR_X,100),(bx+d,by-d),(bx-d,by+d),9)
    pygame.draw.circle(pantalla, (*COLOR_O,100),(cx+220,320),28,9)

    pie = f_chica.render("Algoritmo: Minimax con poda Alfa-Beta", True, GRIS)
    pantalla.blit(pie, pie.get_rect(centerx=cx, bottom=ALTO-8))

    if click:
        if h_ia:  return "vs_ia"
        if h_2j:  return "vs_jugador"
    return None

#  PANTALLA: JUEGO (tablero izquierdo + árbol derecho)

def dibujar_tablero(pantalla):
    for i in (1, 2):
        x = MARGEN + i * CELDA
        pygame.draw.rect(pantalla, LINEA, (x-3, MARGEN, 6, CELDA*3))
        y = MARGEN + i * CELDA
        pygame.draw.rect(pantalla, LINEA, (MARGEN, y-3, CELDA*3, 6))

def dibujar_X(pantalla, cx, cy, color, grosor=13):
    d = CELDA//2 - 33
    pygame.draw.line(pantalla, color, (cx-d, cy-d), (cx+d, cy+d), grosor)
    pygame.draw.line(pantalla, color, (cx+d, cy-d), (cx-d, cy+d), grosor)
    for dx, dy in ((-d,-d),(d,d),(d,-d),(-d,d)):
        pygame.draw.circle(pantalla, color, (cx+dx, cy+dy), grosor//2)

def dibujar_O(pantalla, cx, cy, color):
    r = CELDA//2 - 28
    pygame.draw.circle(pantalla, color, (cx, cy), r, 13)

def dibujar_fichas(pantalla, tablero, linea_gan):
    for i, v in enumerate(tablero):
        if v is VACIA: continue
        fila, col = divmod(i, 3)
        cx = MARGEN + col*CELDA + CELDA//2
        cy = MARGEN + fila*CELDA + CELDA//2
        es_gan = linea_gan is not None and i in linea_gan
        color  = DORADO if es_gan else (COLOR_X if v == MAX_P else COLOR_O)
        if v == MAX_P: dibujar_X(pantalla, cx, cy, color)
        else:          dibujar_O(pantalla, cx, cy, color)

def dibujar_hover(pantalla, col, fila, tablero):
    if tablero[fila*3+col] is not VACIA: return
    x = MARGEN + col*CELDA + 4
    y = MARGEN + fila*CELDA + 4
    s = CELDA - 8
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((255,255,255,18))
    pantalla.blit(surf, (x, y))

def pantalla_juego(pantalla, fuentes, mouse, click,
                   scroll_event, ej):

    _, f_sub, f_btn, f_chica = fuentes

    modo      = ej["modo"]
    estado    = ej["estado"]
    linea_gan = ej["linea_gan"]
    ia_espera = ej["ia_espera"]
    raiz      = ej["raiz_arbol"]
    scroll_y  = ej["scroll_y"]

    scroll_y = max(0, scroll_y + scroll_event * 30)
    ej["scroll_y"] = scroll_y

    #  Turno humano 
    es_humano = (not TERMINAL(estado) and (
        modo == "vs_jugador" or
        (modo == "vs_ia" and PLAYER(estado) == MAX_P)
    ))

    if es_humano and click:
        mx, my = mouse
        en_tab = (MARGEN < mx < MARGEN + CELDA*3 and
                  MARGEN < my < MARGEN + CELDA*3)
        if en_tab:
            col  = (mx - MARGEN) // CELDA
            fila = (my - MARGEN) // CELDA
            acc  = fila*3 + col
            if acc in ACTIONS(estado):
                estado = RESULT(estado, acc)
                _, linea_gan = _linea_ganadora(estado["tablero"])
                if not TERMINAL(estado) and modo == "vs_ia":
                    ia_espera = 40
                    raiz      = None   # limpiar árbol mientras piensa

    # Turno IA 
    if (modo == "vs_ia" and not TERMINAL(estado)
            and PLAYER(estado) == MIN_P):
        if ia_espera > 0:
            ia_espera -= 1
        else:
            acc, raiz = MINIMAX_con_arbol(estado)
            estado = RESULT(estado, acc)
            _, linea_gan = _linea_ganadora(estado["tablero"])
            scroll_y = 0
            ej["scroll_y"] = 0

    ej["estado"]     = estado
    ej["linea_gan"]  = linea_gan
    ej["ia_espera"]  = ia_espera
    ej["raiz_arbol"] = raiz

    # Dibujar panel izquierdo (juego)
    pantalla.fill(FONDO)

    pantalla.set_clip(pygame.Rect(0, 0, ANCHO_JUEGO, ALTO))

    dibujar_tablero(pantalla)
    dibujar_fichas(pantalla, estado["tablero"], linea_gan)

    if es_humano:
        mx, my = mouse
        if (MARGEN < mx < MARGEN + CELDA*3 and
                MARGEN < my < MARGEN + CELDA*3):
            col  = (mx - MARGEN) // CELDA
            fila = (my - MARGEN) // CELDA
            dibujar_hover(pantalla, col, fila, estado["tablero"])

    if TERMINAL(estado):
        u = UTILITY(estado)
        if u == 1:   msg, mc = ("¡Gano X!"  if modo=="vs_jugador" else "¡Ganaste!"),  COLOR_X
        elif u == -1:msg, mc = ("¡Gano O!"  if modo=="vs_jugador" else "¡Gano la IA!"), COLOR_O
        else:        msg, mc = "¡Empate!", DORADO
    elif modo=="vs_ia" and PLAYER(estado)==MIN_P and ia_espera>0:
        msg, mc = "IA pensando...", COLOR_O
    elif PLAYER(estado)==MAX_P:
        msg, mc = ("Turno de X" if modo=="vs_jugador" else "Tu turno (X)"), COLOR_X
    else:
        msg, mc = ("Turno de O" if modo=="vs_jugador" else "Turno IA (O)"), COLOR_O

    cx_j = ANCHO_JUEGO // 2
    texto_centrado_en(pantalla, f_sub, msg, 578, mc, cx_j)

    modo_lbl = ("Jugador vs Jugador" if modo=="vs_jugador"
                else "Jugador vs IA (Minimax + alfa-beta)")
    texto_centrado_en(pantalla, f_chica, modo_lbl, 604, GRIS, cx_j)

    r_rei = pygame.Rect(cx_j - 180, 630, 160, 42)
    r_men = pygame.Rect(cx_j +  20, 630, 160, 42)
    h_rei = r_rei.collidepoint(mouse)
    h_men = r_men.collidepoint(mouse)
    dibujar_boton(pantalla, f_btn, r_rei, "Reiniciar", h_rei)
    dibujar_boton(pantalla, f_btn, r_men, "<- Menu",   h_men)

    texto_centrado_en(pantalla, f_chica,
                      "Tu=X  |  IA=O  |  Minimax+alfa-beta",
                      ALTO - 16, GRIS, cx_j)

    pantalla.set_clip(None)

    # Dibujar panel derecho (árbol)
    if modo == "vs_ia":
        dibujar_panel_arbol(pantalla, fuentes, raiz, scroll_y)

    if click:
        if h_rei:
            ej["estado"]     = S0()
            ej["linea_gan"]  = None
            ej["ia_espera"]  = 0
            ej["raiz_arbol"] = None
            ej["scroll_y"]   = 0
        if h_men:
            return True

    return False


def main():
    pygame.init()

    # Ventana grande (juego + árbol) desde el inicio
    pantalla = pygame.display.set_mode((ANCHO_TOTAL, ALTO))
    pygame.display.set_caption("3 en Raya — Minimax + árbol de decisión")
    reloj = pygame.time.Clock()

    fuentes = (
        pygame.font.SysFont("segoeui", 44, bold=True),
        pygame.font.SysFont("segoeui", 20),
        pygame.font.SysFont("segoeui", 19),
        pygame.font.SysFont("segoeui", 13),
    )

    pantalla_actual = PANTALLA_MENU
    ej = {}

    while True:
        mouse        = pygame.mouse.get_pos()
        click        = False
        scroll_event = 0

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1: click = True
                if evento.button == 4: scroll_event = -1
                if evento.button == 5: scroll_event =  1
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:   scroll_event = -1
                if evento.key == pygame.K_DOWN: scroll_event =  1

        if pantalla_actual == PANTALLA_MENU:
            modo = pantalla_menu(pantalla, fuentes, mouse, click)
            if modo:
                ej = {
                    "modo":      modo,
                    "estado":    S0(),
                    "linea_gan": None,
                    "ia_espera": 0,
                    "raiz_arbol":None,
                    "scroll_y":  0,
                }
                pantalla_actual = PANTALLA_JUEGO

        elif pantalla_actual == PANTALLA_JUEGO:
            volver = pantalla_juego(
                pantalla, fuentes, mouse, click, scroll_event, ej
            )
            if volver:
                pantalla_actual = PANTALLA_MENU

        pygame.display.flip()
        reloj.tick(FPS)


if __name__ == "__main__":
    main()