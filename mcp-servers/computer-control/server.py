#!/usr/bin/env python3
"""
Computer Control MCP Server v2.0
Annab Claude'ile hiire, klaviatuuri, ekraani nägemise, UI Automationi, OCR-i ja aknasündmused.

v2 muudatused (2026-11-13):
  - screenshot() tagastab päris MCP pildi (JPEG, vähendatud) + skaala; region/window/zoom
  - act(): mitu tegevust + ootamine (ekraan rahuneb / aknasündmus) + pilt ÜHES kutses
  - wait_for_change(): oota kuni ekraan muutub
  - get_windows()/focus_window(): Win32 EnumWindows (ka modaalsed dialoogid), hwnd, töökindel fookus
  - click_coords(): "inimlik" klõps (hover + hold), expect_text klõpsukaitse, space="shot"
  - ui_tree()/click_ui(): UIA puu koos rect'idega, klõps id/nime järgi (Invoke kui võimalik)
  - ocr()/find_text()/click_text(): Windowsi sisseehitatud OCR
  - events()/wait_for_window(): aknasündmuste jälgija (SetWinEventHook)
Varukoopia: server.py.bak-2026-11-13
"""

import asyncio
import ctypes
import ctypes.wintypes as wt
import io
import os
import sys
import time
from typing import Optional, Any

import pyautogui
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.02

import mss
from PIL import Image as PILImage, ImageChops, ImageDraw

try:
    from pywinauto import Desktop
    from pywinauto.controls.uiawrapper import UIAWrapper
    from pywinauto.uia_element_info import UIAElementInfo
    HAS_PYWINAUTO = True
except Exception:
    HAS_PYWINAUTO = False

try:
    import winrt.windows.media.ocr as _ocr
    import winrt.windows.globalization as _glob
    from winrt.windows.graphics.imaging import SoftwareBitmap, BitmapPixelFormat
    from winrt.windows.storage.streams import DataWriter
    HAS_OCR = True
except Exception:
    HAS_OCR = False

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import winevents

from mcp.server.fastmcp import FastMCP, Image

mcp = FastMCP("computer-control")
user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

WATCHER = winevents.start_watcher()

# viimase pildi teisendus: ekraan = origin + shot / scale
_LAST = {"ox": 0, "oy": 0, "scale": 1.0}


# ─── PÜÜDMINE ─────────────────────────────────────────────────────────────────

def _named_monitors():
    """{'left': rect, 'primary': rect, 'right': rect, ...} asukoha järgi (x järjekorras)."""
    with mss.mss() as s:
        mons = sorted(s.monitors[1:], key=lambda m: (m["left"], m["top"]))
    out = {}
    prim_i = next((i for i, m in enumerate(mons) if m["left"] == 0 and m["top"] == 0), 0)
    for i, m in enumerate(mons):
        r = (m["left"], m["top"], m["width"], m["height"])
        if i == prim_i:
            out["primary"] = r
        elif i < prim_i:
            out["left" if i == prim_i - 1 else f"left{prim_i - i}"] = r
        else:
            out["right" if i == prim_i + 1 else f"right{i - prim_i}"] = r
    return out


def _monitor_of_point(x, y):
    for n, (mx, my, mw, mh) in _named_monitors().items():
        if mx <= x < mx + mw and my <= y < my + mh:
            return n
    return "?"


def _monitor_rect(monitor="primary"):
    """
    'primary' | 'left' | 'right' | 'active' (fookuses akna monitor) | 'mouse' (hiire monitor) | 'all'
    """
    monitor = str(monitor or "primary").lower()
    if monitor == "all":
        with mss.mss() as s:
            m = s.monitors[0]
        return (m["left"], m["top"], m["width"], m["height"])
    named = _named_monitors()
    if monitor in ("active", "mouse"):
        if monitor == "active":
            fg = user32.GetForegroundWindow()
            x, y, w, h = _window_rect(fg) if fg else (0, 0, 1, 1)
            px, py = x + w // 2, y + h // 2
        else:
            px, py = pyautogui.position()
        monitor = _monitor_of_point(px, py)
    return named.get(monitor, named.get("primary"))


def _grab(region=None) -> PILImage.Image:
    """region = (x, y, w, h) ekraanikoordinaatides; None = põhimonitor (0,0)."""
    if not region:
        region = _monitor_rect("primary")
    x, y, w, h = region
    with mss.mss() as s:
        raw = s.grab({"left": int(x), "top": int(y), "width": int(w), "height": int(h)})
    return PILImage.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")


def _parse_region(region) -> Optional[tuple]:
    if not region:
        return None
    if isinstance(region, (list, tuple)):
        return tuple(int(v) for v in region)
    return tuple(int(float(v)) for v in str(region).split(","))


def _window_rect(hwnd) -> tuple:
    r = wt.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(r))
    return (r.left, r.top, r.right - r.left, r.bottom - r.top)


