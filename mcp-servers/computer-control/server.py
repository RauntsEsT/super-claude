#!/usr/bin/env python3
"""
Computer Control MCP Server v1.0
Annab Claude'ile hiire, klaviatuuri ja ekraani nägemise võime.

Tööriistad:
  screenshot()           — ekraanipilt
  get_windows()          — avatud aknad
  find_element()         — leia UI element
  click_element()        — klõpsa elementi nime järgi
  click_coords()         — klõpsa koordinaatidel (fallback)
  type_text()            — trüki tekst
  hotkey()               — kiirklahvid (ctrl+c, alt+tab, jne)
  key_press()            — üksik klahv (enter, escape, jne)
  focus_window()         — too aken fookusesse
  scroll()               — keri hiirerattaga
  mouse_move()           — liiguta hiirt
  get_screen_size()      — ekraani suurus
"""

import asyncio
import base64
import io
import sys
from typing import Optional

# pyautogui seadistus (FAILSAFE: hiir vasakusse ülanurka = peatus)
import pyautogui
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05  # väike viide toimingute vahel

import PIL.ImageGrab

try:
    from pywinauto import Desktop, Application
    HAS_PYWINAUTO = True
except Exception:
    HAS_PYWINAUTO = False

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("computer-control")


# ─── EKRAAN ───────────────────────────────────────────────────────────────────

@mcp.tool()
def screenshot(region: Optional[str] = None) -> list:
    """
    Tee ekraanipilt.
    region: valikuline "x,y,w,h" formaadis (nt "0,0,1920,1080") — jäta tühjaks täisekraaniks.
    Tagastab base64 PNG pildi.
    """
    if region:
        x, y, w, h = map(int, region.split(","))
        img = PIL.ImageGrab.grab(bbox=(x, y, x + w, y + h))
    else:
        img = PIL.ImageGrab.grab()

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()

    return [
        {"type": "text", "text": f"Ekraanipilt: {img.width}x{img.height}px"},
        {"type": "image", "data": b64, "mimeType": "image/png"},
    ]


@mcp.tool()
def get_screen_size() -> str:
    """Tagasta ekraani laius ja kõrgus pikslites."""
    w, h = pyautogui.size()
    return f"Ekraan: {w}x{h} pikslit"


# ─── AKNAD ────────────────────────────────────────────────────────────────────

@mcp.tool()
def get_windows() -> str:
    """Loetelu kõigist avatud ja nähtavatest akendest (pealkiri + klass)."""
    if not HAS_PYWINAUTO:
        return "VIGA: pywinauto pole saadaval"

    desktop = Desktop(backend="uia")
    lines = []
    for w in desktop.windows():
        try:
            title = w.window_text()
            cls = w.class_name()
            if title:
                lines.append(f"• [{cls}] {title}")
        except Exception:
            pass

    return "\n".join(lines) if lines else "Ühtegi akent ei leitud."


@mcp.tool()
def focus_window(title: str) -> str:
    """
    Too aken fookusesse pealkirja järgi (osaline vaste).
    title: akna pealkirja fragment (nt "Chrome", "Notepad")
    """
    if not HAS_PYWINAUTO:
        return "VIGA: pywinauto pole saadaval"

    try:
        app = Application(backend="uia").connect(title_re=f".*{title}.*")
        win = app.top_window()
        win.set_focus()
        return f"✓ Aken fookuses: '{win.window_text()}'"
    except Exception as e:
        return f"VIGA: {e}"


# ─── UI ELEMENDID ──────────────────────────────────────────────────────────────

@mcp.tool()
def find_element(window_title: str, element_name: str) -> str:
    """
    Leia UI element nime järgi pywinauto (UIA) abil.
    window_title: akna pealkirja fragment
    element_name: elemendi tekst/nimi
    Tagastab elemendi info (klass, asukoht).
    """
    if not HAS_PYWINAUTO:
        return "VIGA: pywinauto pole saadaval"

    try:
        app = Application(backend="uia").connect(title_re=f".*{window_title}.*")
        win = app.top_window()
        elem = win.child_window(title=element_name, found_index=0)
        rect = elem.rectangle()
        cls = elem.element_info.class_name
        return (
            f"✓ Element leitud: '{element_name}'\n"
            f"  Klass: {cls}\n"
            f"  Asukoht: ({rect.left},{rect.top}) — ({rect.right},{rect.bottom})\n"
            f"  Suurus: {rect.width()}x{rect.height()}px"
        )
    except Exception as e:
        return f"VIGA: '{element_name}' ei leitud aknas '{window_title}': {e}"


