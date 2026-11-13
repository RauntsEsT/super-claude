"""
Windowsi aknasündmuste jälgija (SetWinEventHook).

Kasutus:
  1) Moodulina serveris: start_watcher() käivitab taustalõime, sündmused ringpuhvrisse.
  2) Eraldi skriptina (Monitor-tööriista jaoks):
       python winevents.py [protsessi_filter ...]
     Prindib iga sündmuse ühe reana stdout-i (flush), nt:
       10:58:03 SHOW  hwnd=0x1234 [#32770] "Choose one or more files" (bambu-studio.exe)
"""

import ctypes
import ctypes.wintypes as wt
import os
import sys
import threading
import time
from collections import deque

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

EVENT_SYSTEM_FOREGROUND = 0x0003
EVENT_SYSTEM_DIALOGSTART = 0x0010
EVENT_SYSTEM_DIALOGEND = 0x0011
EVENT_OBJECT_CREATE = 0x8000
EVENT_OBJECT_DESTROY = 0x8001
EVENT_OBJECT_SHOW = 0x8002
EVENT_OBJECT_HIDE = 0x8003
EVENT_OBJECT_NAMECHANGE = 0x800C
WINEVENT_OUTOFCONTEXT = 0x0000
WINEVENT_SKIPOWNPROCESS = 0x0002
OBJID_WINDOW = 0
CHILDID_SELF = 0
GA_ROOT = 2

WinEventProcType = ctypes.WINFUNCTYPE(
    None, wt.HANDLE, wt.DWORD, wt.HWND, wt.LONG, wt.LONG, wt.DWORD, wt.DWORD
)

user32.SetWinEventHook.restype = wt.HANDLE
user32.SetWinEventHook.argtypes = [wt.DWORD, wt.DWORD, wt.HMODULE, WinEventProcType,
                                   wt.DWORD, wt.DWORD, wt.DWORD]
user32.GetAncestor.restype = wt.HWND
user32.GetAncestor.argtypes = [wt.HWND, wt.UINT]
user32.GetWindowThreadProcessId.argtypes = [wt.HWND, ctypes.POINTER(wt.DWORD)]

NAMES = {
    EVENT_SYSTEM_FOREGROUND: "FOREGROUND",
    EVENT_SYSTEM_DIALOGSTART: "DIALOG",
    EVENT_SYSTEM_DIALOGEND: "DIALOG_END",
    EVENT_OBJECT_SHOW: "SHOW",
    EVENT_OBJECT_HIDE: "HIDE",
    EVENT_OBJECT_DESTROY: "DESTROY",
    EVENT_OBJECT_NAMECHANGE: "TITLE",
}

_exe_cache = {}


def window_text(hwnd) -> str:
    n = user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(n + 1)
    user32.GetWindowTextW(hwnd, buf, n + 1)
    return buf.value


def class_name(hwnd) -> str:
    buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buf, 256)
    return buf.value


def process_name(hwnd) -> str:
    pid = wt.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    p = pid.value
    if p in _exe_cache:
        return _exe_cache[p]
    name = "?"
    h = kernel32.OpenProcess(0x1000, False, p)  # PROCESS_QUERY_LIMITED_INFORMATION
    if h:
        buf = ctypes.create_unicode_buffer(520)
        size = wt.DWORD(520)
        if kernel32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(size)):
            name = os.path.basename(buf.value)
        kernel32.CloseHandle(h)
    _exe_cache[p] = name
    return name