def _encode(img: PILImage.Image, origin=(0, 0), max_width=1280, quality=70, grayscale=False):
    scale = 1.0
    if max_width and img.width > max_width:
        scale = max_width / img.width
        img = img.resize((max_width, max(1, round(img.height * scale))), PILImage.LANCZOS)
    if grayscale:
        img = img.convert("L")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    _LAST.update(ox=origin[0], oy=origin[1], scale=scale)
    note = (f"pilt {img.width}x{img.height}, ala algus=({origin[0]},{origin[1]}), skaala={scale:.4f}"
            f" | ekraan = algus + pildi_px / skaala  (või kasuta space='shot')")
    return note, Image(data=buf.getvalue(), format="jpeg")


def _to_screen(x, y, space="screen"):
    if space == "shot":
        return (round(_LAST["ox"] + x / _LAST["scale"]), round(_LAST["oy"] + y / _LAST["scale"]))
    return (int(x), int(y))


def _shot(region=None, window=None, max_width=1280, quality=70, grayscale=False, monitor="primary"):
    reg = _parse_region(region)
    if window and not reg:
        hw = _resolve_hwnd(window)
        if hw:
            reg = _clip_to_monitor(_window_rect(hw))
    if not reg:
        reg = _monitor_rect(monitor)
    img = _grab(reg)
    return _encode(img, (reg[0], reg[1]), max_width, quality, grayscale)


def _clip_to_monitor(r):
    """Lõika akna rect (maksimeeritud aknal -7..-8 serv) monitori piiridesse."""
    x, y, w, h = r
    cx, cy = x + w // 2, y + h // 2
    with mss.mss() as s:
        for m in s.monitors[1:]:
            if m["left"] <= cx < m["left"] + m["width"] and m["top"] <= cy < m["top"] + m["height"]:
                x0, y0 = max(x, m["left"]), max(y, m["top"])
                x1 = min(x + w, m["left"] + m["width"]); y1 = min(y + h, m["top"] + m["height"])
                return (x0, y0, x1 - x0, y1 - y0)
    return r


@mcp.tool()
def screenshot(region: Optional[str] = None, window: Optional[str] = None, max_width: int = 1280,
               quality: int = 70, grayscale: bool = False, monitor: str = "primary") -> list:
    """
    Ekraanipilt päris pildina (JPEG, vähendatud).
    region: "x,y,w,h" ekraanikoordinaatides (täisresolutsioonis väljalõige)
    window: akna pealkirja fragment või hwnd (0x...) — pildista ainult see aken
    monitor: 'primary' (vaikimisi) | 'left' | 'right' | 'active' (fookuses akna monitor) | 'mouse' | 'all'
    Kõik koordinaadid on ühised virtuaalse töölaua koordinaadid (vasak monitor = negatiivne x).
    max_width: pildi max laius (vaikimisi 1280; 0 = täissuurus)
    Tekstis tagastatakse skaala; klõpsa kas ekraanikoordinaatidega või space='shot'.
    """
    note, img = _shot(region, window, max_width, quality, grayscale, monitor)
    return [note, img]