@mcp.tool()
def list_elements(window_title: str, depth: int = 3) -> str:
    """
    Loetele kõik UI elemendid aknas (debugging/avastamiseks).
    window_title: akna pealkirja fragment
    depth: otsimissügavus (1-5, default 3)
    """
    if not HAS_PYWINAUTO:
        return "VIGA: pywinauto pole saadaval"

    try:
        app = Application(backend="uia").connect(title_re=f".*{window_title}.*")
        win = app.top_window()
        lines = []

        def recurse(elem, level=0):
            if level > depth:
                return
            try:
                title = elem.window_text()
                cls = elem.element_info.class_name
                ctrl = elem.element_info.control_type
                if title or cls:
                    indent = "  " * level
                    lines.append(f"{indent}[{ctrl}] '{title}' ({cls})")
                for child in elem.children():
                    recurse(child, level + 1)
            except Exception:
                pass

        recurse(win)
        return "\n".join(lines[:100]) if lines else "Elemente ei leitud."
    except Exception as e:
        return f"VIGA: {e}"


# ─── HIIR ─────────────────────────────────────────────────────────────────────

@mcp.tool()
def click_element(window_title: str, element_name: str, button: str = "left") -> str:
    """
    Klõpsa UI elementi nime järgi (pywinauto UIA).
    window_title: akna pealkirja fragment
    element_name: elemendi tekst/nimi
    button: 'left' (default), 'right', 'double'
    """
    if not HAS_PYWINAUTO:
        return "VIGA: pywinauto pole saadaval"

    try:
        app = Application(backend="uia").connect(title_re=f".*{window_title}.*")
        win = app.top_window()
        elem = win.child_window(title=element_name, found_index=0)
        if button == "double":
            elem.double_click_input()
        elif button == "right":
            elem.right_click_input()
        else:
            elem.click_input()
        return f"✓ Klõpsasin '{element_name}' ({button})"
    except Exception as e:
        return f"VIGA: {e}"


@mcp.tool()
def click_coords(x: int, y: int, button: str = "left") -> str:
    """
    Klõpsa koordinaatidel (fallback kui elementi pole võimalik leida nimega).
    x, y: pikslite koordinaadid
    button: 'left' (default), 'right', 'middle'
    """
    pyautogui.click(x, y, button=button)
    return f"✓ Klõpsasin ({x}, {y}) {button} nupuga"


@mcp.tool()
def double_click_coords(x: int, y: int) -> str:
    """Topeltklõps koordinaatidel."""
    pyautogui.doubleClick(x, y)
    return f"✓ Topeltklõps ({x}, {y})"


@mcp.tool()
def mouse_move(x: int, y: int, duration: float = 0.2) -> str:
    """
    Liiguta hiirt koordinaatidele (ilma klõpsamata).
    duration: liigutuse kestus sekundites (default 0.2)
    """
    pyautogui.moveTo(x, y, duration=duration)
    return f"✓ Hiir liigutatud ({x}, {y})"


@mcp.tool()
def scroll(x: int, y: int, clicks: int = 3, direction: str = "up") -> str:
    """
    Keri hiirerattaga.
    x, y: koordinaadid kus kerida
    clicks: sammude arv (default 3)
    direction: 'up' või 'down'
    """
    amount = clicks if direction == "up" else -clicks
    pyautogui.scroll(amount, x=x, y=y)
    return f"✓ Kerisin {direction} {clicks} sammu ({x}, {y})"


# ─── KLAVIATUUR ───────────────────────────────────────────────────────────────

@mcp.tool()
def type_text(text: str, interval: float = 0.03) -> str:
    """
    Trüki tekst (saadab klahvivajutused aktiivsele aknale).
    text: trükitav tekst
    interval: viide klahvide vahel sekundites (default 0.03)
    Märkus: kasuta hotkey() erikohtade (enter, tab) jaoks.
    """
    pyautogui.write(text, interval=interval)
    return f"✓ Trükitud: '{text}'"


@mcp.tool()
def hotkey(keys: str) -> str:
    """
    Vajuta kiirklahve.
    keys: '+' eraldatud kombinatsioon, nt 'ctrl+c', 'alt+tab', 'ctrl+shift+esc', 'win+d'
    Toetatud klahvid: ctrl, alt, shift, win, tab, enter, escape, space, f1-f12, jne.
    """
    key_list = [k.strip() for k in keys.split("+")]
    pyautogui.hotkey(*key_list)
    return f"✓ Klahvikombinatsioon: {keys}"


@mcp.tool()
def key_press(key: str) -> str:
    """
    Vajuta üksikut klahvi.
    key: klahvi nimi, nt 'enter', 'escape', 'tab', 'space', 'backspace',
         'delete', 'home', 'end', 'pageup', 'pagedown', 'up', 'down', 'left', 'right',
         'f1'-'f12', 'printscreen', 'insert'
    """
    pyautogui.press(key)
    return f"✓ Klahv: {key}"


@mcp.tool()
def key_down(key: str) -> str:
    """Hoia klahvi all (kasuta key_up() et vabastada)."""
    pyautogui.keyDown(key)
    return f"✓ Klahv all: {key}"


@mcp.tool()
def key_up(key: str) -> str:
    """Vabasta eelnevalt alla vajutatud klahv."""
    pyautogui.keyUp(key)
    return f"✓ Klahv vabastatud: {key}"


# ─── KÄIVITAMINE ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Computer Control MCP Server v1.0 käivitub...", file=sys.stderr)
    mcp.run()