class Watcher:
    def __init__(self, maxlen=500, proc_filter=None, printer=None):
        self.events = deque(maxlen=maxlen)
        self.seq = 0
        self.lock = threading.Lock()
        self.cond = threading.Condition(self.lock)
        self.proc_filter = [p.lower() for p in (proc_filter or [])]
        self.printer = printer
        self._proc = WinEventProcType(self._callback)
        self.thread = None
        self._last_title = {}

    def _callback(self, hHook, event, hwnd, idObject, idChild, thread, ms):
        try:
            if idObject != OBJID_WINDOW or idChild != CHILDID_SELF or not hwnd:
                return
            # ainult tipptaseme aknad (ka owned dialoogid on root)
            if user32.GetAncestor(hwnd, GA_ROOT) != hwnd:
                return
            if event in (EVENT_OBJECT_SHOW, EVENT_OBJECT_HIDE, EVENT_OBJECT_NAMECHANGE):
                if not user32.IsWindowVisible(hwnd) and event != EVENT_OBJECT_HIDE:
                    return
            title = window_text(hwnd)
            cls = class_name(hwnd)
            if event in (EVENT_OBJECT_SHOW, EVENT_OBJECT_HIDE, EVENT_OBJECT_NAMECHANGE) and not title:
                return
            if event == EVENT_OBJECT_NAMECHANGE:
                if self._last_title.get(hwnd) == title:
                    return
            self._last_title[hwnd] = title
            if cls in ("tooltips_class32", "Xaml_WindowedPopupClass", "ForegroundStaging"):
                return
            exe = process_name(hwnd)
            if self.proc_filter and not any(f in exe.lower() for f in self.proc_filter):
                return
            ev = {
                "t": time.strftime("%H:%M:%S"),
                "type": NAMES.get(event, hex(event)),
                "hwnd": int(hwnd),
                "cls": cls,
                "title": title,
                "exe": exe,
            }
            with self.cond:
                self.seq += 1
                ev["id"] = self.seq
                self.events.append(ev)
                self.cond.notify_all()
            if self.printer:
                self.printer(format_event(ev))
        except Exception:
            pass

    def _loop(self):
        hooks = []
        for lo, hi in ((EVENT_SYSTEM_FOREGROUND, EVENT_SYSTEM_FOREGROUND),
                       (EVENT_SYSTEM_DIALOGSTART, EVENT_SYSTEM_DIALOGEND),
                       (EVENT_OBJECT_SHOW, EVENT_OBJECT_HIDE),
                       (EVENT_OBJECT_NAMECHANGE, EVENT_OBJECT_NAMECHANGE)):
            h = user32.SetWinEventHook(lo, hi, None, self._proc, 0, 0,
                                       WINEVENT_OUTOFCONTEXT | WINEVENT_SKIPOWNPROCESS)
            hooks.append(h)
        msg = wt.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.thread = threading.Thread(target=self._loop, daemon=True, name="winevents")
        self.thread.start()

    def since(self, last_id=0, pattern=None, limit=50):
        with self.lock:
            out = [e for e in self.events if e["id"] > last_id]
        if pattern:
            p = pattern.lower()
            out = [e for e in out if p in (e["title"] + " " + e["cls"] + " " + e["exe"] + " " + e["type"]).lower()]
        return out[-limit:]

    def wait_for(self, pattern, timeout=10.0, after_id=None, types=None):
        p = (pattern or "").lower()
        start_id = self.seq if after_id is None else after_id
        deadline = time.time() + timeout
        with self.cond:
            while True:
                for e in self.events:
                    if e["id"] <= start_id:
                        continue
                    if types and e["type"] not in types:
                        continue
                    hay = (e["title"] + " " + e["cls"] + " " + e["exe"] + " " + e["type"]).lower()
                    if p in hay:
                        return e
                left = deadline - time.time()
                if left <= 0:
                    return None
                self.cond.wait(left)


def format_event(e) -> str:
    return f'{e["t"]} #{e["id"]} {e["type"]:<10} hwnd=0x{e["hwnd"]:x} [{e["cls"]}] "{e["title"]}" ({e["exe"]})'


_watcher = None


def start_watcher():
    global _watcher
    if _watcher is None:
        _watcher = Watcher()
        _watcher.start()
    return _watcher


if __name__ == "__main__":
    filt = sys.argv[1:]

    def pr(line):
        print(line, flush=True)

    w = Watcher(proc_filter=filt, printer=pr)
    print(f"winevents jälgija käivitus (filter: {filt or 'kõik'})", flush=True)
    w._loop()