@mcp.tool()
def monitors() -> str:
    """Monitorid nimedega (left/primary/right), asukohad ja millised aknad igal on."""
    wins = _enum_windows()
    lines = []
    for n, (x, y, w, h) in _named_monitors().items():
        on = [wi["title"][:50] for wi in wins if not wi["min"] and wi["owner"] == 0 and
              _monitor_of_point(wi["rect"][0] + wi["rect"][2] // 2, wi["rect"][1] + wi["rect"][3] // 2) == n]
        lines.append(f"{n}: x={x}..{x + w - 1}, y={y}..{y + h - 1} ({w}x{h}) aknad: {on[:6]}")
    fg = user32.GetForegroundWindow()
    if fg:
        fx, fy, fw, fh = _window_rect(fg)
        lines.append(f"fookuses: \"{winevents.window_text(fg)}\" monitoril {_monitor_of_point(fx + fw // 2, fy + fh // 2)}")
    return "\n".join(lines)


@mcp.tool()
def zoom(x: int, y: int, size: int = 200, factor: float = 2.0, space: str = "screen") -> list:
    """
    Suurendatud väljalõige punkti ümber (täisresolutsioon) + punase ristiga sihtpunkt.
    Kasuta enne täpset klõpsu: kas rist on õige nupu peal?
    """
    sx, sy = _to_screen(x, y, space)
    half = size // 2
    img = _grab((sx - half, sy - half, size, size))
    img = img.resize((int(size * factor), int(size * factor)), PILImage.LANCZOS)
    d = ImageDraw.Draw(img)
    c = int(half * factor)
    d.line((c - 12, c, c + 12, c), fill=(255, 0, 0), width=2)
    d.line((c, c - 12, c, c + 12), fill=(255, 0, 0), width=2)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=80)
    _LAST.update(ox=sx - half, oy=sy - half, scale=factor)
    return [f"zoom ({sx},{sy}) ±{half}px x{factor}; rist = sihtpunkt", Image(data=buf.getvalue(), format="jpeg")]


@mcp.tool()
def get_screen_size() -> str:
    """Tagasta ekraani laius ja kõrgus pikslites."""
    w, h = pyautogui.size()
    return f"Ekraan: {w}x{h} pikslit"


# ─── OOTAMINE ─────────────────────────────────────────────────────────────────

def _small(region=None):
    img = _grab(region).convert("L")
    return img.resize((max(1, img.width // 4), max(1, img.height // 4)))


def _diff_bbox(a, b, thresh=12, min_frac=0.0005):
    """Muutunud ala bbox; väikesed muutused (kursor, spinner) ignoreeritakse."""
    d = ImageChops.difference(a, b).point(lambda v: 255 if v > thresh else 0)
    bbox = d.getbbox()
    if bbox is None:
        return None
    changed = d.histogram()[255]
    if changed < max(4, min_frac * a.width * a.height):
        return None
    return bbox


def _fg_region():
    fg = user32.GetForegroundWindow()
    if not fg:
        return None
    return _clip_to_monitor(_window_rect(fg))


def _wait_stable(region=None, timeout=3.0, interval=0.12, need=2) -> str:
    if region is None:
        region = _fg_region()
    t0 = time.time()
    prev = _small(region)
    calm = 0
    while time.time() - t0 < timeout:
        time.sleep(interval)
        cur = _small(region)
        if _diff_bbox(prev, cur) is None:
            calm += 1
            if calm >= need:
                return f"stabiilne {time.time() - t0:.2f}s"
        else:
            calm = 0
        prev = cur
    return f"ei rahunenud {timeout:.1f}s jooksul"


@mcp.tool()
def wait_for_change(region: Optional[str] = None, timeout: float = 10.0, then_screenshot: bool = True,
                    monitor: str = "active") -> list:
    """
    Oota kuni ekraan (või region "x,y,w,h") muutub, siis oota rahunemist ja tee pilt.
    Tagastab muutunud ala (ekraanikoordinaadid).
    """
    reg = _parse_region(region) or _monitor_rect(monitor)
    t0 = time.time()
    base = _small(reg)
    bbox = None
    while time.time() - t0 < timeout:
        time.sleep(0.1)
        bbox = _diff_bbox(base, _small(reg))
        if bbox:
            break
    if not bbox:
        return [f"muutust ei tulnud {timeout:.1f}s jooksul"]
    ox, oy = (reg[0], reg[1]) if reg else (0, 0)
    ch = (ox + bbox[0] * 4, oy + bbox[1] * 4, (bbox[2] - bbox[0]) * 4, (bbox[3] - bbox[1]) * 4)
    st = _wait_stable(reg)
    out = [f"muutus {time.time() - t0:.2f}s pärast, ala x,y,w,h={ch}; {st}"]
    if then_screenshot:
        out += list(_shot(",".join(map(str, reg))))
    return out


# ─── AKNAD (Win32) ────────────────────────────────────────────────────────────

EnumWindowsProc = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
GW_OWNER, GW_ENABLEDPOPUP = 4, 6


def _enum_windows(include_untitled=False):
    res = []

    def cb(hwnd, lp):
        if not user32.IsWindowVisible(hwnd):
            return True
        title = winevents.window_text(hwnd)
        if not title and not include_untitled:
            return True
        x, y, w, h = _window_rect(hwnd)
        if w <= 1 or h <= 1:
            return True
        res.append({
            "hwnd": int(hwnd), "title": title, "cls": winevents.class_name(hwnd),
            "exe": winevents.process_name(hwnd), "rect": (x, y, w, h),
            "owner": int(user32.GetWindow(hwnd, GW_OWNER) or 0),
            "popup": int(user32.GetWindow(hwnd, GW_ENABLEDPOPUP) or 0),
            "min": bool(user32.IsIconic(hwnd)),
        })
        return True

    user32.EnumWindows(EnumWindowsProc(cb), 0)
    return res


def _resolve_hwnd(window) -> Optional[int]:
    if window is None:
        return None
    s = str(window).strip()
    if s.lower().startswith("0x"):
        return int(s, 16)
    if s.isdigit():
        return int(s)
    cands = [w for w in _enum_windows() if s.lower() in (w["title"] + " " + w["exe"]).lower()]
    if not cands:
        return None
    # eelista omanikuta (põhi)akent, siis suurimat
    cands.sort(key=lambda w: (w["owner"] != 0, -(w["rect"][2] * w["rect"][3])))
    return cands[0]["hwnd"]


@mcp.tool()
def get_windows(filter: Optional[str] = None) -> str:
    """
    Kõik nähtavad aknad (ka modaalsed dialoogid ja owned aknad): hwnd, klass, pealkiri, protsess, rect.
    filter: pealkirja/protsessi fragment. 'popup=' näitab akna aktiivset modaalset dialoogi.
    """
    fg = int(user32.GetForegroundWindow() or 0)
    lines = []
    for w in _enum_windows():
        if filter and filter.lower() not in (w["title"] + " " + w["exe"] + " " + w["cls"]).lower():
            continue
        extra = []
        if w["hwnd"] == fg:
            extra.append("FOOKUS")
        if w["owner"]:
            extra.append(f"owner=0x{w['owner']:x}")
        if w["popup"] and w["popup"] != w["hwnd"]:
            extra.append(f"popup=0x{w['popup']:x} \"{winevents.window_text(w['popup'])}\"")
        if w["min"]:
            extra.append("minimeeritud")
        x, y, ww, hh = w["rect"]
        mon = "-" if w["min"] else _monitor_of_point(x + ww // 2, y + hh // 2)
        lines.append(f"0x{w['hwnd']:x} [{w['cls']}] \"{w['title']}\" ({w['exe']}) monitor={mon} rect={x},{y},{ww},{hh} {' '.join(extra)}")
    return "\n".join(lines) if lines else "Ühtegi akent ei leitud."


def _force_foreground(hwnd) -> bool:
    fg = user32.GetForegroundWindow()
    if fg == hwnd:
        return True
    cur_tid = kernel32.GetCurrentThreadId()
    fg_tid = user32.GetWindowThreadProcessId(fg, None) if fg else 0
    tgt_tid = user32.GetWindowThreadProcessId(hwnd, None)
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, 9)  # SW_RESTORE
    user32.keybd_event(0x12, 0, 0, 0)  # ALT alla/üles: lubab SetForegroundWindow
    user32.keybd_event(0x12, 0, 2, 0)
    attached = []
    for tid in {fg_tid, tgt_tid}:
        if tid and tid != cur_tid and user32.AttachThreadInput(cur_tid, tid, True):
            attached.append(tid)
    user32.BringWindowToTop(hwnd)
    user32.SetForegroundWindow(hwnd)
    user32.SetFocus(hwnd)
    for tid in attached:
        user32.AttachThreadInput(cur_tid, tid, False)
    time.sleep(0.15)
    return user32.GetForegroundWindow() == hwnd


@mcp.tool()
def focus_window(title: str) -> str:
    """
    Too aken esiplaanile (pealkirja/protsessi fragment või hwnd '0x...').
    Kui aknal on avatud modaalne dialoog, tuuakse see esile.
    """
    hwnd = _resolve_hwnd(title)
    if not hwnd:
        return f"VIGA: akent '{title}' ei leitud"
    popup = user32.GetWindow(hwnd, GW_ENABLEDPOPUP)
    if popup and popup != hwnd and user32.IsWindowVisible(popup) and winevents.window_text(popup):
        hwnd = popup
    ok = _force_foreground(hwnd)
    t = winevents.window_text(hwnd)
    return (f"✓ Fookuses: 0x{hwnd:x} \"{t}\"" if ok
            else f"⚠ SetForegroundWindow ei õnnestunud: 0x{hwnd:x} \"{t}\" (fookuses: \"{winevents.window_text(user32.GetForegroundWindow())}\")")


# ─── SÜNDMUSED ────────────────────────────────────────────────────────────────

@mcp.tool()
def events(since_id: int = 0, filter: Optional[str] = None, limit: int = 30) -> str:
    """
    Viimased aknasündmused (SHOW/HIDE/TITLE/FOREGROUND/DIALOG/DESTROY) taustajälgijast.
    since_id: tagasta ainult sellest uuemad (vt viimase rea #id)
    filter: pealkirja/klassi/protsessi/tüübi fragment
    """
    evs = WATCHER.since(since_id, filter, limit)
    if not evs:
        return f"Uusi sündmusi pole (viimane id={WATCHER.seq})"
    return "\n".join(winevents.format_event(e) for e in evs)


@mcp.tool()
def wait_for_window(pattern: str, timeout: float = 10.0, types: Optional[str] = None) -> str:
    """
    Oota aknasündmust, mille pealkiri/klass/protsess sisaldab pattern'it (alates praegusest hetkest).
    types: komaga, nt "SHOW,DIALOG,TITLE,FOREGROUND,HIDE"
    """
    tl = [t.strip().upper() for t in types.split(",")] if types else None
    e = WATCHER.wait_for(pattern, timeout, None, tl)
    if not e:
        return f"Ei tulnud {timeout:.1f}s jooksul: '{pattern}'"
    x, y, w, h = _window_rect(e["hwnd"])
    return winevents.format_event(e) + f" rect={x},{y},{w},{h}"


# ─── UI AUTOMATION ────────────────────────────────────────────────────────────

_UI_CACHE: dict = {}


def _uia_root(window):
    hwnd = _resolve_hwnd(window)
    if not hwnd:
        raise RuntimeError(f"akent '{window}' ei leitud")
    return UIAWrapper(UIAElementInfo(hwnd)), hwnd


@mcp.tool()
def ui_tree(window: str, depth: int = 8, filter: Optional[str] = None, max_items: int = 150,
            only_named: bool = True) -> str:
    """
    Akna UI Automation puu: id, tüüp, nimi, automation id, rect (ekraanikoordinaadid).
    Klõpsa hiljem click_ui(id). window: pealkirja fragment või hwnd.
    filter: näita ainult elemente, mille nimi/tüüp sisaldab teksti.
    """
    if not HAS_PYWINAUTO:
        return "VIGA: pywinauto pole saadaval"
    root, hwnd = _uia_root(window)
    _UI_CACHE.clear()
    lines = []
    count = [0]

    def rec(el, lvl):
        if count[0] >= max_items or lvl > depth:
            return
        try:
            info = el.element_info
            name = info.name or ""
            ctype = info.control_type or ""
            r = info.rectangle
            visible = r.width() > 0 and r.height() > 0
            show = visible and (name or not only_named)
            if show and filter and filter.lower() not in (name + " " + ctype + " " + (info.automation_id or "")).lower():
                show = False
            if show:
                count[0] += 1
                i = count[0]
                _UI_CACHE[i] = el
                aid = f" aid={info.automation_id}" if info.automation_id else ""
                lines.append(f"{'  ' * min(lvl, 6)}#{i} [{ctype}] \"{name}\"{aid} rect={r.left},{r.top},{r.width()},{r.height()}")
            for ch in el.children():
                rec(ch, lvl + 1)
        except Exception:
            pass

    rec(root, 0)
    head = f"UIA puu 0x{hwnd:x} \"{winevents.window_text(hwnd)}\": {count[0]} elementi"
    return head + "\n" + "\n".join(lines)


def _human_click(x, y, button="left", double=False, hover_ms=80, hold_ms=50):
    pyautogui.moveTo(x, y, duration=0.05)
    time.sleep(hover_ms / 1000)
    clicks = 2 if double else 1
    for i in range(clicks):
        pyautogui.mouseDown(button=button)
        time.sleep(hold_ms / 1000)
        pyautogui.mouseUp(button=button)
        if i + 1 < clicks:
            time.sleep(0.06)


@mcp.tool()
def click_ui(id: Optional[int] = None, window: Optional[str] = None, name: Optional[str] = None,
             control_type: Optional[str] = None, button: str = "left", double: bool = False,
             use_invoke: bool = True) -> str:
    """
    Klõpsa UIA elementi: kas id (viimasest ui_tree väljundist) või window+name(+control_type).
    use_invoke: proovi esmalt InvokePattern'it (ei vaja hiirt), muidu klõps rect'i keskele.
    """
    if not HAS_PYWINAUTO:
        return "VIGA: pywinauto pole saadaval"
    el = None
    if id is not None:
        el = _UI_CACHE.get(id)
        if el is None:
            return f"VIGA: id {id} puudub (käivita ui_tree uuesti)"
    else:
        if not (window and name):
            return "VIGA: anna id või window+name"
        root, _ = _uia_root(window)
        nl = name.lower()
        for d in root.descendants():
            try:
                info = d.element_info
                if nl in (info.name or "").lower() and (not control_type or control_type.lower() == (info.control_type or "").lower()):
                    r = info.rectangle
                    if r.width() > 0 and r.height() > 0:
                        el = d
                        break
            except Exception:
                continue
        if el is None:
            return f"VIGA: '{name}' ei leitud"
    info = el.element_info
    label = f"[{info.control_type}] \"{info.name}\""
    if use_invoke and button == "left" and not double:
        try:
            el.invoke()
            return f"✓ Invoke {label}"
        except Exception:
            pass
    r = info.rectangle
    cx, cy = (r.left + r.right) // 2, (r.top + r.bottom) // 2
    _human_click(cx, cy, button, double)
    return f"✓ Klõps {label} ({cx},{cy})"


# kaasühilduvus
@mcp.tool()
def list_elements(window_title: str, depth: int = 3) -> str:
    """(Vana) Sama mis ui_tree(window, depth)."""
    return ui_tree(window_title, depth)


@mcp.tool()
def find_element(window_title: str, element_name: str) -> str:
    """(Vana) Leia element nime järgi: tagastab rect'i."""
    return ui_tree(window_title, 12, element_name, 20)


@mcp.tool()
def click_element(window_title: str, element_name: str, button: str = "left") -> str:
    """(Vana) Klõpsa elementi nime järgi. button: left/right/double."""
    return click_ui(window=window_title, name=element_name,
                    button="left" if button == "double" else button, double=(button == "double"))


# ─── OCR ──────────────────────────────────────────────────────────────────────

async def _ocr_image(img: PILImage.Image, lang="en-US"):
    eng = _ocr.OcrEngine.try_create_from_language(_glob.Language(lang))
    if eng is None:
        eng = _ocr.OcrEngine.try_create_from_user_profile_languages()
    rgba = img.convert("RGBA")
    w = DataWriter()
    w.write_bytes(rgba.tobytes())
    bmp = SoftwareBitmap.create_copy_from_buffer(w.detach_buffer(), BitmapPixelFormat.RGBA8, rgba.width, rgba.height)
    return await eng.recognize_async(bmp)


async def _ocr_words(region=None, upscale=None, monitor="active"):
    reg = _parse_region(region) or _monitor_rect(monitor)
    img = _grab(reg)
    ox, oy = (reg[0], reg[1]) if reg else (0, 0)
    f = upscale or (2.0 if img.width * img.height < 600_000 else 1.0)
    if f != 1.0:
        img = img.resize((int(img.width * f), int(img.height * f)), PILImage.LANCZOS)
    res = await _ocr_image(img)
    lines = []
    for ln in res.lines:
        words = []
        for wd in ln.words:
            r = wd.bounding_rect
            words.append((wd.text, ox + r.x / f, oy + r.y / f, r.width / f, r.height / f))
        lines.append((ln.text, words))
    return lines


def _norm(s):
    return "".join(ch for ch in s.lower() if ch.isalnum())


def _match(lines, query):
    q = _norm(query)
    hits = []
    for text, words in lines:
        if q not in _norm(text):
            continue
        for i in range(len(words)):
            acc = ""
            for j in range(i, len(words)):
                acc += _norm(words[j][0])
                if q in acc:
                    xs = [words[k][1] for k in range(i, j + 1)]
                    ys = [words[k][2] for k in range(i, j + 1)]
                    x2 = max(words[k][1] + words[k][3] for k in range(i, j + 1))
                    y2 = max(words[k][2] + words[k][4] for k in range(i, j + 1))
                    hits.append((text, int(min(xs)), int(min(ys)), int(x2 - min(xs)), int(y2 - min(ys))))
                    break
                if len(acc) > len(q) + 40:
                    break
            if hits and hits[-1][0] == text:
                break
    return hits


@mcp.tool()
async def ocr(region: Optional[str] = None, max_lines: int = 80, monitor: str = "active") -> str:
    """Loe ekraanilt tekst (Windows OCR) koos asukohtadega. region: "x,y,w,h"; monitor: active/primary/left/right/all."""
    if not HAS_OCR:
        return "VIGA: OCR pole saadaval (winrt-Windows.Media.Ocr)"
    lines = await _ocr_words(region, monitor=monitor)
    out = []
    for text, words in lines[:max_lines]:
        if not words:
            continue
        x = int(min(w[1] for w in words)); y = int(min(w[2] for w in words))
        x2 = int(max(w[1] + w[3] for w in words)); y2 = int(max(w[2] + w[4] for w in words))
        out.append(f"({x},{y},{x2 - x},{y2 - y}) {text}")
    return "\n".join(out) if out else "Teksti ei leitud."


@mcp.tool()
async def find_text(text: str, region: Optional[str] = None, monitor: str = "all") -> str:
    """Leia tekst ekraanilt (OCR), vaikimisi kõigilt monitoridelt. Tagastab vasted: rect, keskpunkt, monitor."""
    if not HAS_OCR:
        return "VIGA: OCR pole saadaval"
    hits = _match(await _ocr_words(region, monitor=monitor), text)
    if not hits:
        return f"'{text}' ei leitud"
    return "\n".join(f"[{i}] keskpunkt=({x + w // 2},{y + h // 2}) monitor={_monitor_of_point(x, y)} rect={x},{y},{w},{h} rida=\"{t}\""
                     for i, (t, x, y, w, h) in enumerate(hits))


@mcp.tool()
async def click_text(text: str, region: Optional[str] = None, index: int = 0, button: str = "left",
                     double: bool = False, offset_x: int = 0, offset_y: int = 0, monitor: str = "all") -> str:
    """
    Klõpsa ekraanil nähtavale tekstile (OCR) — nt click_text("Slice plate").
    index: mitmes vaste (0 = esimene); offset_x/y: nihe keskpunktist.
    """
    if not HAS_OCR:
        return "VIGA: OCR pole saadaval"
    hits = _match(await _ocr_words(region, monitor=monitor), text)
    if len(hits) <= index:
        return f"VIGA: '{text}' ei leitud (vasteid {len(hits)})"
    t, x, y, w, h = hits[index]
    cx, cy = x + w // 2 + offset_x, y + h // 2 + offset_y
    _human_click(cx, cy, button, double)
    return f"✓ Klõpsasin tekstile '{text}' ({cx},{cy}) monitor={_monitor_of_point(cx, cy)} rida=\"{t}\" (vasteid {len(hits)})"


# ─── HIIR ─────────────────────────────────────────────────────────────────────

async def _check_expect(sx, sy, expect_text) -> Optional[str]:
    """Tagastab None kui OK, muidu veateate."""
    found = []
    if HAS_PYWINAUTO:
        try:
            el = Desktop(backend="uia").from_point(sx, sy)
            nm = el.element_info.name or ""
            found.append(f"UIA=\"{nm}\"")
            if _norm(expect_text) and _norm(expect_text) in _norm(nm):
                return None
        except Exception:
            pass
    if HAS_OCR:
        lines = await _ocr_words((sx - 160, sy - 30, 320, 60), upscale=2.0)
        txt = " | ".join(t for t, _ in lines)
        found.append(f"OCR=\"{txt}\"")
        if _norm(expect_text) in _norm(txt):
            return None
    return f"⛔ Klõpsu EI tehtud: ootasin '{expect_text}', punktis ({sx},{sy}) leidsin {', '.join(found) or 'mitte midagi'}"


@mcp.tool()
async def click_coords(x: int, y: int, button: str = "left", space: str = "screen",
                       expect_text: Optional[str] = None, hover_ms: int = 80, hold_ms: int = 50) -> str:
    """
    Klõpsa koordinaatidel ("inimlik": liigu kohale, oota hover_ms, vajuta hold_ms).
    space: 'screen' (vaikimisi) või 'shot' (viimase screenshot/zoom pildi pikslid)
    expect_text: klõpsukaitse — klõpsa ainult kui punktis on see tekst (UIA nimi või OCR)
    """
    sx, sy = _to_screen(x, y, space)
    if expect_text:
        err = await _check_expect(sx, sy, expect_text)
        if err:
            return err
    _human_click(sx, sy, button, False, hover_ms, hold_ms)
    return f"✓ Klõpsasin ({sx}, {sy}) {button}"


@mcp.tool()
async def double_click_coords(x: int, y: int, space: str = "screen", expect_text: Optional[str] = None) -> str:
    """Topeltklõps koordinaatidel (space/expect_text nagu click_coords)."""
    sx, sy = _to_screen(x, y, space)
    if expect_text:
        err = await _check_expect(sx, sy, expect_text)
        if err:
            return err
    _human_click(sx, sy, "left", True)
    return f"✓ Topeltklõps ({sx}, {sy})"


@mcp.tool()
def mouse_move(x: int, y: int, duration: float = 0.2, space: str = "screen") -> str:
    """Liiguta hiirt (ilma klõpsamata)."""
    sx, sy = _to_screen(x, y, space)
    pyautogui.moveTo(sx, sy, duration=duration)
    return f"✓ Hiir ({sx}, {sy})"


@mcp.tool()
def scroll(x: int, y: int, clicks: int = 3, direction: str = "up", space: str = "screen") -> str:
    """Keri hiirerattaga. direction: 'up'/'down'."""
    sx, sy = _to_screen(x, y, space)
    pyautogui.scroll(clicks if direction == "up" else -clicks, x=sx, y=sy)
    return f"✓ Kerisin {direction} {clicks} ({sx}, {sy})"


# ─── KLAVIATUUR ───────────────────────────────────────────────────────────────

def _type(text, interval=0.02):
    """Alati Unicode SendInput: ei sõltu klaviatuuripaigutusest (EE paigutusel pyautogui '+' -> '?')."""
    for ch in text:
        if ch == "\n":
            pyautogui.press("enter")
        elif ch == "\t":
            pyautogui.press("tab")
        else:
            _send_unicode(ch)
        time.sleep(interval)


class _KI(ctypes.Structure):
    _fields_ = [("wVk", wt.WORD), ("wScan", wt.WORD), ("dwFlags", wt.DWORD), ("time", wt.DWORD),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]


class _INPUT(ctypes.Structure):
    class _U(ctypes.Union):
        _fields_ = [("ki", _KI), ("pad", ctypes.c_byte * 32)]
    _anonymous_ = ("u",)
    _fields_ = [("type", wt.DWORD), ("u", _U)]


def _send_unicode(ch):
    for flags in (0x0004, 0x0004 | 0x0002):  # KEYEVENTF_UNICODE, +KEYUP
        inp = _INPUT(type=1)
        inp.ki = _KI(0, ord(ch), flags, 0, None)
        user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(_INPUT))


@mcp.tool()
def type_text(text: str, interval: float = 0.02) -> str:
    """Trüki tekst aktiivsesse aknasse (toetab ka täpitähti)."""
    _type(text, interval)
    return f"✓ Trükitud: '{text}'"


@mcp.tool()
def hotkey(keys: str) -> str:
    """Kiirklahvid: 'ctrl+c', 'alt+tab', 'ctrl+shift+g'."""
    pyautogui.hotkey(*[k.strip() for k in keys.split("+")])
    return f"✓ Klahvikombinatsioon: {keys}"


@mcp.tool()
def key_press(key: str, presses: int = 1) -> str:
    """Üksik klahv: enter, escape, tab, delete, up, down, f1..f12, 1..9 jne."""
    pyautogui.press(key, presses=presses)
    return f"✓ Klahv: {key}" + (f" x{presses}" if presses > 1 else "")


@mcp.tool()
def key_down(key: str) -> str:
    """Hoia klahvi all."""
    pyautogui.keyDown(key)
    return f"✓ Klahv all: {key}"


@mcp.tool()
def key_up(key: str) -> str:
    """Vabasta klahv."""
    pyautogui.keyUp(key)
    return f"✓ Klahv vabastatud: {key}"


# ─── ACT: mitu tegevust + ootamine + pilt ühes kutses ─────────────────────────

@mcp.tool()
async def act(actions: list[dict[str, Any]], wait: str = "stable", timeout: float = 4.0,
              wait_window: Optional[str] = None, screenshot: bool = True,
              region: Optional[str] = None, window: Optional[str] = None, max_width: int = 1280,
              monitor: str = "active") -> list:
    """
    Tee järjest mitu tegevust, siis oota ja tee pilt — kõik ühes kutses.
    actions: list, iga element üks järgmistest:
      {"focus": "Bambu"}                       too aken esile
      {"click": [x, y], "button": "left", "double": false, "space": "screen"|"shot", "expect": "tekst"}
      {"click_text": "Slice plate", "index": 0}
      {"click_ui": 12}                         id viimasest ui_tree'st
      {"move": [x, y]}
      {"type": "tekst"}
      {"key": "enter", "presses": 1}
      {"hotkey": "ctrl+i"}
      {"scroll": [x, y, clicks, "down"]}
      {"sleep": 0.5}
      {"wait_window": "Choose one", "timeout": 8}   oota aknasündmust
    wait: "stable" (oota kuni ekraan rahuneb), "none", või sekundid nt "1.5"
    wait_window: pärast tegevusi oota aknasündmust (pealkirja fragment)
    screenshot: lisa lõpus pilt (region/window/max_width nagu screenshot()); monitor vaikimisi 'active'
    Peatub esimese vea juures.
    """
    log = []
    t0 = time.time()
    for i, a in enumerate(actions):
        try:
            if "focus" in a:
                log.append(focus_window(str(a["focus"])))
            elif "click" in a:
                x, y = a["click"]
                sx, sy = _to_screen(x, y, a.get("space", "screen"))
                if a.get("expect"):
                    err = await _check_expect(sx, sy, a["expect"])
                    if err:
                        log.append(err)
                        break
                _human_click(sx, sy, a.get("button", "left"), a.get("double", False),
                             a.get("hover_ms", 80), a.get("hold_ms", 50))
                log.append(f"klõps ({sx},{sy})")
            elif "click_text" in a:
                r = await click_text(a["click_text"], a.get("region"), a.get("index", 0),
                                     a.get("button", "left"), a.get("double", False),
                                     monitor=a.get("monitor", "all"))
                log.append(r)
                if r.startswith("VIGA"):
                    break
            elif "click_ui" in a:
                r = click_ui(id=int(a["click_ui"]))
                log.append(r)
                if r.startswith("VIGA"):
                    break
            elif "move" in a:
                sx, sy = _to_screen(*a["move"], a.get("space", "screen"))
                pyautogui.moveTo(sx, sy, duration=0.05)
                log.append(f"hiir ({sx},{sy})")
            elif "type" in a:
                _type(str(a["type"]), a.get("interval", 0.02))
                log.append(f"trükk '{a['type']}'")
            elif "key" in a:
                pyautogui.press(a["key"], presses=int(a.get("presses", 1)))
                log.append(f"klahv {a['key']}")
            elif "hotkey" in a:
                pyautogui.hotkey(*[k.strip() for k in str(a["hotkey"]).split("+")])
                log.append(f"hotkey {a['hotkey']}")
            elif "scroll" in a:
                x, y, n, d = (list(a["scroll"]) + [3, "down"])[:4]
                pyautogui.scroll(n if d == "up" else -n, x=x, y=y)
                log.append(f"kerimine {d} {n}")
            elif "sleep" in a:
                time.sleep(float(a["sleep"]))
                log.append(f"paus {a['sleep']}s")
            elif "wait_window" in a:
                log.append(wait_for_window(a["wait_window"], float(a.get("timeout", 8))))
            else:
                log.append(f"? tundmatu tegevus {a}")
        except Exception as e:
            log.append(f"VIGA tegevusel {i}: {e}")
            break
    if wait_window:
        log.append(wait_for_window(wait_window, timeout))
    if wait == "stable":
        log.append(_wait_stable(_parse_region(region), timeout))
    elif wait and wait != "none":
        time.sleep(float(wait))
    fg = user32.GetForegroundWindow()
    log.append(f"fookuses: \"{winevents.window_text(fg)}\" | {time.time() - t0:.2f}s")
    out = ["\n".join(log)]
    if screenshot:
        out += list(_shot(region, window, max_width, monitor=monitor))
    return out


# ─── KÄIVITAMINE ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Computer Control MCP Server v2.0 käivitub...", file=sys.stderr)
    mcp.run()
