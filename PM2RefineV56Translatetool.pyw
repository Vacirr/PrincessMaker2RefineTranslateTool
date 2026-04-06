#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PM2 Çeviri Aracı  v22  —  Princess Maker 2  Pointer Relocation + TR/EN
v22 Değişiklikler:
  • HEX BYTE EDİTÖRÜ — büyük hex görünümünde bayta tıkla → değerini değiştir → Uygula
  • _manual_patches sistemi — ham hex yamaları EXE kayıtta korunur
  • BUG FIX: _relocate_from_hex f-string crash (va None)
  • BUG FIX: _hv_send_selection pe.data yerine _hv_display kullanıyor
  • BUG FIX: _hex_click kolon hesabı (v20 mantığı restore)
  • BUG FIX: _hv_update_rows satır tag yenileme
  • BUG FIX: show_history open_dir None crash
  • BUG FIX: Ctrl+Z / Ctrl+Y (undo=True) korundu
  • BUG FIX: Enter → sadece satır sonu; Ctrl+Enter → kaydet
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re, os, json, struct, datetime, traceback, shutil

# ═══════════════════════════════════════════════════════════════════════════
#  TEMA
# ═══════════════════════════════════════════════════════════════════════════
BG      = "#0d0f14"
BG2     = "#141720"
BG3     = "#1c2030"
ACCENT  = "#e8a045"
ACCENT2 = "#5b8dd9"
GREEN   = "#4ecb71"
RED     = "#e05555"
YELLOW  = "#e8d045"
FG      = "#dde3f0"
FG2     = "#7a8499"
BORDER  = "#2a3045"

# ═══════════════════════════════════════════════════════════════════════════
#  DİL
# ═══════════════════════════════════════════════════════════════════════════
LANG = {
    "TR": {
        "title":          "⚔  PM2 ÇEVİRİ ARACI  v22",
        "subtitle":       "Pointer Relocation · Sınırsız Uzunluk · Hex Editör · Otomatik Yedek",
        "status_default": "EXE dosyası yükleyin",
        "btn_load":       "📂 EXE Yükle",
        "btn_save":       "💾 EXE Kaydet",
        "btn_export":     "📤 JSON Dışa",
        "btn_import":     "📥 JSON İçe",
        "btn_lang":       "🌐 English",
        "btn_history":    "🕓 Geçmiş",
        "lbl_search":     "Ara:",
        "filter_all":     "Tümü",
        "filter_pending": "Bekleyen",
        "filter_done":    "Çevrildi",
        "filter_native":  "Zaten TR",
        "col_status":     "✓",
        "col_offset":     "Adres",
        "col_orig":       "Orijinal",
        "col_tr":         "Çeviri",
        "lbl_list":       "METİN LİSTESİ",
        "lbl_editor":     "EDİTÖR",
        "lbl_orig":       "ORİJİNAL:",
        "lbl_tr":         "ÇEVİRİ:",
        "lbl_hex":        "HEX:",
        "lbl_ptrs":       "POINTER'LAR:",
        "lbl_addr":       "Adres: —",
        "btn_save_tr":    "✔  Kaydet  (Ctrl+Enter)",
        "btn_prev":       "◀ Önceki",
        "btn_next":       "Sonraki ▶",
        "chk_reloc":      "⚡ Pointer Relocation — çeviri sığmazsa yeni alana taşı",
        "warn_ok":        "✔  {used}/{max} byte — sığıyor",
        "warn_reloc":     "⚡  {used}/{max} byte — taşınacak",
        "warn_over":      "✘  {used}/{max} byte — {over} fazla! Relocation aç ↑",
        "max_lbl":        "Maks {n} byte",
        "relocated_lbl":  "⚡ Taşındı → {addr}",
        "stat":           "Toplam:{t}  Çevrildi:{d}  Taşındı:{r}  ZatenTR:{n}  Bekliyor:{p}",
        "err_load":       "Önce EXE yükleyin!",
        "err_enc_title":  "Encoding Hatası",
        "err_enc_msg":    "Bu karakterler kodlanamıyor:\n{e}",
        "err_long_title": "Çok Uzun",
        "err_long_msg":   "{used}b > {max}b  (+{over}b fazla)\nRelocation'ı aç veya metni kısalt!",
        "save_title":     "Yamlanmış EXE Kaydet",
        "save_suffix":    "_TR.exe",
        "save_ok_title":  "Başarılı",
        "save_ok_msg":    "✔ Kaydedildi!\nNormal:{a}  Reloc:{r}  HexYama:{h}  Hata:{e}\n\n{path}\n\n{detail}",
        "saved_status":   "✔ Kaydedildi: {f}",
        "json_saved":     "{n} string kaydedildi.",
        "json_loaded":    "{n} çeviri yüklendi.",
        "warn_lbl":       "Uyarı",
        "exe_running":    "EXE Çalışıyor",
        "exe_run_msg":    "'{name}' çalışıyor!\nÖnce oyunu kapatın.",
    },
    "EN": {
        "title":          "⚔  PM2 TRANSLATION TOOL  v22",
        "subtitle":       "Pointer Relocation · Unlimited Length · Hex Editor · Auto Backup",
        "status_default": "Load an EXE file to begin",
        "btn_load":       "📂 Load EXE",
        "btn_save":       "💾 Save EXE",
        "btn_export":     "📤 Export JSON",
        "btn_import":     "📥 Import JSON",
        "btn_lang":       "🌐 Türkçe",
        "btn_history":    "🕓 History",
        "lbl_search":     "Search:",
        "filter_all":     "All",
        "filter_pending": "Pending",
        "filter_done":    "Translated",
        "filter_native":  "Already TR",
        "col_status":     "✓",
        "col_offset":     "Offset",
        "col_orig":       "Original",
        "col_tr":         "Translation",
        "lbl_list":       "STRING LIST",
        "lbl_editor":     "EDITOR",
        "lbl_orig":       "ORIGINAL:",
        "lbl_tr":         "TRANSLATION:",
        "lbl_hex":        "HEX:",
        "lbl_ptrs":       "POINTERS:",
        "lbl_addr":       "Offset: —",
        "btn_save_tr":    "✔  Save  (Ctrl+Enter)",
        "btn_prev":       "◀ Previous",
        "btn_next":       "Next ▶",
        "chk_reloc":      "⚡ Pointer Relocation — relocate if translation is too long",
        "warn_ok":        "✔  {used}/{max} bytes — fits",
        "warn_reloc":     "⚡  {used}/{max} bytes — will relocate",
        "warn_over":      "✘  {used}/{max} bytes — {over} over! Enable Relocation ↑",
        "max_lbl":        "Max {n} bytes",
        "relocated_lbl":  "⚡ Relocated → {addr}",
        "stat":           "Total:{t}  Done:{d}  Relocated:{r}  NativeTR:{n}  Pending:{p}",
        "err_load":       "Load an EXE file first!",
        "err_enc_title":  "Encoding Error",
        "err_enc_msg":    "Cannot encode:\n{e}",
        "err_long_title": "Too Long",
        "err_long_msg":   "{used}b > {max}b  (+{over}b over)\nEnable Relocation or shorten!",
        "save_title":     "Save Patched EXE",
        "save_suffix":    "_EN.exe",
        "save_ok_title":  "Success",
        "save_ok_msg":    "✔ Saved!\nNormal:{a}  Reloc:{r}  HexPatch:{h}  Errors:{e}\n\n{path}\n\n{detail}",
        "saved_status":   "✔ Saved: {f}",
        "json_saved":     "{n} strings exported.",
        "json_loaded":    "{n} translations imported.",
        "warn_lbl":       "Warning",
        "exe_running":    "EXE Running",
        "exe_run_msg":    "'{name}' is running!\nClose the game first.",
    },
}

# ═══════════════════════════════════════════════════════════════════════════
#  PE YARDIMCILARI
# ═══════════════════════════════════════════════════════════════════════════
def align_up(val, align):
    return (val + align - 1) & ~(align - 1)


class PEInfo:
    def __init__(self, data):
        self.data         = bytearray(data)
        self.pe_off       = struct.unpack_from('<I', data, 0x3c)[0]
        self.num_sections = struct.unpack_from('<H', data, self.pe_off + 6)[0]
        self.opt_size     = struct.unpack_from('<H', data, self.pe_off + 20)[0]
        self.image_base   = struct.unpack_from('<I', data, self.pe_off + 52)[0]
        self.sec_align    = struct.unpack_from('<I', data, self.pe_off + 56)[0]
        self.file_align   = struct.unpack_from('<I', data, self.pe_off + 60)[0]
        self.sec_table    = self.pe_off + 24 + self.opt_size
        self._load_sections()

    def _load_sections(self):
        self.sections = []
        for i in range(self.num_sections):
            o = self.sec_table + i * 40
            d = self.data
            self.sections.append({
                'name':    d[o:o+8].rstrip(b'\x00').decode('ascii', 'replace'),
                'vsize':   struct.unpack_from('<I', d, o+8)[0],
                'vaddr':   struct.unpack_from('<I', d, o+12)[0],
                'rawsize': struct.unpack_from('<I', d, o+16)[0],
                'rawoff':  struct.unpack_from('<I', d, o+20)[0],
                'hdr_off': o,
            })

    def file_to_va(self, foff):
        for s in self.sections:
            if s['rawoff'] <= foff < s['rawoff'] + s['rawsize']:
                return foff - s['rawoff'] + s['vaddr'] + self.image_base
        return None

    def find_pointers(self, file_off):
        va = self.file_to_va(file_off)
        if va is None:
            return []
        target = struct.pack('<I', va)
        result, idx = [], 0
        while True:
            pos = self.data.find(target, idx)
            if pos == -1:
                break
            result.append(pos)
            idx = pos + 1
        return result

    def add_section(self, name=b'.xtra\x00\x00\x00', size=0x10000):
        first_raw  = min(s['rawoff'] for s in self.sections if s['rawoff'] > 0)
        header_end = self.sec_table + self.num_sections * 40
        free_bytes = first_raw - header_end
        if free_bytes < 40:
            raise RuntimeError(
                f"PE header'da yeni section için yer yok! "
                f"({free_bytes}b boş, 40b lazım)")
        last        = self.sections[-1]
        new_vaddr   = align_up(last['vaddr'] + max(last['vsize'], last['rawsize']), self.sec_align)
        new_rawoff  = align_up(last['rawoff'] + last['rawsize'], self.file_align)
        new_rawsize = align_up(size, self.file_align)
        new_hdr_off = self.sec_table + self.num_sections * 40
        hdr = bytearray(40)
        hdr[0:8] = name[:8]
        struct.pack_into('<I', hdr,  8, size)
        struct.pack_into('<I', hdr, 12, new_vaddr)
        struct.pack_into('<I', hdr, 16, new_rawsize)
        struct.pack_into('<I', hdr, 20, new_rawoff)
        struct.pack_into('<I', hdr, 36, 0xC0000040)
        self.data[new_hdr_off:new_hdr_off + 40] = hdr
        struct.pack_into('<H', self.data, self.pe_off + 6,  self.num_sections + 1)
        struct.pack_into('<I', self.data, self.pe_off + 80,
                         align_up(new_vaddr + size, self.sec_align))
        padding = new_rawoff - len(self.data)
        if padding > 0:
            self.data += b'\x00' * padding
        self.data += b'\x00' * new_rawsize
        self.num_sections += 1
        self._load_sections()
        return new_rawoff, new_vaddr + self.image_base

    def find_code_cave(self, needed, exclude_ranges=None):
        data           = bytes(self.data)
        exclude_ranges = exclude_ranges or []
        best_off  = None
        best_va   = None
        best_size = 0

        def in_exclude(off, sz):
            for (a, b) in exclude_ranges:
                if off < b and off + sz > a:
                    return True
            return False

        for sec in self.sections:
            ro  = sec['rawoff']
            rsz = sec['rawsize']
            if ro == 0 or rsz == 0:
                continue
            region = data[ro:ro + rsz]
            i = 0
            while i < len(region):
                if region[i] != 0:
                    i += 1
                    continue
                j = i
                while j < len(region) and region[j] == 0:
                    j += 1
                cave_size = j - i
                cave_abs  = ro + i
                if cave_size >= needed and cave_size > best_size:
                    if not in_exclude(cave_abs, cave_size):
                        best_size = cave_size
                        best_off  = cave_abs
                        best_va   = cave_abs - sec['rawoff'] + sec['vaddr'] + self.image_base
                i = j

        if best_off is None:
            raise RuntimeError(
                f"Code cave bulunamadı!\nGereken: {needed} byte — EXE içinde yeterli boş alan yok.")
        return best_off, best_va


# ═══════════════════════════════════════════════════════════════════════════
#  STRING EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════
def is_game_text(s):
    if re.match(r'^PM2RF_', s):               return False
    if re.match(r'^[A-Z0-9_.\\/:]+$', s):     return False
    if len(s) < 4:                             return False
    vis = sum(1 for c in s if c.isprintable() and ord(c) > 31)
    return vis / max(len(s), 1) > 0.65


def extract_strings(data, start=0x100000, end=0x165000):
    region = data[start:end]
    result, current, start_i = [], b'', 0
    for i, b in enumerate(region):
        if b == 0:
            if len(current) >= 4:
                try:
                    s = current.decode('windows-1254')
                    if is_game_text(s):
                        result.append({
                            'offset':      start + start_i,
                            'length':      len(current),
                            'text':        s,
                            'translation': '',
                            'relocated':   False,
                        })
                except Exception:
                    pass
            current, start_i = b'', i + 1
        else:
            current += bytes([b])
    return result


def is_turkish(s):
    return bool(re.search(r'[ğüşıöçĞÜŞİÖÇ]', s))


# ═══════════════════════════════════════════════════════════════════════════
#  HEX VIEWER SABİTLERİ
#  Format:  " {fo:08X}  {hex_str}  │ {asc} │\n"
#  hex_str = '   '.join(4 × "XX XX XX XX").ljust(57)
#
#  Kolon haritası (0-indexed):
#   0       : boşluk
#   1-8     : adres
#   9-10    : "  "
#   11-21   : grup0  "XX XX XX XX"
#   22-24   : "   "  separator
#   25-35   : grup1
#   36-38   : "   "  separator
#   39-49   : grup2
#   50-52   : "   "  separator
#   53-63   : grup3
#   64-67   : ljust padding (4 boşluk)
#   68-69   : "  "
#   70      : "│"
#   71      : " "
#   72-87   : ASCII (16 karakter)
#   88      : " "
#   89      : "│"
# ═══════════════════════════════════════════════════════════════════════════
HV_HEX_START   = 11
HV_ASCII_START = 72
HV_BPR         = 16


def hv_col_to_byte(col):
    """Büyük hex viewer'da kolon → byte indisi (0-15)."""
    if col >= HV_ASCII_START:
        return min(col - HV_ASCII_START, HV_BPR - 1)
    if col < HV_HEX_START:
        return 0
    rel    = col - HV_HEX_START          # grup bloğuna göre offset
    g      = min(rel // 14, 3)           # hangi 4'lü grup (0-3)
    within = rel - g * 14                # grup içi offset (0-13)
    return min(g * 4 + min(within // 3, 3), HV_BPR - 1)


def hv_byte_to_col(byte_idx):
    """Byte indisi (0-15) → hex viewer sütun başlangıcı."""
    g   = byte_idx // 4
    b   = byte_idx % 4
    return HV_HEX_START + g * 14 + b * 3


def hv_format_row(fo, row_bytes):
    """16 byte için hex viewer satırı üretir (\\n olmadan)."""
    parts = []
    for g in range(4):
        grp = row_bytes[g*4:(g+1)*4]
        parts.append(' '.join(f'{x:02X}' for x in grp))
    hex_str = '   '.join(parts).ljust(4*3*4 + 3*3)
    asc     = ''.join(chr(b) if 0x20 <= b < 0x7F else '·' for b in row_bytes)
    return f" {fo:08X}  {hex_str}  │ {asc} │"


# ═══════════════════════════════════════════════════════════════════════════
#  ANA UYGULAMA
# ═══════════════════════════════════════════════════════════════════════════
class PM2Translator(tk.Tk):

    # ── Init ──────────────────────────────────────────────────────────────
    def __init__(self):
        super().__init__()
        self.geometry("1360x860")
        self.configure(bg=BG)
        self.minsize(980, 620)

        self.lang          = "TR"
        self.exe_path      = None
        self.pe            = None
        self._orig_raw     = None
        self.strings       = []
        self.filtered      = []
        self.selected      = None
        self.unsaved       = False
        self._hv_display   = bytearray()
        self._hv_loaded    = False
        self._hv_str_map   = {}
        self._hv_matches   = []
        self._hv_match_idx = -1
        self._hv_last_q    = ''
        self._log_entries  = []
        self._log_path     = None
        self.hex_sel_off   = None

        # v21: yedek sistemi
        self._backup_dir   = None
        self._history      = []
        self._backup_count = 0

        # v22: ham hex yamaları  {file_offset: new_byte_value}
        self._manual_patches = {}
        self._hv_edit_off    = None   # büyük hex'te seçili byte ofseti

        # v22b: küçük hex editörü inline düzenleme
        self._hex_edit_byte  = None   # düzenlenen byte index'i (string içinde, 0-N)
        self._hex_input_buf  = ''     # yazılan hex karakter tamponu ('', 'X', 'XX')

        self._build_ui()
        self._apply_lang()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def T(self, key, **kw):
        t = LANG[self.lang].get(key, key)
        return t.format(**kw) if kw else t

    # ══════════════════════════════════════════════════════════════════════
    #  UI İNŞA
    # ══════════════════════════════════════════════════════════════════════
    def _build_ui(self):
        self._build_header()
        tk.Frame(self, bg=BORDER, height=1).pack(fill='x')
        self._build_toolbar()
        self._build_filterbar()
        tk.Frame(self, bg=BORDER, height=1).pack(fill='x')
        self._build_body()

    def _build_header(self):
        f = tk.Frame(self, bg=BG)
        f.pack(fill='x')
        self.lbl_title    = tk.Label(f, font=("Courier New", 14, "bold"), bg=BG, fg=ACCENT)
        self.lbl_title.pack(side='left', padx=16, pady=8)
        self.lbl_subtitle = tk.Label(f, font=("Courier New", 9), bg=BG, fg=FG2)
        self.lbl_subtitle.pack(side='left')
        self.status_var   = tk.StringVar()
        tk.Label(f, textvariable=self.status_var, font=("Courier New", 9),
                 bg=BG, fg=GREEN).pack(side='right', padx=16)

    def _build_toolbar(self):
        tb = tk.Frame(self, bg=BG2, pady=5)
        tb.pack(fill='x')

        def btn(text, cmd, bg_col, w=14):
            b = tk.Button(tb, text=text, command=cmd, bg=bg_col, fg='white',
                          font=("Courier New", 9, "bold"), relief='flat',
                          cursor='hand2', width=w, padx=6, pady=4,
                          activebackground=BG3, activeforeground=ACCENT)
            b.pack(side='left', padx=3)
            return b

        self.btn_load   = btn("",          self.load_exe,        ACCENT2)
        self.btn_save   = btn("",          self.save_exe,        GREEN)
        self.btn_export = btn("",          self.export_json,     BG3, 13)
        self.btn_import = btn("",          self.import_json,     BG3, 13)
        self.btn_pe     = btn("🧬 PE Analiz", self.open_pe_analyzer, "#0d1a2e", 12)
        self.btn_pe.config(fg="#5ba8ff")
        self.btn_diff   = btn("⇄ EXE Fark", self.open_hex_diff,  "#1a0d2e", 11)
        self.btn_diff.config(fg="#c080ff")
        self.btn_log    = btn("📋 Log",    self.show_log,        "#1a1a2e", 8)
        self.btn_log.config(fg="#7a9fcc")

        self.btn_history = tk.Button(tb, command=self.show_history,
                                      bg="#1a2010", fg=YELLOW,
                                      font=("Courier New", 9, "bold"), relief='flat',
                                      cursor='hand2', width=12, padx=6, pady=4,
                                      activebackground=BG3, activeforeground=YELLOW)
        self.btn_history.pack(side='left', padx=3)

        self.btn_lang = tk.Button(tb, command=self.toggle_lang, bg=BG3, fg=ACCENT,
                                   font=("Courier New", 9, "bold"), relief='flat',
                                   cursor='hand2', width=13, padx=6, pady=4,
                                   activebackground=BG2, activeforeground=ACCENT)
        self.btn_lang.pack(side='right', padx=6)

        tk.Button(tb, text="★ Credits", command=self.show_credits,
                  bg=BG3, fg=YELLOW, font=("Courier New", 9, "bold"), relief='flat',
                  cursor='hand2', width=11, padx=6, pady=4,
                  activebackground=BG2, activeforeground=YELLOW).pack(side='right', padx=3)

        self.stat_var = tk.StringVar()
        tk.Label(tb, textvariable=self.stat_var, font=("Courier New", 9),
                 bg=BG2, fg=FG2).pack(side='right', padx=8)

    def _build_filterbar(self):
        fb = tk.Frame(self, bg=BG3, pady=4)
        fb.pack(fill='x')
        self.lbl_search = tk.Label(fb, font=("Courier New", 9), bg=BG3, fg=FG2)
        self.lbl_search.pack(side='left', padx=8)
        self.q_var = tk.StringVar()
        self.q_var.trace('w', lambda *_: self._apply_filter())
        tk.Entry(fb, textvariable=self.q_var, bg=BG2, fg=FG,
                 font=("Courier New", 10), insertbackground=ACCENT,
                 relief='flat', width=28).pack(side='left', padx=4, ipady=3)
        self.show_var = tk.StringVar(value="all")
        self.rb_all     = tk.Radiobutton(fb, variable=self.show_var, value="all",     command=self._apply_filter, bg=BG3, fg=FG, selectcolor=BG, font=("Courier New", 9), activebackground=BG3)
        self.rb_pending = tk.Radiobutton(fb, variable=self.show_var, value="notdone", command=self._apply_filter, bg=BG3, fg=FG, selectcolor=BG, font=("Courier New", 9), activebackground=BG3)
        self.rb_done    = tk.Radiobutton(fb, variable=self.show_var, value="done",    command=self._apply_filter, bg=BG3, fg=FG, selectcolor=BG, font=("Courier New", 9), activebackground=BG3)
        self.rb_native  = tk.Radiobutton(fb, variable=self.show_var, value="turkish", command=self._apply_filter, bg=BG3, fg=FG, selectcolor=BG, font=("Courier New", 9), activebackground=BG3)
        for rb in [self.rb_all, self.rb_pending, self.rb_done, self.rb_native]:
            rb.pack(side='left', padx=5)
        self.backup_info_var = tk.StringVar(value="")
        tk.Label(fb, textvariable=self.backup_info_var,
                 font=("Courier New", 8), bg=BG3, fg=YELLOW).pack(side='right', padx=12)

    def _build_body(self):
        body = tk.Frame(self, bg=BG)
        body.pack(fill='both', expand=True)

        left = tk.Frame(body, bg=BG2, width=700)
        left.pack(side='left', fill='both', expand=True)
        left.pack_propagate(False)

        sty = ttk.Style()
        sty.theme_use('clam')
        sty.configure("Treeview", background=BG2, foreground=FG,
                      fieldbackground=BG2, rowheight=24, font=("Courier New", 9))
        sty.configure("Treeview.Heading", background=BG3, foreground=ACCENT,
                      font=("Courier New", 9, "bold"), relief='flat')
        sty.map("Treeview", background=[('selected', BG3)], foreground=[('selected', ACCENT)])
        sty.configure("TNotebook",     background=BG2, borderwidth=0)
        sty.configure("TNotebook.Tab", background=BG3, foreground=FG2,
                       font=("Courier New", 9, "bold"), padding=[10, 4])
        sty.map("TNotebook.Tab", background=[('selected', BG)], foreground=[('selected', ACCENT)])

        self.nb = ttk.Notebook(left)
        self.nb.pack(fill='both', expand=True, padx=4, pady=4)
        self.nb.bind('<<NotebookTabChanged>>', self._on_tab_change)

        self._build_list_tab()
        self._build_hex_tab()

        right = tk.Frame(body, bg=BG, width=500)
        right.pack(side='right', fill='both')
        right.pack_propagate(False)
        self._build_editor(right)

    # ── List Tab ──────────────────────────────────────────────────────────
    def _build_list_tab(self):
        tab = tk.Frame(self.nb, bg=BG2)
        self.nb.add(tab, text=" 📋 Metin Listesi ")
        self.lbl_list = tk.Label(tab, font=("Courier New", 8, "bold"),
                                  bg=BG2, fg=FG2, padx=8, pady=2)
        self.lbl_list.pack(fill='x')
        lf = tk.Frame(tab, bg=BG2)
        lf.pack(fill='both', expand=True)
        cols = ('s', 'offset', 'orig', 'tr')
        self.tree = ttk.Treeview(lf, columns=cols, show='headings', selectmode='browse')
        self.tree.column('s',      width=26,  anchor='center', stretch=False)
        self.tree.column('offset', width=82,  anchor='center', stretch=False)
        self.tree.column('orig',   width=280, anchor='w')
        self.tree.column('tr',     width=280, anchor='w')
        self.tree.tag_configure('done',      foreground=GREEN)
        self.tree.tag_configure('turkish',   foreground=ACCENT)
        self.tree.tag_configure('undone',    foreground=FG)
        self.tree.tag_configure('relocated', foreground=YELLOW)
        vsb = tk.Scrollbar(lf, orient='vertical', command=self.tree.yview, bg=BG3)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')
        self.tree.pack(fill='both', expand=True)
        self.tree.bind('<<TreeviewSelect>>', self._on_select)

    # ── Hex Tab ───────────────────────────────────────────────────────────
    def _build_hex_tab(self):
        tab = tk.Frame(self.nb, bg="#06080d")
        self.nb.add(tab, text=" 🔢 Hex Görünümü ")

        # Arama çubuğu
        top = tk.Frame(tab, bg="#0e1118", pady=5)
        top.pack(fill='x')
        tk.Label(top, text="🔍", font=("Courier New", 11),
                 bg="#0e1118", fg=ACCENT).pack(side='left', padx=(10, 2))
        self.hv_q_var = tk.StringVar()
        self.hv_entry = tk.Entry(top, textvariable=self.hv_q_var,
                                  bg="#161b26", fg=FG, font=("Courier New", 10),
                                  insertbackground=ACCENT, relief='flat', width=26,
                                  highlightthickness=1, highlightcolor=ACCENT2,
                                  highlightbackground="#2a3045")
        self.hv_entry.pack(side='left', padx=4, ipady=4)
        self.hv_entry.bind('<Return>', lambda e: self._hv_search(1))
        self.hv_mode = tk.StringVar(value='text')
        for val, lbl in [('text', 'Metin'), ('hex', 'Hex')]:
            tk.Radiobutton(top, text=lbl, variable=self.hv_mode, value=val,
                           bg="#0e1118", fg=FG2, selectcolor="#0e1118",
                           activeforeground=ACCENT, activebackground="#0e1118",
                           font=("Courier New", 9)).pack(side='left', padx=3)
        for sym, d in [("◀", -1), ("▶", 1)]:
            tk.Button(top, text=sym, command=lambda x=d: self._hv_search(x),
                      bg="#1a2030", fg=FG, font=("Courier New", 10, "bold"),
                      relief='flat', cursor='hand2', padx=8, pady=2,
                      activebackground=ACCENT2, activeforeground='white',
                      bd=0).pack(side='left', padx=1)
        self.hv_match_lbl = tk.Label(top, text="", font=("Courier New", 9, "bold"),
                                      bg="#0e1118", fg=ACCENT2, width=8)
        self.hv_match_lbl.pack(side='left', padx=6)
        self.hv_status_lbl = tk.Label(top, text="← EXE yüklenince açılır",
                                       font=("Courier New", 8), bg="#0e1118", fg=FG2)
        self.hv_status_lbl.pack(side='right', padx=10)

        # Başlık
        hdr_str = ("  Offset    " +
                   "  00 01 02 03   04 05 06 07   08 09 0A 0B   0C 0D 0E 0F" +
                   "    ASCII           ")
        tk.Label(tab, text=hdr_str, font=("Courier New", 9),
                 bg="#0a0d14", fg="#2a3a50", anchor='w', padx=4).pack(fill='x')
        tk.Frame(tab, bg="#1a2030", height=1).pack(fill='x')

        # Ana hex metin alanı
        hv_frame = tk.Frame(tab, bg="#06080d")
        hv_frame.pack(fill='both', expand=True)
        hv_vsb = tk.Scrollbar(hv_frame, orient='vertical',   bg="#0e1118", troughcolor="#06080d", width=12)
        hv_vsb.pack(side='right', fill='y')
        hv_hsb = tk.Scrollbar(hv_frame, orient='horizontal', bg="#0e1118", troughcolor="#06080d", width=10)
        hv_hsb.pack(side='bottom', fill='x')

        self.hv_text = tk.Text(hv_frame, bg="#06080d", fg="#2d7a55",
                                font=("Courier New", 10), wrap='none', relief='flat',
                                cursor='ibeam', spacing1=2, spacing3=2,
                                selectbackground="#e8a045", selectforeground="#000000",
                                insertbackground="#06080d",
                                yscrollcommand=hv_vsb.set, xscrollcommand=hv_hsb.set)
        hv_vsb.config(command=self.hv_text.yview)
        hv_hsb.config(command=self.hv_text.xview)
        self.hv_text.pack(fill='both', expand=True)

        # Klavyeyle doğrudan metin değişikliğini engelle (editör aracılığıyla yapılmalı)
        for seq in ('<Delete>', '<BackSpace>', '<Control-v>', '<Control-x>'):
            self.hv_text.bind(seq, lambda e: 'break')

        self.hv_text.tag_configure('hv_addr', foreground="#2a4060")
        self.hv_text.tag_configure('hv_g0',   foreground="#3a9e72")
        self.hv_text.tag_configure('hv_g1',   foreground="#2a7054")
        self.hv_text.tag_configure('hv_asc',  foreground="#1a4030")
        self.hv_text.tag_configure('hv_str',  background="#071a10", foreground="#50e890")
        self.hv_text.tag_configure('hv_sel',  background="#0a2840", foreground="#60b8ff")
        self.hv_text.tag_configure('hv_mall', background="#1e1600", foreground="#c8a020")
        self.hv_text.tag_configure('hv_mcur', background="#7a5000", foreground="#ffffff")
        # v22: manuel yama rengi
        self.hv_text.tag_configure('hv_patch', background="#1a0a00", foreground="#ff8800")
        # v22: seçili byte highlight
        self.hv_text.tag_configure('hv_click', background="#2a1a50", foreground="#c8a0ff")

        self.hv_text.bind('<<Selection>>',     self._hv_on_sel_change)
        self.hv_text.bind('<ButtonRelease-1>', self._hv_on_release)

        # ── v22: Byte Editörü çubuğu ─────────────────────────────────────
        tk.Frame(tab, bg="#1a1a2e", height=1).pack(fill='x')
        edit_bar = tk.Frame(tab, bg="#0c0a18", pady=5)
        edit_bar.pack(fill='x')

        tk.Label(edit_bar, text="✎ BYTE EDİT:", font=("Courier New", 9, "bold"),
                 bg="#0c0a18", fg="#8060c0").pack(side='left', padx=(10, 4))

        self.hv_edit_off_lbl = tk.Label(edit_bar, text="Offset: —",
                                         font=("Courier New", 9), bg="#0c0a18", fg=FG2, width=18, anchor='w')
        self.hv_edit_off_lbl.pack(side='left', padx=2)

        self.hv_edit_cur_lbl = tk.Label(edit_bar, text="Mevcut: —",
                                         font=("Courier New", 9, "bold"), bg="#0c0a18", fg=ACCENT, width=16, anchor='w')
        self.hv_edit_cur_lbl.pack(side='left', padx=2)

        tk.Label(edit_bar, text="Yeni (hex):",
                 font=("Courier New", 9), bg="#0c0a18", fg=FG2).pack(side='left', padx=(8, 2))

        self.hv_edit_var = tk.StringVar()
        self.hv_edit_entry = tk.Entry(edit_bar, textvariable=self.hv_edit_var,
                                       width=4, bg="#1a1030", fg="#c8a0ff",
                                       font=("Courier New", 11, "bold"),
                                       insertbackground="#c8a0ff", relief='flat',
                                       highlightthickness=1, highlightcolor="#8060c0",
                                       highlightbackground="#2a1a40",
                                       justify='center')
        self.hv_edit_entry.pack(side='left', padx=4, ipady=3)
        self.hv_edit_entry.bind('<Return>', lambda e: self._hv_apply_edit())

        self.hv_apply_btn = tk.Button(edit_bar, text="⚡ Uygula",
                                       command=self._hv_apply_edit,
                                       bg="#2a1a40", fg="#c8a0ff",
                                       font=("Courier New", 9, "bold"), relief='flat',
                                       cursor='hand2', padx=10, pady=3, state='disabled',
                                       activebackground="#8060c0", activeforeground='white', bd=0)
        self.hv_apply_btn.pack(side='left', padx=4)

        # Yama sayacı
        self.hv_patch_lbl = tk.Label(edit_bar, text="",
                                      font=("Courier New", 8), bg="#0c0a18", fg="#ff8800")
        self.hv_patch_lbl.pack(side='left', padx=8)

        # Patch geri al butonu
        self.hv_undo_patch_btn = tk.Button(edit_bar, text="↩ Yamayı Geri Al",
                                            command=self._hv_undo_last_patch,
                                            bg="#2a1a10", fg="#ff8800",
                                            font=("Courier New", 8, "bold"), relief='flat',
                                            cursor='hand2', padx=8, pady=3, state='disabled',
                                            activebackground="#ff8800", activeforeground='black', bd=0)
        self.hv_undo_patch_btn.pack(side='left', padx=2)

        self.hv_edit_info_lbl = tk.Label(edit_bar,
                                          text="← Bayta tıkla → değerini değiştir → Enter/Uygula",
                                          font=("Courier New", 8), bg="#0c0a18", fg="#3a2a50")
        self.hv_edit_info_lbl.pack(side='right', padx=10)

        # ── Alt: string yükleme/gönderme çubuğu ─────────────────────────
        tk.Frame(tab, bg="#1a2030", height=1).pack(fill='x')
        bot = tk.Frame(tab, bg="#0e1118", pady=4)
        bot.pack(fill='x', side='bottom')
        tk.Frame(tab, bg="#1a2030", height=1).pack(fill='x', side='bottom')
        self.hv_sel_lbl = tk.Label(bot,
                                    text="🖱  Tıkla → string yükle  |  Sürükle → Orijinale Gönder  |  Sağ tık → Byte Seç",
                                    font=("Courier New", 9), bg="#0e1118", fg="#3a5060", anchor='w')
        self.hv_sel_lbl.pack(side='left', padx=10)
        self.btn_hv_send = tk.Button(bot, text="⬆ Orijinale Gönder",
                                      command=self._hv_send_selection,
                                      bg="#1a2a1a", fg="#50c050",
                                      font=("Courier New", 9, "bold"), relief='flat',
                                      cursor='hand2', padx=12, pady=3, state='disabled',
                                      activebackground=GREEN, activeforeground='black', bd=0)
        self.btn_hv_send.pack(side='right', padx=10)

        # Yama geçmişi (undo stack): [(offset, old_val), ...]
        self._patch_undo_stack = []

    # ── Editor (sağ panel) ────────────────────────────────────────────────
    def _build_editor(self, parent):
        self.lbl_editor = tk.Label(parent, font=("Courier New", 8, "bold"),
                                    bg=BG, fg=FG2, padx=12, pady=4)
        self.lbl_editor.pack(fill='x')

        inf = tk.Frame(parent, bg=BG)
        inf.pack(fill='x', padx=12)
        self.lbl_offset  = tk.Label(inf, font=("Courier New", 9), bg=BG, fg=FG2)
        self.lbl_offset.pack(side='left')
        self.lbl_maxsize = tk.Label(inf, font=("Courier New", 9), bg=BG, fg=FG2)
        self.lbl_maxsize.pack(side='right')

        self.lbl_reloc_badge = tk.Label(parent, font=("Courier New", 8, "bold"),
                                         bg=BG, fg=YELLOW, padx=12)
        self.lbl_reloc_badge.pack(fill='x')

        self.lbl_orig_hdr = tk.Label(parent, font=("Courier New", 8, "bold"),
                                      bg=BG, fg=FG2, padx=12)
        self.lbl_orig_hdr.pack(fill='x', pady=(6, 1))
        of = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
        of.pack(fill='x', padx=12)
        of_in = tk.Frame(of, bg=BG3)
        of_in.pack(fill='x')
        self.orig_box = tk.Text(of_in, height=5, bg=BG3, fg=FG, font=("Courier New", 10),
                                 wrap='word', relief='flat', state='disabled',
                                 insertbackground=ACCENT, selectbackground=BG2)
        orig_sb = tk.Scrollbar(of_in, orient='vertical', command=self.orig_box.yview,
                                bg=BG3, troughcolor=BG, width=10)
        self.orig_box.configure(yscrollcommand=orig_sb.set)
        orig_sb.pack(side='right', fill='y')
        self.orig_box.pack(side='left', fill='x', expand=True)

        self.warn_var = tk.StringVar()
        self.warn_lbl = tk.Label(parent, textvariable=self.warn_var,
                                  font=("Courier New", 8), bg=BG, fg=GREEN, padx=12)
        self.warn_lbl.pack(fill='x', pady=2)

        self.lbl_tr_hdr = tk.Label(parent, font=("Courier New", 8, "bold"),
                                    bg=BG, fg=ACCENT, padx=12)
        self.lbl_tr_hdr.pack(fill='x', pady=(4, 1))
        undo_hint = tk.Frame(parent, bg=BG)
        undo_hint.pack(fill='x', padx=12)
        tk.Label(undo_hint, text="Ctrl+Z: Geri Al   Ctrl+Y: İleri Al   Ctrl+Enter: Kaydet",
                 font=("Courier New", 7), bg=BG, fg=FG2, anchor='w').pack(side='left')

        tf = tk.Frame(parent, bg=ACCENT, padx=1, pady=1)
        tf.pack(fill='x', padx=12)
        tf_in = tk.Frame(tf, bg=BG2)
        tf_in.pack(fill='x')
        self.tr_box = tk.Text(tf_in, height=5, bg=BG2, fg=FG, font=("Courier New", 10),
                               wrap='word', relief='flat',
                               insertbackground=ACCENT, selectbackground=BG3,
                               undo=True, maxundo=100)
        tr_sb = tk.Scrollbar(tf_in, orient='vertical', command=self.tr_box.yview,
                              bg=BG3, troughcolor=BG, width=10)
        self.tr_box.configure(yscrollcommand=tr_sb.set)
        tr_sb.pack(side='right', fill='y')
        self.tr_box.pack(side='left', fill='x', expand=True)
        self.tr_box.bind('<KeyRelease>', self._update_warn)
        self.tr_box.bind('<Control-z>', self._tr_undo)
        self.tr_box.bind('<Control-Z>', self._tr_undo)
        self.tr_box.bind('<Control-y>', self._tr_redo)
        self.tr_box.bind('<Control-Y>', self._tr_redo)
        self.tr_box.bind('<Control-Return>', lambda e: (self._save_translation(), 'break')[1])

        self.line_ctr_var = tk.StringVar()
        lc_f = tk.Frame(parent, bg=BG)
        lc_f.pack(fill='x', padx=12, pady=(2, 0))
        self.lbl_linectr = tk.Label(lc_f, textvariable=self.line_ctr_var,
                                     font=("Courier New", 8), bg=BG, fg=FG2, anchor='w')
        self.lbl_linectr.pack(side='left')

        tool_row = tk.Frame(parent, bg=BG)
        tool_row.pack(fill='x', padx=12, pady=(3, 0))
        tk.Label(tool_row, text="Genişlik:", font=("Courier New", 8), bg=BG, fg=FG2).pack(side='left')
        self.width_var = tk.IntVar(value=24)
        tk.Spinbox(tool_row, from_=10, to=60, textvariable=self.width_var,
                   width=4, bg=BG2, fg=FG, font=("Courier New", 9),
                   insertbackground=ACCENT, relief='flat',
                   buttonbackground=BG3, command=self._update_warn
                   ).pack(side='left', padx=(2, 8))
        tk.Button(tool_row, text="↵ Otomatik Satır", command=self._auto_wrap,
                  bg=BG3, fg=FG, font=("Courier New", 8, "bold"), relief='flat',
                  cursor='hand2', padx=6, pady=2,
                  activebackground=ACCENT2, activeforeground='white').pack(side='left', padx=(0, 4))
        tk.Button(tool_row, text="👁 Önizle", command=self._show_preview,
                  bg=BG3, fg=YELLOW, font=("Courier New", 8, "bold"), relief='flat',
                  cursor='hand2', padx=6, pady=2,
                  activebackground=YELLOW, activeforeground='black').pack(side='left')

        self.reloc_var = tk.BooleanVar(value=False)
        self.chk_reloc = tk.Checkbutton(parent, variable=self.reloc_var,
                                         bg=BG, fg=YELLOW, font=("Courier New", 8),
                                         selectcolor=BG3, activebackground=BG,
                                         activeforeground=YELLOW)
        self.chk_reloc.pack(fill='x', padx=12, pady=(6, 2))

        self.btn_save_tr = tk.Button(parent, command=self._save_translation,
                                      bg=ACCENT, fg="#000", font=("Courier New", 10, "bold"),
                                      relief='flat', cursor='hand2', pady=7,
                                      activebackground=GREEN, activeforeground="#000")
        self.btn_save_tr.pack(fill='x', padx=12, pady=6)

        # Up/Down sadece liste odaklanmamışsa çalışsın
        self.bind('<Up>',   lambda e: self._prev() if self.focus_get() is not self.tr_box else None)
        self.bind('<Down>', lambda e: self._next() if self.focus_get() is not self.tr_box else None)

        nav = tk.Frame(parent, bg=BG)
        nav.pack(fill='x', padx=12)
        self.btn_prev = tk.Button(nav, command=self._prev, bg=BG3, fg=FG,
                                   font=("Courier New", 9), relief='flat', width=13, cursor='hand2')
        self.btn_prev.pack(side='left')
        self.btn_next = tk.Button(nav, command=self._next, bg=BG3, fg=FG,
                                   font=("Courier New", 9), relief='flat', width=13, cursor='hand2')
        self.btn_next.pack(side='right')

        self.lbl_hex_hdr = tk.Label(parent, font=("Courier New", 8, "bold"),
                                     bg=BG, fg=FG2, padx=12)
        self.lbl_hex_hdr.pack(fill='x', pady=(12, 1))
        hxf = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
        hxf.pack(fill='x', padx=12)
        hxf_in = tk.Frame(hxf, bg="#090b0f")
        hxf_in.pack(fill='x')
        self.hex_box = tk.Text(hxf_in, height=5, bg="#090b0f", fg="#3fa87a",
                                font=("Courier New", 8), wrap='none',
                                relief='flat', state='normal', cursor='ibeam',
                                insertbackground="#090b0f")
        hex_vsb = tk.Scrollbar(hxf_in, orient='vertical', command=self.hex_box.yview,
                               bg=BG3, troughcolor=BG, width=10)
        self.hex_box.configure(yscrollcommand=hex_vsb.set)
        hex_vsb.pack(side='right', fill='y')
        self.hex_box.pack(side='left', fill='x', expand=True)
        self.hex_box.tag_configure('addr',          foreground=FG2)
        self.hex_box.tag_configure('hexbyte',       foreground="#3fa87a")
        self.hex_box.tag_configure('ascii',         foreground="#7a9f7a")
        self.hex_box.tag_configure('selected_byte', background="#2a5040", foreground=ACCENT)
        # v22b: inline editör renkleri
        self.hex_box.tag_configure('hex_edit_sel',  background="#1a1a40", foreground="#a0a0ff")
        self.hex_box.tag_configure('hex_edit_inp1', background="#3a2200", foreground="#ffaa00")
        self.hex_box.tag_configure('hex_patched',   background="#1a0a00", foreground="#ff8800")
        self.hex_box.bind('<Button-1>', self._hex_click)
        self.hex_box.bind('<Key>',      self._hex_key_press)

        hex_sel = tk.Frame(parent, bg=BG)
        hex_sel.pack(fill='x', padx=12, pady=(2, 0))
        self.lbl_hex_sel = tk.Label(hex_sel, text="📌 Tıkla seç → hex gir → yaz  |  ⚡ Relocate",
                                     font=("Courier New", 8), bg=BG, fg=FG2, anchor='w')
        self.lbl_hex_sel.pack(side='left', fill='x', expand=True)
        self.btn_reloc_here = tk.Button(hex_sel, text="⚡ Bu Adresten Relocate",
                                         command=self._relocate_from_hex,
                                         bg=BG3, fg=YELLOW, font=("Courier New", 8, "bold"),
                                         relief='flat', cursor='hand2', padx=6, pady=2,
                                         state='disabled',
                                         activebackground=YELLOW, activeforeground='black')
        self.btn_reloc_here.pack(side='right')

        self.lbl_ptr_hdr = tk.Label(parent, font=("Courier New", 8, "bold"),
                                     bg=BG, fg=FG2, padx=12)
        self.lbl_ptr_hdr.pack(fill='x', pady=(8, 1))
        pf = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
        pf.pack(fill='x', padx=12)
        self.ptr_box = tk.Text(pf, height=2, bg="#090b0f", fg=ACCENT2,
                                font=("Courier New", 8), wrap='word',
                                relief='flat', state='disabled')
        self.ptr_box.pack(fill='x')

    # ══════════════════════════════════════════════════════════════════════
    #  v21: UNDO / REDO
    # ══════════════════════════════════════════════════════════════════════
    def _tr_undo(self, event=None):
        try:
            self.tr_box.edit_undo()
            self._update_warn()
        except tk.TclError:
            pass
        return 'break'

    def _tr_redo(self, event=None):
        try:
            self.tr_box.edit_redo()
            self._update_warn()
        except tk.TclError:
            pass
        return 'break'

    # ══════════════════════════════════════════════════════════════════════
    #  v22: BÜYÜK HEX BYTE EDİTÖRÜ
    # ══════════════════════════════════════════════════════════════════════
    def _hv_select_byte(self, abs_off):
        """Büyük hex görünümünde bir byte'ı seçer ve editör çubuğunu günceller."""
        if not self.pe or abs_off < 0 or abs_off >= len(self._hv_display):
            return
        self._hv_edit_off = abs_off
        cur_val = self._hv_display[abs_off]
        self.hv_edit_off_lbl.config(text=f"Offset: 0x{abs_off:08X}", fg=ACCENT2)
        self.hv_edit_cur_lbl.config(
            text=f"Mevcut: 0x{cur_val:02X}  ({cur_val:3d})",
            fg=ACCENT if abs_off in self._manual_patches else FG)
        self.hv_edit_var.set(f"{cur_val:02X}")
        self.hv_apply_btn.config(state='normal')

        # Önceki highlight kaldır, yeni ekle
        self.hv_text.tag_remove('hv_click', '1.0', 'end')
        BPR      = HV_BPR
        row      = abs_off // BPR + 1
        byte_idx = abs_off % BPR
        col_s    = hv_byte_to_col(byte_idx)
        col_e    = col_s + 2
        self.hv_text.tag_add('hv_click', f"{row}.{col_s}", f"{row}.{col_e}")
        self.hv_text.see(f"{row}.{col_s}")

        self.hv_edit_info_lbl.config(
            text=f"0x{abs_off:08X} seçili — yeni hex değeri gir → Enter",
            fg="#6040a0")
        self.hv_edit_entry.focus_set()
        self.hv_edit_entry.select_range(0, 'end')

    def _hv_apply_edit(self):
        """Editör çubuğundaki değeri ilgili byte'a yazar."""
        if self._hv_edit_off is None or not self.pe:
            return
        raw = self.hv_edit_var.get().strip().upper()
        # 1 veya 2 hex karakter kabul et
        if not re.match(r'^[0-9A-Fa-f]{1,2}$', raw):
            self.hv_edit_info_lbl.config(
                text=f"✘ Geçersiz hex: '{raw}'  (örnek: FF veya 3A)", fg=RED)
            self.hv_edit_entry.config(bg="#3a0000")
            self.after(600, lambda: self.hv_edit_entry.config(bg="#1a1030"))
            return

        new_val  = int(raw, 16)
        abs_off  = self._hv_edit_off
        old_val  = self._hv_display[abs_off]

        if old_val == new_val:
            self.hv_edit_info_lbl.config(text="Değer aynı, değişiklik yok.", fg=FG2)
            return

        # Undo stack'e ekle
        self._patch_undo_stack.append((abs_off, old_val))

        # Uygula
        self.pe.data[abs_off]       = new_val
        self._hv_display[abs_off]   = new_val
        self._manual_patches[abs_off] = new_val
        self.unsaved = True

        # Satırı yenile
        BPR  = HV_BPR
        fo   = (abs_off // BPR) * BPR
        row  = abs_off // BPR + 1
        row_bytes = bytearray(self._hv_display[fo:fo + BPR])
        new_line  = hv_format_row(fo, row_bytes)
        self.hv_text.delete(f"{row}.0", f"{row}.end")
        self.hv_text.insert(f"{row}.0", new_line)

        # Tag'leri geri uygula
        if fo in {s['offset'] & ~(BPR-1) for s in self.strings
                  if s['offset'] <= fo < s['offset'] + s['length']}:
            self.hv_text.tag_add('hv_str', f"{row}.0", f"{row}.end+1c")

        # Yama rengi: değiştirilmiş byte
        byte_idx = abs_off % BPR
        col_s    = hv_byte_to_col(byte_idx)
        self.hv_text.tag_add('hv_patch', f"{row}.{col_s}", f"{row}.{col_s+2}")
        self.hv_text.tag_add('hv_click', f"{row}.{col_s}", f"{row}.{col_s+2}")

        # UI güncelle
        self.hv_edit_cur_lbl.config(
            text=f"Mevcut: 0x{new_val:02X}  ({new_val:3d})", fg="#ff8800")
        patch_count = len(self._manual_patches)
        self.hv_patch_lbl.config(text=f"⚠ {patch_count} yama")
        self.hv_undo_patch_btn.config(state='normal')
        self.hv_edit_info_lbl.config(
            text=f"✔ 0x{abs_off:08X}: 0x{old_val:02X} → 0x{new_val:02X}", fg=GREEN)

        self._log(f"HEX EDIT 0x{abs_off:08X}: 0x{old_val:02X} → 0x{new_val:02X}")

        # Editörde yeni değeri hazırla
        self.hv_edit_entry.select_range(0, 'end')

    def _hv_undo_last_patch(self):
        """Son hex yamasını geri alır."""
        if not self._patch_undo_stack:
            return
        abs_off, old_val = self._patch_undo_stack.pop()
        new_val = self._hv_display[abs_off]   # şu anki

        self.pe.data[abs_off]     = old_val
        self._hv_display[abs_off] = old_val
        if abs_off in self._manual_patches:
            if old_val == (self._orig_raw[abs_off] if self._orig_raw else old_val):
                del self._manual_patches[abs_off]
            else:
                self._manual_patches[abs_off] = old_val

        # Satırı yenile
        BPR       = HV_BPR
        fo        = (abs_off // BPR) * BPR
        row       = abs_off // BPR + 1
        row_bytes = bytearray(self._hv_display[fo:fo + BPR])
        new_line  = hv_format_row(fo, row_bytes)
        self.hv_text.delete(f"{row}.0", f"{row}.end")
        self.hv_text.insert(f"{row}.0", new_line)
        self.hv_text.tag_remove('hv_patch', f"{row}.0", f"{row}.end")

        patch_count = len(self._manual_patches)
        self.hv_patch_lbl.config(text=f"⚠ {patch_count} yama" if patch_count else "")
        if not self._patch_undo_stack:
            self.hv_undo_patch_btn.config(state='disabled')

        self.hv_edit_info_lbl.config(
            text=f"↩ 0x{abs_off:08X}: 0x{new_val:02X} → 0x{old_val:02X} (geri alındı)", fg=YELLOW)
        self._log(f"HEX UNDO 0x{abs_off:08X}: 0x{new_val:02X} → 0x{old_val:02X}")

        if self._hv_edit_off == abs_off:
            self.hv_edit_cur_lbl.config(text=f"Mevcut: 0x{old_val:02X}  ({old_val:3d})", fg=FG)
            self.hv_edit_var.set(f"{old_val:02X}")

    # ══════════════════════════════════════════════════════════════════════
    #  DİL
    # ══════════════════════════════════════════════════════════════════════
    def toggle_lang(self):
        self.lang = "EN" if self.lang == "TR" else "TR"
        self._apply_lang()

    def _apply_lang(self):
        self.title(self.T("title").replace("⚔  ", ""))
        self.lbl_title.config(text=self.T("title"))
        self.lbl_subtitle.config(text=self.T("subtitle"))
        self.status_var.set(self.T("status_default"))
        self.btn_load.config(text=self.T("btn_load"))
        self.btn_save.config(text=self.T("btn_save"))
        self.btn_export.config(text=self.T("btn_export"))
        self.btn_import.config(text=self.T("btn_import"))
        self.btn_lang.config(text=self.T("btn_lang"))
        self.btn_history.config(text=self.T("btn_history"))
        self.lbl_search.config(text=self.T("lbl_search"))
        self.rb_all.config(text=self.T("filter_all"))
        self.rb_pending.config(text=self.T("filter_pending"))
        self.rb_done.config(text=self.T("filter_done"))
        self.rb_native.config(text=self.T("filter_native"))
        self.lbl_list.config(text=self.T("lbl_list"))
        self.lbl_editor.config(text=self.T("lbl_editor"))
        self.lbl_orig_hdr.config(text=self.T("lbl_orig"))
        self.lbl_tr_hdr.config(text=self.T("lbl_tr"))
        self.lbl_hex_hdr.config(text=self.T("lbl_hex"))
        self.lbl_ptr_hdr.config(text=self.T("lbl_ptrs"))
        self.chk_reloc.config(text=self.T("chk_reloc"))
        self.btn_save_tr.config(text=self.T("btn_save_tr"))
        self.btn_prev.config(text=self.T("btn_prev"))
        self.btn_next.config(text=self.T("btn_next"))
        self.lbl_offset.config(text=self.T("lbl_addr"))
        self.tree.heading('s',      text=self.T("col_status"))
        self.tree.heading('offset', text=self.T("col_offset"))
        self.tree.heading('orig',   text=self.T("col_orig"))
        self.tree.heading('tr',     text=self.T("col_tr"))
        self._update_warn()
        self._update_stats()

    # ══════════════════════════════════════════════════════════════════════
    #  LOGGING
    # ══════════════════════════════════════════════════════════════════════
    def _log(self, msg, level="INFO"):
        ts    = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        entry = (ts, level, msg)
        self._log_entries.append(entry)
        if hasattr(self, '_log_text_widget'):
            try:
                self._log_text_widget.insert('end', f"[{ts}] [{level:4s}]  {msg}\n", level)
                self._log_text_widget.see('end')
            except Exception:
                pass

    def _flush_log(self):
        if not self._log_path:
            return
        try:
            with open(self._log_path, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*60}\nOturum: {datetime.datetime.now()}\n{'='*60}\n")
                for ts, level, msg in self._log_entries:
                    f.write(f"[{ts}] [{level:4s}] {msg}\n")
        except Exception:
            pass

    def show_log(self):
        w = tk.Toplevel(self, bg="#05070d")
        w.title("📋 PM2 Log")
        w.geometry("800x440")
        tk.Frame(w, bg=ACCENT2, height=3).pack(fill='x')
        hdr = tk.Frame(w, bg="#0a0d14")
        hdr.pack(fill='x')
        tk.Label(hdr, text="📋  ÇALIŞMA LOGU", font=("Courier New", 10, "bold"),
                 bg="#0a0d14", fg=ACCENT2).pack(side='left', padx=12, pady=6)

        def flush_and_notify():
            self._flush_log()
            messagebox.showinfo("Log", f"Log kaydedildi:\n{self._log_path}", parent=w)

        tk.Button(hdr, text="💾 Diske Yaz", command=flush_and_notify,
                  bg=BG3, fg=GREEN, font=("Courier New", 8, "bold"),
                  relief='flat', cursor='hand2', padx=8, pady=3).pack(side='right', padx=8, pady=4)
        tk.Button(hdr, text="🗑 Temizle",
                  command=lambda: (self._log_entries.clear(),
                                   self._log_text_widget.delete('1.0', 'end')),
                  bg=BG3, fg=RED, font=("Courier New", 8, "bold"),
                  relief='flat', cursor='hand2', padx=8, pady=3).pack(side='right', padx=4, pady=4)

        frm = tk.Frame(w, bg="#05070d")
        frm.pack(fill='both', expand=True, padx=4, pady=4)
        self._log_text_widget = tk.Text(frm, bg="#05070d", fg="#2a9a55",
                                         font=("Courier New", 9), wrap='none', relief='flat')
        self._log_text_widget.tag_configure('ERR',  foreground=RED)
        self._log_text_widget.tag_configure('WARN', foreground=YELLOW)
        self._log_text_widget.tag_configure('INFO', foreground="#2a9a55")
        sb  = tk.Scrollbar(frm, orient='vertical',   command=self._log_text_widget.yview)
        hsb = tk.Scrollbar(frm, orient='horizontal', command=self._log_text_widget.xview)
        self._log_text_widget.configure(yscrollcommand=sb.set, xscrollcommand=hsb.set)
        sb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
        self._log_text_widget.pack(fill='both', expand=True)
        for ts, level, msg in self._log_entries:
            self._log_text_widget.insert('end', f"[{ts}] [{level:4s}]  {msg}\n", level)
        self._log_text_widget.see('end')

    # ══════════════════════════════════════════════════════════════════════
    #  YEDEK SİSTEMİ (v21)
    # ══════════════════════════════════════════════════════════════════════
    def _setup_backup_dir(self, exe_path):
        base = os.path.splitext(exe_path)[0]
        self._backup_dir = base + "_yedekler"
        try:
            os.makedirs(self._backup_dir, exist_ok=True)
            self._log(f"Yedek klasörü: {self._backup_dir}")
        except Exception as e:
            self._log(f"Yedek klasörü oluşturulamadı: {e}", "WARN")
            self._backup_dir = None

    def _auto_backup_json(self, reason="otomatik"):
        if not self._backup_dir or not self.strings:
            return
        try:
            ts       = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"yedek_{ts}.json"
            path     = os.path.join(self._backup_dir, filename)
            done_cnt = sum(1 for s in self.strings if s['translation'])
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.strings, f, ensure_ascii=False, indent=2)
            self._backup_count += 1
            entry = {
                'ts':     datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                'type':   'json',
                'path':   path,
                'reason': reason,
                'count':  done_cnt,
                'size':   os.path.getsize(path),
            }
            self._history.append(entry)
            self._update_backup_info()
            self._log(f"JSON yedek #{self._backup_count}: {filename}  ({done_cnt} çeviri)")
        except Exception as e:
            self._log(f"JSON yedek hatası: {e}", "WARN")

    def _auto_backup_exe(self, saved_path):
        if not self._backup_dir:
            return
        try:
            ts       = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"yedek_exe_{ts}.exe"
            bak_path = os.path.join(self._backup_dir, filename)
            shutil.copy2(saved_path, bak_path)
            sz = os.path.getsize(bak_path)
            entry = {
                'ts':     datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                'type':   'exe',
                'path':   bak_path,
                'reason': 'EXE kayıt',
                'count':  sum(1 for s in self.strings if s['translation']),
                'size':   sz,
            }
            self._history.append(entry)
            self._update_backup_info()
            self._log(f"EXE yedek: {filename}  ({sz//1024} KB)")
        except Exception as e:
            self._log(f"EXE yedek hatası: {e}", "WARN")

    def _update_backup_info(self):
        if self._history:
            last = self._history[-1]
            t    = last['type'].upper()
            cnt  = len(self._history)
            self.backup_info_var.set(f"💾 {cnt} yedek  |  son: {t}")

    # ══════════════════════════════════════════════════════════════════════
    #  GEÇMİŞ PENCERESİ (v21, bugfix: open_dir guard)
    # ══════════════════════════════════════════════════════════════════════
    def show_history(self):
        win = tk.Toplevel(self, bg="#08090f")
        win.title("🕓 Kayıt Geçmişi")
        win.geometry("820x520")
        win.grab_set()

        tk.Frame(win, bg=YELLOW, height=3).pack(fill='x')
        hdr = tk.Frame(win, bg="#0d1008")
        hdr.pack(fill='x')
        tk.Label(hdr, text="🕓  KAYIT GEÇMİŞİ", font=("Courier New", 11, "bold"),
                 bg="#0d1008", fg=YELLOW).pack(side='left', padx=14, pady=8)
        if self._backup_dir:
            tk.Label(hdr, text=self._backup_dir, font=("Courier New", 8),
                     bg="#0d1008", fg=FG2).pack(side='left', padx=6)

        if not self._history:
            tk.Label(win, text="\n\n  Henüz yedek yok.\n  EXE yükleyin ve çeviri kaydedin.",
                     font=("Courier New", 11), bg="#08090f", fg=FG2).pack(expand=True)
            tk.Button(win, text="Kapat", command=win.destroy,
                      bg=BG3, fg=FG, font=("Courier New", 9), relief='flat',
                      cursor='hand2', padx=12, pady=4).pack(pady=12)
            return

        cols = ('ts', 'type', 'reason', 'count', 'size')
        sty  = ttk.Style()
        sty.configure("H.Treeview", background="#0d1008", foreground=FG,
                      fieldbackground="#0d1008", rowheight=22, font=("Courier New", 9))
        sty.configure("H.Treeview.Heading", background="#1a2010", foreground=YELLOW,
                      font=("Courier New", 9, "bold"), relief='flat')
        sty.map("H.Treeview",
                background=[('selected', '#1a2a10')],
                foreground=[('selected', YELLOW)])

        tf = tk.Frame(win, bg="#08090f")
        tf.pack(fill='both', expand=True, padx=6, pady=6)
        tv = ttk.Treeview(tf, columns=cols, show='headings', selectmode='browse', style="H.Treeview")
        tv.heading('ts',     text='Tarih / Saat')
        tv.heading('type',   text='Tür')
        tv.heading('reason', text='Sebep')
        tv.heading('count',  text='Çeviri')
        tv.heading('size',   text='Boyut')
        tv.column('ts',     width=160, anchor='w')
        tv.column('type',   width=60,  anchor='center')
        tv.column('reason', width=160, anchor='w')
        tv.column('count',  width=70,  anchor='center')
        tv.column('size',   width=90,  anchor='center')
        tv.tag_configure('json', foreground=GREEN)
        tv.tag_configure('exe',  foreground=ACCENT2)

        vsb = tk.Scrollbar(tf, orient='vertical', command=tv.yview, bg="#0d1008")
        tv.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')
        tv.pack(fill='both', expand=True)

        for i, e in enumerate(reversed(self._history)):
            sz_str = f"{e['size']//1024} KB" if e['size'] >= 1024 else f"{e['size']} B"
            tv.insert('', 'end', iid=str(i),
                      values=(e['ts'], e['type'].upper(), e['reason'],
                              f"{e['count']} string", sz_str),
                      tags=(e['type'],))

        bot = tk.Frame(win, bg="#0d1008", pady=6)
        bot.pack(fill='x')
        tk.Frame(win, bg="#2a3010", height=1).pack(fill='x')

        info_lbl = tk.Label(bot, text="Bir yedek seçin",
                             font=("Courier New", 9), bg="#0d1008", fg=FG2)
        info_lbl.pack(side='left', padx=14)

        # Butonları önceden oluştur, sonra on_select içinde aktif et
        btn_restore  = tk.Button(bot, text="↩ JSON Geri Yükle", command=lambda: restore_json(),
                                  bg="#1a2a10", fg=GREEN, font=("Courier New", 9, "bold"),
                                  relief='flat', cursor='hand2', padx=10, pady=4,
                                  state='disabled', activebackground=GREEN, activeforeground='black')
        btn_restore.pack(side='right', padx=4)

        # v22 BUG FIX: backup_dir None kontrolü
        btn_open_dir = tk.Button(bot, text="📁 Klasörü Aç",
                                  command=lambda: (os.startfile(self._backup_dir)
                                                   if self._backup_dir and os.path.exists(self._backup_dir)
                                                   else None),
                                  bg=BG3, fg=ACCENT2, font=("Courier New", 9, "bold"),
                                  relief='flat', cursor='hand2', padx=10, pady=4,
                                  state='normal' if self._backup_dir else 'disabled',
                                  activebackground=ACCENT2, activeforeground='black')
        btn_open_dir.pack(side='right', padx=4)

        def on_select(_=None):
            sel = tv.selection()
            if not sel:
                return
            idx = int(sel[0])
            e   = list(reversed(self._history))[idx]
            info_lbl.config(text=f"Seçili: {os.path.basename(e['path'])}", fg=ACCENT)
            btn_restore.config(state='normal' if e['type'] == 'json' else 'disabled')

        tv.bind('<<TreeviewSelect>>', on_select)

        def restore_json():
            sel = tv.selection()
            if not sel: return
            idx = int(sel[0])
            e   = list(reversed(self._history))[idx]
            if e['type'] != 'json': return
            if not messagebox.askyesno("Geri Yükle",
                f"{e['ts']} tarihli yedeği yükle?\n({e['count']} çeviri)\n\nMevcut çeviriler üzerine yazılacak!",
                parent=win):
                return
            try:
                with open(e['path'], 'r', encoding='utf-8') as f:
                    data = json.load(f)
                lut = {s['offset']: s for s in self.strings}
                updated = 0
                for item in data:
                    if item['offset'] in lut and item.get('translation'):
                        lut[item['offset']]['translation'] = item['translation']
                        lut[item['offset']]['relocated']   = item.get('relocated', False)
                        updated += 1
                if self._orig_raw:
                    for s in self.strings:
                        if s.get('translation'):
                            self._hv_update_rows(s)
                self._apply_filter()
                self._update_stats()
                self._log(f"Yedek geri yüklendi: {e['path']}  ({updated} çeviri)")
                messagebox.showinfo("✔ Geri Yüklendi", f"{updated} çeviri yüklendi.", parent=win)
            except Exception as ex:
                messagebox.showerror("Hata", str(ex), parent=win)

        def delete_selected():
            sel = tv.selection()
            if not sel: return
            idx = int(sel[0])
            e   = list(reversed(self._history))[idx]
            if not messagebox.askyesno("Sil", f"Bu yedeği sil?\n{os.path.basename(e['path'])}", parent=win):
                return
            try:
                os.remove(e['path'])
                self._history.remove(e)
                tv.delete(sel[0])
                self._update_backup_info()
                info_lbl.config(text="Silindi.", fg=RED)
            except Exception as ex:
                messagebox.showerror("Hata", str(ex), parent=win)

        tk.Button(bot, text="🗑 Seçili Sil", command=delete_selected,
                  bg=BG3, fg=RED, font=("Courier New", 9, "bold"),
                  relief='flat', cursor='hand2', padx=10, pady=4,
                  activebackground=RED, activeforeground='white').pack(side='right', padx=4)
        tk.Button(bot, text="Kapat", command=win.destroy,
                  bg=BG3, fg=FG, font=("Courier New", 9), relief='flat',
                  cursor='hand2', padx=12, pady=4).pack(side='left', padx=6)

    # ══════════════════════════════════════════════════════════════════════
    #  EXE YÜKLE
    # ══════════════════════════════════════════════════════════════════════
    def load_exe(self):
        path = filedialog.askopenfilename(
            title="EXE Seç" if self.lang == "TR" else "Select EXE",
            filetypes=[("EXE files", "*.exe"), ("All files", "*.*")])
        if not path:
            return
        self.exe_path        = path
        raw                  = open(path, 'rb').read()
        self._orig_raw       = raw
        self._log_path       = path.replace('.exe', '_pm2.log')
        self.pe              = PEInfo(raw)
        self.strings         = extract_strings(bytes(self.pe.data))
        self._hv_display     = bytearray(self.pe.data)
        self._hv_loaded      = False
        self._log_entries    = []
        self._history        = []
        self._backup_count   = 0
        self._manual_patches = {}      # v22: yeni EXE = yamalar sıfırla
        self._patch_undo_stack = []
        self.backup_info_var.set("")
        self._setup_backup_dir(path)
        self._log(f"EXE yüklendi: {path}  ({len(raw):,} byte)")
        self._log(f"String sayısı: {len(self.strings)}")
        self._apply_filter()
        self.status_var.set(("✔ Loaded: " if self.lang == "EN" else "✔ Yüklendi: ")
                            + os.path.basename(path))
        self._update_stats()
        # Hex editör çubuğunu sıfırla
        self.hv_edit_off_lbl.config(text="Offset: —", fg=FG2)
        self.hv_edit_cur_lbl.config(text="Mevcut: —", fg=FG)
        self.hv_edit_var.set("")
        self.hv_apply_btn.config(state='disabled')
        self.hv_patch_lbl.config(text="")
        self.hv_undo_patch_btn.config(state='disabled')

    # ══════════════════════════════════════════════════════════════════════
    #  FİLTRE & TREE
    # ══════════════════════════════════════════════════════════════════════
    def _apply_filter(self, *_):
        q    = self.q_var.get().lower()
        show = self.show_var.get()
        self.filtered = []
        for s in self.strings:
            done   = bool(s['translation'])
            native = is_turkish(s['text'])
            if show == 'notdone'  and (done or native): continue
            if show == 'done'     and not done:         continue
            if show == 'turkish'  and not native:       continue
            if q and q not in s['text'].lower() and q not in s['translation'].lower():
                continue
            self.filtered.append(s)
        self._refresh_tree()

    def _refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for s in self.filtered:
            done   = bool(s['translation'])
            native = is_turkish(s['text'])
            reloc  = s.get('relocated', False)
            if reloc:    tag, ico = 'relocated', '⚡'
            elif done:   tag, ico = 'done',      '✔'
            elif native: tag, ico = 'turkish',   '~'
            else:        tag, ico = 'undone',    ' '
            op = s['text'][:44].replace('\r\n', '↵').replace('\n', '↵')
            tp = (s['translation'][:44].replace('\r\n', '↵').replace('\n', '↵')
                  if s['translation'] else '')
            self.tree.insert('', 'end', iid=str(s['offset']),
                             values=(ico, hex(s['offset']), op, tp), tags=(tag,))
        if self._hv_loaded:
            self._hv_rebuild_str_ranges()
            self._hv_retag_strings()

    def _update_stats(self):
        if not self.strings:
            return
        t = len(self.strings)
        d = sum(1 for s in self.strings if s['translation'])
        r = sum(1 for s in self.strings if s.get('relocated'))
        n = sum(1 for s in self.strings if is_turkish(s['text']) and not s['translation'])
        p = t - d - n
        self.stat_var.set(self.T("stat", t=t, d=d, r=r, n=n, p=p))

    # ══════════════════════════════════════════════════════════════════════
    #  SEÇİM & EDİTÖR
    # ══════════════════════════════════════════════════════════════════════
    def _on_select(self, *_):
        sel = self.tree.selection()
        if not sel:
            return
        off = int(sel[0])
        s   = next((x for x in self.filtered if x['offset'] == off), None)
        if s:
            self.selected = s
            self._show_entry(s)

    def _show_entry(self, s):
        self.orig_box.config(state='normal')
        self.orig_box.delete('1.0', 'end')
        self.orig_box.insert('end', s['text'])
        self.orig_box.config(state='disabled')

        self.tr_box.delete('1.0', 'end')
        if s['translation']:
            self.tr_box.insert('end', s['translation'])
        self.tr_box.edit_reset()   # undo geçmişini sıfırla

        self.lbl_offset.config(
            text=f"{'Offset' if self.lang=='EN' else 'Adres'}: {hex(s['offset'])}")
        self.lbl_maxsize.config(text=self.T("max_lbl", n=s['length']))
        self.lbl_reloc_badge.config(
            text=self.T("relocated_lbl", addr=hex(s.get('new_offset', 0)))
            if s.get('relocated') else "")

        self._refresh_small_hex(s)

        ptrs = self.pe.find_pointers(s['offset']) if self.pe else []
        pt   = ', '.join(hex(p) for p in ptrs[:8]) if ptrs else '—'
        self.ptr_box.config(state='normal')
        self.ptr_box.delete('1.0', 'end')
        self.ptr_box.insert('end', pt)
        self.ptr_box.config(state='disabled')

        self.hex_sel_off = None
        self._hex_edit_byte = None
        self._hex_input_buf = ''
        self.lbl_hex_sel.config(text="📌 Tıkla seç → hex gir → yaz  |  ⚡ Relocate", fg=FG2)
        self.btn_reloc_here.config(state='disabled')

        self._update_warn()
        self.tr_box.focus_set()

    def _refresh_small_hex(self, s):
        display = s['translation'] if s.get('translation') else s['text']
        # v22b FIX: _hv_display oku — çeviriler + manuel yamalar buraya yazılıyor
        # pe.data DEĞİL: o sadece ham orijinal + hex editör yamalarını tutar
        if self._hv_display and not s.get('_custom') and len(self._hv_display) > s['offset']:
            off = s['offset']
            ln  = s['length']
            raw = bytes(self._hv_display[off:off + ln])
        elif self.pe and not s.get('_custom'):
            # _hv_display henüz oluşturulmadıysa pe.data'dan al
            off = s['offset']
            ln  = s['length']
            raw = bytes(self.pe.data)[off:off + ln]
        else:
            raw  = display.encode('windows-1254', errors='replace')
        BPR  = 16
        self.hex_box.delete('1.0', 'end')
        self._hex_raw   = bytearray(raw)
        self._hex_start = s['offset']
        self._hex_edit_byte = None
        self._hex_input_buf = ''
        ADDR = 10
        for row_off in range(0, len(raw), BPR):
            chunk    = bytearray(raw[row_off:row_off + BPR])
            file_off = s['offset'] + row_off
            self.hex_box.insert('end', f"{file_off:08X}: ", 'addr')
            for bi, b in enumerate(chunk):
                abs_off = file_off + bi
                tag = 'hex_patched' if abs_off in self._manual_patches else 'hexbyte'
                self.hex_box.insert('end', f"{b:02X}", tag)
                self.hex_box.insert('end', ' ')
                if bi == 7:
                    self.hex_box.insert('end', ' ')
            missing = BPR - len(chunk)
            self.hex_box.insert('end', '   ' * missing + ('  ' if missing > 8 else ''))
            asc = ''.join(chr(b) if 0x20 <= b < 0x7F else '.' for b in chunk)
            self.hex_box.insert('end', f" |{asc}|\n", 'ascii')
        # hex_box state=normal kalır — inline editör için

    def _update_warn(self, *_):
        if not self.selected:
            return
        text = self.tr_box.get('1.0', 'end-1c')
        try:    enc = text.encode('windows-1254')
        except: enc = text.encode('utf-8', errors='replace')
        used  = len(enc)
        mx    = self.selected['length']
        reloc = self.reloc_var.get()
        if used <= mx:
            self.warn_var.set(self.T("warn_ok", used=used, max=mx))
            self.warn_lbl.config(fg=GREEN)
        elif reloc:
            self.warn_var.set(self.T("warn_reloc", used=used, max=mx))
            self.warn_lbl.config(fg=YELLOW)
        else:
            self.warn_var.set(self.T("warn_over", used=used, max=mx, over=used - mx))
            self.warn_lbl.config(fg=RED)

        max_w  = self.width_var.get()
        lines  = text.split('\n')
        parts  = []
        over_any = False
        for i, line in enumerate(lines[:6], 1):
            n = len(line)
            if n > max_w:
                parts.append(f"S{i}:{n}⚠")
                over_any = True
            else:
                parts.append(f"S{i}:{n}")
        if len(lines) > 6:
            parts.append(f"+{len(lines)-6}")
        self.line_ctr_var.set("  ".join(parts))
        self.lbl_linectr.config(fg=RED if over_any else FG2)

    def _auto_wrap(self):
        if not self.selected:
            return
        text  = self.tr_box.get('1.0', 'end-1c')
        max_w = self.width_var.get()
        words = text.replace('\n', ' ').split()
        lines, cur = [], ''
        for w in words:
            if cur and len(cur) + 1 + len(w) > max_w:
                lines.append(cur); cur = w
            else:
                cur = (cur + ' ' + w).strip()
        if cur:
            lines.append(cur)
        self.tr_box.delete('1.0', 'end')
        self.tr_box.insert('end', '\n'.join(lines))
        self._update_warn()

    def _show_preview(self):
        if not self.selected:
            return
        text  = self.tr_box.get('1.0', 'end-1c')
        max_w = self.width_var.get()
        lines = text.split('\n')
        win   = tk.Toplevel(self, bg="#2a1a2e")
        win.title("👁 Önizleme")
        win.geometry("420x320")
        win.grab_set()
        tk.Frame(win, bg=ACCENT, height=3).pack(fill='x')
        txt_f = tk.Frame(win, bg="#1a0f1e", padx=8, pady=8)
        txt_f.pack(fill='both', expand=True, padx=10, pady=8)
        visible   = lines[:6]
        truncated = len(lines) > 6
        for ln in visible:
            over = len(ln) > max_w
            tk.Label(txt_f, text=ln or " ", font=("Courier New", 11),
                     bg="#1a0f1e", fg=RED if over else FG, anchor='w').pack(fill='x')
        if truncated:
            tk.Label(txt_f, text=f"▼ +{len(lines)-6} satır daha",
                     font=("Courier New", 7), bg="#7a3060", fg=RED).pack()
        info_lines = []
        for i, ln in enumerate(visible, 1):
            mark = " ⚠" if len(ln) > max_w else ""
            info_lines.append(f"S{i}:{len(ln)}/{max_w}{mark}")
        tk.Label(win, text="  ".join(info_lines[:3]),
                 font=("Courier New", 8), bg="#2a1a2e", fg=FG2).pack()
        tk.Button(win, text="Kapat", command=win.destroy,
                  bg=ACCENT, fg="#000", font=("Courier New", 9, "bold"),
                  relief='flat', cursor='hand2', width=10, pady=4,
                  activebackground=GREEN).pack(pady=8)

    # ── Kaydet çeviri ─────────────────────────────────────────────────────
    def _save_translation(self):
        if not self.selected:
            return
        text = self.tr_box.get('1.0', 'end-1c').strip()
        if not text:
            self.selected['translation'] = ''
            self.selected['relocated']   = False
            self._refresh_tree(); self._update_stats(); self._next()
            return
        try:
            enc = text.encode('windows-1254')
        except Exception as e:
            messagebox.showerror(self.T("err_enc_title"), self.T("err_enc_msg", e=e))
            return
        if len(enc) > self.selected['length']:
            if not self.reloc_var.get():
                messagebox.showerror(self.T("err_long_title"),
                    self.T("err_long_msg", used=len(enc),
                           max=self.selected['length'],
                           over=len(enc) - self.selected['length']))
                return
            self.selected['relocated'] = True
        else:
            self.selected['relocated'] = False

        self.selected['translation'] = text
        self.unsaved = True

        # ── v22b FIX: _custom entry (hex'ten gönderilen) → _manual_patches'e yaz ──
        if self.selected.get('_custom') and self.pe:
            off  = self.selected['offset']
            ln   = self.selected['length']
            padded = bytearray(enc) + b'\x00' * max(0, ln - len(enc))
            padded = padded[:ln]
            for i, b in enumerate(padded):
                foff = off + i
                if 0 <= foff < len(self.pe.data):
                    old_b = self.pe.data[foff]
                    if old_b != b:
                        self._patch_undo_stack.append((foff, old_b))
                        self.pe.data[foff]   = b
                        self._manual_patches[foff] = b
                        if foff < len(self._hv_display):
                            self._hv_display[foff] = b
            self._log(f"CUSTOM PATCH 0x{off:08X} [{ln}b] {repr(text[:28])}")
            patch_count = len(self._manual_patches)
            self.hv_patch_lbl.config(text=f"⚠ {patch_count} yama")
            self.hv_undo_patch_btn.config(state='normal')

        self._refresh_tree(); self._update_stats()
        self._hv_update_rows(self.selected)
        self._refresh_small_hex(self.selected)

        # Otomatik yedek: her 5 çeviride veya relocation varsa
        done_cnt = sum(1 for s in self.strings if s['translation'])
        if done_cnt == 1 or done_cnt % 5 == 0 or self.selected.get('relocated'):
            reason = f"Çeviri #{done_cnt}" + (" (reloc)" if self.selected.get('relocated') else "")
            self._auto_backup_json(reason)

        self._next()

    # ── Nav ───────────────────────────────────────────────────────────────
    def _nav(self, delta):
        if not self.filtered:
            return
        sel = self.tree.selection()
        if sel:
            off = int(sel[0])
            idx = next((i for i, s in enumerate(self.filtered) if s['offset'] == off), 0)
            idx = max(0, min(len(self.filtered) - 1, idx + delta))
        else:
            idx = 0
        s = self.filtered[idx]
        self.tree.selection_set(str(s['offset']))
        self.tree.see(str(s['offset']))
        self.selected = s
        self._show_entry(s)

    def _next(self): self._nav(+1)
    def _prev(self): self._nav(-1)

    # ── Küçük hex tıklama (v20 orijinal logic, v22 restore) ───────────────
    def _hex_click(self, event):
        if not self.selected or not hasattr(self, '_hex_raw'):
            return
        idx      = self.hex_box.index(f"@{event.x},{event.y}")
        row, col = (int(x) for x in idx.split('.'))
        row -= 1
        ADDR = 10
        BPR  = 16
        if col < ADDR:
            byte_in_row = 0
        else:
            hc = col - ADDR
            byte_in_row = min(8 + (hc - 25) // 3, 15) if hc >= 25 else min(hc // 3, 7)
        bi = row * BPR + byte_in_row
        if bi < 0 or bi >= len(self._hex_raw):
            return
        foff = self._hex_start + bi
        self.hex_sel_off = foff
        self.btn_reloc_here.config(state='normal')
        self._hex_move_to_byte(bi)   # v22b: inline editör modu

    def _hex_byte_col(self, byte_in_row):
        """Byte index → küçük hex kutusundaki kolon başlangıcı."""
        ADDR = 10
        return ADDR + (byte_in_row * 3 if byte_in_row < 8 else 25 + (byte_in_row - 8) * 3)

    def _hex_move_to_byte(self, bi):
        """Küçük hex editöründe imleci bi. byte'a taşı ve edit moduna gir."""
        if not hasattr(self, '_hex_raw') or bi < 0 or bi >= len(self._hex_raw):
            return
        BPR = 16
        self._hex_edit_byte = bi
        self._hex_input_buf = ''
        foff = self._hex_start + bi
        self.hex_sel_off = foff
        row = bi // BPR + 1
        cs  = self._hex_byte_col(bi % BPR)
        # Tüm vurguları temizle, seçiliyi işaretle
        self.hex_box.tag_remove('selected_byte',  '1.0', 'end')
        self.hex_box.tag_remove('hex_edit_sel',   '1.0', 'end')
        self.hex_box.tag_remove('hex_edit_inp1',  '1.0', 'end')
        self.hex_box.tag_add('hex_edit_sel', f"{row}.{cs}", f"{row}.{cs+2}")
        self.lbl_hex_sel.config(
            text=f"✎ 0x{foff:08X}  (+{bi})  =  0x{self._hex_raw[bi]:02X}  — hex gir: ",
            fg="#a0a0ff")
        self.hex_box.focus_set()

    def _hex_key_press(self, event):
        """Küçük hex kutusu — tüm klavye girdisini yakala."""
        if self._hex_edit_byte is None:
            return 'break'
        ks = event.keysym
        ch = event.char.upper()
        # Navigasyon
        if ks in ('Tab', 'Right'):
            self._hex_move_to_byte(self._hex_edit_byte + 1); return 'break'
        if ks == 'Left':
            self._hex_move_to_byte(self._hex_edit_byte - 1); return 'break'
        if ks == 'Up':
            self._hex_move_to_byte(max(0, self._hex_edit_byte - 16)); return 'break'
        if ks == 'Down':
            self._hex_move_to_byte(self._hex_edit_byte + 16); return 'break'
        if ks == 'Escape':
            self._hex_edit_byte = None; self._hex_input_buf = ''
            self.hex_box.tag_remove('hex_edit_sel',  '1.0', 'end')
            self.hex_box.tag_remove('hex_edit_inp1', '1.0', 'end')
            self.lbl_hex_sel.config(text="📌 Bayta tıkla → düzenle", fg=FG2)
            return 'break'
        # Hex input
        if ch in '0123456789ABCDEF':
            buf = self._hex_input_buf + ch
            bi  = self._hex_edit_byte
            BPR = 16
            row = bi // BPR + 1
            cs  = self._hex_byte_col(bi % BPR)
            if len(buf) == 1:
                # 1. karakter: "X?" göster
                self._hex_input_buf = buf
                self.hex_box.delete(f"{row}.{cs}", f"{row}.{cs+2}")
                self.hex_box.insert(f"{row}.{cs}", buf[0] + '?', 'hex_edit_inp1')
                self.lbl_hex_sel.config(
                    text=f"✎ 0x{self._hex_start+bi:08X}  →  {buf[0]}?  (2. hex char...)",
                    fg="#ffaa00")
            else:
                # 2. karakter: uygula
                self._hex_input_buf = ''
                self._hex_commit_byte(bi, int(buf, 16))
        return 'break'   # başka hiçbir şeyin widget'a yazmasına izin verme

    def _hex_commit_byte(self, bi, new_val):
        """Küçük hex editöründe byte'ı yazar ve bir sonraki byte'a geçer."""
        if not self.pe or not hasattr(self, '_hex_raw'):
            return
        foff    = self._hex_start + bi
        old_val = self._hex_raw[bi]
        # Uygula
        self.pe.data[foff]           = new_val
        if foff < len(self._hv_display):
            self._hv_display[foff]   = new_val
        self._hex_raw[bi]            = new_val
        self._manual_patches[foff]   = new_val
        self._patch_undo_stack.append((foff, old_val))
        self.unsaved = True
        # Satırı yenile
        BPR = 16
        row = bi // BPR + 1
        row_start = (bi // BPR) * BPR
        chunk     = self._hex_raw[row_start:row_start + BPR]
        file_off  = self._hex_start + row_start
        self.hex_box.delete(f"{row}.0", f"{row}.end")
        self.hex_box.insert(f"{row}.0", f"{file_off:08X}: ", 'addr')
        ADDR = 10
        for k, b in enumerate(chunk):
            abs_off = self._hex_start + row_start + k
            tag = 'hex_patched' if abs_off in self._manual_patches else 'hexbyte'
            self.hex_box.insert(f"{row}.end", f"{b:02X}", tag)
            self.hex_box.insert(f"{row}.end", ' ')
            if k == 7:
                self.hex_box.insert(f"{row}.end", ' ')
        asc = ''.join(chr(b) if 0x20 <= b < 0x7F else '.' for b in chunk)
        self.hex_box.insert(f"{row}.end", f" |{asc}|", 'ascii')
        # Log & büyük hex'i güncelle
        self._log(f"SMALL HEX EDIT 0x{foff:08X}: 0x{old_val:02X} → 0x{new_val:02X}")
        patch_count = len(self._manual_patches)
        self.hv_patch_lbl.config(text=f"⚠ {patch_count} yama")
        self.hv_undo_patch_btn.config(state='normal')
        # Büyük hex görünümünü de güncelle (yüklüyse)
        if self._hv_loaded:
            hv_BPR  = HV_BPR
            hv_row  = foff // hv_BPR + 1
            hv_fo   = (foff // hv_BPR) * hv_BPR
            hv_rb   = bytearray(self._hv_display[hv_fo:hv_fo + hv_BPR])
            hv_line = hv_format_row(hv_fo, hv_rb)
            self.hv_text.delete(f"{hv_row}.0", f"{hv_row}.end")
            self.hv_text.insert(f"{hv_row}.0", hv_line)
            byte_idx = foff % hv_BPR
            col_s    = hv_byte_to_col(byte_idx)
            self.hv_text.tag_add('hv_patch', f"{hv_row}.{col_s}", f"{hv_row}.{col_s+2}")
        # Sonraki byte'a geç
        self._hex_move_to_byte(bi + 1)

    def _relocate_from_hex(self):
        if self.hex_sel_off is None or not self.pe:
            return
        off  = self.hex_sel_off
        va   = self.pe.file_to_va(off)
        ptrs = self.pe.find_pointers(off)
        # v22 BUG FIX: va None olabilir, f-string güvenli hale getirildi
        va_str = f"0x{va:08X}" if va is not None else "N/A"
        if not ptrs:
            messagebox.showinfo("Relocation",
                f"0x{off:08X} → VA {va_str}\n\nBu adrese pointer bulunamadı.")
            return
        messagebox.showinfo("⚡ Pointer Bilgisi",
            f"Dosya ofseti : 0x{off:08X}\n"
            f"VA           : {va_str}\n"
            f"Pointer'lar  : {', '.join(hex(p) for p in ptrs[:12])}\n\n"
            "Relocation kutusunu işaretleyip çeviriyi kaydedin.")

    # ══════════════════════════════════════════════════════════════════════
    #  BÜYÜK HEX GÖRÜNÜMÜ
    # ══════════════════════════════════════════════════════════════════════
    def _on_tab_change(self, event):
        try:
            tab = self.nb.index(self.nb.select())
        except Exception:
            return
        if tab == 1 and not self._hv_loaded and self.pe:
            self._hv_load()

    def _hv_load(self):
        self._hv_loaded = False
        data = bytes(self._hv_display)
        total_rows = (len(data) + 15) // 16
        self.hv_text.delete('1.0', 'end')
        self.hv_status_lbl.config(text="⏳ Yükleniyor…")
        self.update_idletasks()
        self._hv_rebuild_str_ranges()
        self._hv_load_batch(data, 0, total_rows, 2000)

    def _hv_load_batch(self, data, start_row, total_rows, batch):
        BPR     = HV_BPR
        end_row = min(start_row + batch, total_rows)
        lines   = []
        for row in range(start_row, end_row):
            fo    = row * BPR
            chunk = bytearray(BPR)
            avail = data[fo:fo + BPR]
            chunk[:len(avail)] = avail
            lines.append(hv_format_row(fo, chunk) + '\n')
        self.hv_text.insert('end', ''.join(lines))
        pct = int(end_row * 100 / total_rows)
        self.hv_status_lbl.config(text=f"⏳ {pct}%  ({end_row}/{total_rows})")
        self.update_idletasks()
        if end_row < total_rows:
            self.after(0, self._hv_load_batch, data, end_row, total_rows, batch)
        else:
            self._hv_loaded = True
            self.hv_status_lbl.config(
                text=f"✔ {len(data)//1024} KB · {total_rows} satır · {len(self.strings)} string")
            self.after(0, self._hv_retag_strings)
            # v22: mevcut yamaları renklendir
            self.after(100, self._hv_retag_patches)

    def _hv_rebuild_str_ranges(self):
        self._hv_str_map = {}
        for s in self.strings:
            for i in range(s['length'] + 1):
                self._hv_str_map[s['offset'] + i] = s

    def _hv_retag_strings(self):
        if not self._hv_loaded:
            return
        BPR = HV_BPR
        self.hv_text.tag_remove('hv_str', '1.0', 'end')
        str_lines = set()
        for s in self.strings:
            for r in range(s['offset'] // BPR, (s['offset'] + s['length']) // BPR + 1):
                str_lines.add(r)
        if not str_lines:
            return
        rows = sorted(str_lines)
        groups = []
        gs = pr = rows[0]
        for r in rows[1:]:
            if r == pr + 1:
                pr = r
            else:
                groups.append((gs, pr)); gs = pr = r
        groups.append((gs, pr))
        for rs, re in groups:
            self.hv_text.tag_add('hv_str', f"{rs+1}.0", f"{re+1}.end+1c")

    def _hv_retag_patches(self):
        """Tüm manuel yamaları turuncu renkle işaretle."""
        if not self._hv_loaded or not self._manual_patches:
            return
        BPR = HV_BPR
        self.hv_text.tag_remove('hv_patch', '1.0', 'end')
        for abs_off in self._manual_patches:
            row      = abs_off // BPR + 1
            byte_idx = abs_off % BPR
            col_s    = hv_byte_to_col(byte_idx)
            self.hv_text.tag_add('hv_patch', f"{row}.{col_s}", f"{row}.{col_s+2}")

    def _hv_update_rows(self, s):
        """_hv_display overlay'ini ve widget satırlarını günceller."""
        offset = s['offset']
        length = s['length']
        if length <= 0:
            return
        tr = s.get('translation', '')
        if tr:
            enc = bytearray(tr.encode('windows-1254', errors='replace'))
            if len(enc) < length:
                enc += bytearray(length - len(enc))
            enc = enc[:length]
        else:
            if self._orig_raw:
                enc = bytearray(self._orig_raw)[offset:offset + length]
            else:
                return
        self._hv_display[offset:offset + length] = enc

        if not self._hv_loaded:
            return

        BPR = HV_BPR
        row_start = offset // BPR
        row_end   = (offset + length - 1) // BPR
        for row_idx in range(row_start, row_end + 1):
            ln        = row_idx + 1
            fo        = row_idx * BPR
            row_bytes = bytearray(self._hv_display[fo:fo + BPR])
            new_line  = hv_format_row(fo, row_bytes)
            self.hv_text.delete(f"{ln}.0", f"{ln}.end")
            self.hv_text.insert(f"{ln}.0", new_line)
            # string tag'ini geri uygula
            self.hv_text.tag_add('hv_str', f"{ln}.0", f"{ln}.end+1c")
        # patch tag'lerini de geri uygula
        self._hv_retag_patches()

    # ── Hex arama ─────────────────────────────────────────────────────────
    def _hv_search(self, direction=1):
        q = self.hv_q_var.get().strip()
        if not q or not self._hv_loaded or not self.pe:
            return
        data = bytes(self._hv_display)
        if self.hv_mode.get() == 'hex':
            try:
                needle = bytes.fromhex(q.replace(' ', ''))
            except ValueError:
                self.hv_match_lbl.config(text="⚠ Geçersiz hex", fg=RED)
                return
        else:
            try:    needle = q.encode('windows-1254')
            except: needle = q.encode('utf-8', errors='replace')

        if q != self._hv_last_q:
            self._hv_match_idx = -1
            self._hv_last_q    = q

        matches = []
        idx = 0
        while True:
            pos = data.find(needle, idx)
            if pos == -1: break
            matches.append(pos); idx = pos + 1

        self._hv_matches = matches
        if not matches:
            self.hv_match_lbl.config(text="Bulunamadı", fg=RED)
            return

        self._hv_match_idx = (self._hv_match_idx + direction) % len(matches)
        self.hv_match_lbl.config(text=f"{self._hv_match_idx+1}/{len(matches)}", fg=ACCENT2)

        match_fo = matches[self._hv_match_idx]
        BPR      = HV_BPR
        ln_start = match_fo // BPR + 1
        ln_end   = (match_fo + len(needle) - 1) // BPR + 1
        self.hv_text.tag_remove('hv_mall', '1.0', 'end')
        self.hv_text.tag_remove('hv_mcur', '1.0', 'end')
        for mfo in matches[:200]:
            mln = mfo // BPR + 1
            self.hv_text.tag_add('hv_mall', f"{mln}.0", f"{mln}.end")
        self.hv_text.tag_add('hv_mcur', f"{ln_start}.0", f"{ln_end}.end+1c")
        self.hv_text.see(f"{ln_start}.0")

    # ── Hex tıklama / seçim ───────────────────────────────────────────────
    def _hv_col_to_byte(self, col):
        """Büyük hex viewer'da kolon → byte (sarmalayıcı)."""
        return hv_col_to_byte(col)

    def _hv_on_sel_change(self, event=None):
        try:
            fi = self.hv_text.index('sel.first')
            li = self.hv_text.index('sel.last')
        except tk.TclError:
            self.hv_sel_lbl.config(
                text="🖱  Tıkla → string yükle  |  Sürükle → Orijinale Gönder",
                fg="#3a5060")
            self.btn_hv_send.config(state='disabled')
            return
        fl, fc = int(fi.split('.')[0]), int(fi.split('.')[1])
        ll, lc = int(li.split('.')[0]), int(li.split('.')[1])
        start_fo = (fl - 1) * HV_BPR + hv_col_to_byte(fc)
        end_fo   = (ll - 1) * HV_BPR + hv_col_to_byte(lc) + 1
        if not self.pe or end_fo <= start_fo:
            self.btn_hv_send.config(state='disabled'); return
        # v22 BUG FIX: pe.data yerine _hv_display kullan
        raw = bytes(self._hv_display)[start_fo:end_fo]
        if b'\x00' in raw: raw = raw[:raw.index(b'\x00')]
        try:    preview = raw.decode('windows-1254', errors='replace')
        except: preview = raw.decode('latin-1',     errors='replace')
        clean = ''.join(c if c.isprintable() else '·' for c in preview)
        self.hv_sel_lbl.config(
            text=f"📌  0x{start_fo:08X}–0x{end_fo-1:08X}  {end_fo-start_fo}b  → \"{clean[:40]}\"",
            fg=ACCENT2)
        self.btn_hv_send.config(state='normal')

    def _hv_on_release(self, event):
        self.after(10, self._hv_check_sel)

    def _hv_check_sel(self):
        try:
            self.hv_text.index('sel.first')
            # Seçim var: sadece _hv_on_sel_change ile halledilir
        except tk.TclError:
            # Seçim yok: tek tıklama
            idx  = self.hv_text.index('insert')
            ln   = int(idx.split('.')[0])
            col  = int(idx.split('.')[1])
            # v22: byte editörüne de bildir
            fo   = (ln - 1) * HV_BPR
            byte_idx = hv_col_to_byte(col)
            abs_off  = fo + byte_idx
            if self.pe and 0 <= abs_off < len(self._hv_display):
                self._hv_select_byte(abs_off)
            self._hv_click_line(ln)
            self.btn_hv_send.config(state='disabled')

    def _hv_click_line(self, ln):
        fo = (ln - 1) * HV_BPR
        s  = None
        for off in range(fo, fo + HV_BPR):
            if off in self._hv_str_map:
                s = self._hv_str_map[off]; break
        if not s: return
        ss = s['offset'] // HV_BPR + 1
        se = (s['offset'] + s['length']) // HV_BPR + 1
        self.hv_text.tag_remove('hv_sel', '1.0', 'end')
        self.hv_text.tag_add('hv_sel', f"{ss}.0", f"{se}.end+1c")
        self.hv_sel_lbl.config(
            text=f"✔ String yüklendi: 0x{s['offset']:08X}  len={s['length']}", fg=GREEN)
        self.selected = s
        self._show_entry(s)
        try:
            self.tree.selection_set(str(s['offset']))
            self.tree.see(str(s['offset']))
        except Exception:
            pass

    def _hv_send_selection(self):
        if not self.pe: return
        try:
            fi = self.hv_text.index('sel.first')
            li = self.hv_text.index('sel.last')
        except tk.TclError:
            return
        fl, fc = int(fi.split('.')[0]), int(fi.split('.')[1])
        ll, lc = int(li.split('.')[0]), int(li.split('.')[1])
        start_fo = (fl - 1) * HV_BPR + hv_col_to_byte(fc)
        end_fo   = (ll - 1) * HV_BPR + hv_col_to_byte(lc) + 1
        # v22 BUG FIX: _hv_display kullan (çeviriler görünsün)
        raw = bytes(self._hv_display)[start_fo:end_fo]
        if b'\x00' in raw: raw = raw[:raw.index(b'\x00')]
        try:    decoded = raw.decode('windows-1254', errors='replace')
        except: decoded = raw.decode('latin-1',     errors='replace')
        fake = {'offset': start_fo, 'length': end_fo - start_fo,
                'text': decoded, 'translation': '', 'relocated': False, '_custom': True}
        self.selected = fake
        self._show_entry(fake)
        self.hv_sel_lbl.config(
            text=f"✔ Gönderildi 0x{start_fo:08X} ({end_fo-start_fo}b) → \"{decoded[:40]}\"",
            fg=GREEN)
        self.btn_hv_send.config(state='disabled')

    # ══════════════════════════════════════════════════════════════════════
    #  EXE ÇALIŞIYOR MU?
    # ══════════════════════════════════════════════════════════════════════
    def _is_exe_running(self, exe_path):
        try:
            with open(exe_path, 'r+b'):
                return False
        except (PermissionError, IOError):
            return True
        except Exception:
            return False

    # ══════════════════════════════════════════════════════════════════════
    #  EXE KAYDET  (v22: _manual_patches eklendi)
    # ══════════════════════════════════════════════════════════════════════
    def save_exe(self):
        if not self.pe or not self._orig_raw:
            messagebox.showwarning(self.T("warn_lbl"), self.T("err_load"))
            return
        if self.exe_path and self._is_exe_running(self.exe_path):
            messagebox.showwarning(
                self.T("exe_running"),
                self.T("exe_run_msg", name=os.path.basename(self.exe_path)))
            return

        to_reloc = [s for s in self.strings if s['translation'] and s.get('relocated')]
        normal   = [s for s in self.strings if s['translation'] and not s.get('relocated')]
        self._log(f"Kayıt başladı — normal:{len(normal)}  reloc:{len(to_reloc)}  hexPatch:{len(self._manual_patches)}")

        work_pe = PEInfo(bytes(self._orig_raw))
        patched = work_pe.data

        # v22: İlk olarak ham hex yamalarını uygula
        hex_patched = 0
        for off, val in self._manual_patches.items():
            if 0 <= off < len(patched):
                patched[off] = val
                hex_patched += 1
        if hex_patched:
            self._log(f"  HEX PATCH: {hex_patched} byte uygulandı")

        if to_reloc:
            needed   = sum(len(s['translation'].encode('windows-1254', 'replace')) + 1
                          for s in to_reloc)
            sec_size = max(align_up(needed + 0x200, 0x1000), 0x2000)
            raw_off = base_va = 0
            try:
                raw_off, base_va = work_pe.add_section(size=sec_size)
                self._log(f".xtra section: raw=0x{raw_off:X}  va=0x{base_va:X}")
            except RuntimeError:
                self._log("add_section başarısız, code cave deneniyor...", "WARN")
                try:
                    excl = [(s['offset'], s['offset'] + s['length'] + 1) for s in self.strings]
                    raw_off, base_va = work_pe.find_code_cave(needed, excl)
                    self._log(f"Code cave: raw=0x{raw_off:X}  va=0x{base_va:X}")
                except RuntimeError as e2:
                    self._log(str(e2), "ERR")
                    messagebox.showerror("Relocation Hatası", str(e2))
                    return
        else:
            raw_off = base_va = 0

        suffix = self.T("save_suffix")
        path = filedialog.asksaveasfilename(
            title=self.T("save_title"),
            initialfile=os.path.basename(self.exe_path).replace('.exe', suffix),
            defaultextension=".exe", filetypes=[("EXE", "*.exe")])
        if not path:
            return

        applied = relocated = errors = 0
        cur_ptr = raw_off

        for s in normal:
            try:
                enc    = s['translation'].encode('windows-1254')
                padded = enc + b'\x00' * (s['length'] - len(enc))
                patched[s['offset']:s['offset'] + s['length']] = padded
                self._log(f"  PATCH 0x{s['offset']:08X} [{s['length']}b] {repr(s['translation'][:28])}")
                applied += 1
            except Exception as e:
                self._log(f"  HATA 0x{s['offset']:08X}: {e}", "ERR")
                errors += 1

        for s in to_reloc:
            try:
                enc          = s['translation'].encode('windows-1254') + b'\x00'
                new_file_off = cur_ptr
                patched[new_file_off:new_file_off + len(enc)] = enc
                cur_ptr     += len(enc)
                new_va       = base_va + (new_file_off - raw_off)
                old_va       = work_pe.file_to_va(s['offset'])
                ptr_count    = 0
                if old_va:
                    old_b = struct.pack('<I', old_va)
                    new_b = struct.pack('<I', new_va)
                    idx   = 0
                    while True:
                        pos = patched.find(old_b, idx)
                        if pos == -1: break
                        patched[pos:pos + 4] = new_b; idx = pos + 1; ptr_count += 1
                self._log(f"  RELOC 0x{s['offset']:08X}→0x{new_file_off:08X}  ptrs={ptr_count}")
                s['new_offset'] = new_file_off
                relocated += 1
            except Exception as e:
                self._log(f"  HATA RELOC 0x{s['offset']:08X}: {e}", "ERR")
                errors += 1

        try:
            with open(path, 'wb') as f:
                f.write(patched)
            self._log(f"Yazıldı: {path}  ({len(patched):,} byte)")
        except Exception as e:
            self._log(str(e), "ERR")
            messagebox.showerror("Kayıt Hatası", str(e))
            return

        self._auto_backup_exe(path)
        self._auto_backup_json(f"EXE kayıt (normal:{applied} reloc:{relocated} hex:{hex_patched})")
        self._flush_log()
        self.unsaved = False

        # ── Detay listesi: ne değişti ──
        detail_lines = []
        for s in normal:
            orig_preview = s['text'][:24].replace('\n','↵')
            tr_preview   = s['translation'][:24].replace('\n','↵')
            detail_lines.append("  0x{:08X}  '{}'  →  '{}'".format(s["offset"], orig_preview, tr_preview))
        for s in to_reloc:
            orig_preview = s['text'][:24].replace('\n','↵')
            tr_preview   = s['translation'][:24].replace('\n','↵')
            detail_lines.append("⚡ 0x{:08X}  '{}'  →  '{}'".format(s["offset"], orig_preview, tr_preview))
        # Manuel hex yamaları (gruplara ayır: ardışık ofsetleri tek satırda göster)
        if self._manual_patches:
            offs = sorted(self._manual_patches.keys())
            groups, gs, pr = [], offs[0], offs[0]
            for o in offs[1:]:
                if o == pr + 1:
                    pr = o
                else:
                    groups.append((gs, pr)); gs = pr = o
            groups.append((gs, pr))
            for gstart, gend in groups[:20]:
                n = gend - gstart + 1
                vals = ' '.join(f'{self._manual_patches[gstart+i]:02X}' for i in range(min(n,8)))
                detail_lines.append(f"  HEX 0x{gstart:08X}+{n}b  [{vals}{'…' if n>8 else ''}]")
            if len(groups) > 20:
                detail_lines.append(f"  … +{len(groups)-20} blok daha")
        detail = '\n'.join(detail_lines) if detail_lines else '  (değişiklik yok)'

        # Eğer hiç değişiklik yoksa uyar
        if applied == 0 and relocated == 0 and hex_patched == 0:
            detail = '⚠ HİÇBİR ŞEY YAZILMADI!\n\n  Olası sebepler:\n  • Hex seçiminden gönderilen metin "Ctrl+Enter" ile kaydedildi mi?\n  • Normal string listesindeki bir entry mi seçiliydi?'

        self._show_save_result(self.T("save_ok_title"),
            self.T("save_ok_msg", a=applied, r=relocated, h=hex_patched, e=errors, path=path, detail=detail))
        self.status_var.set(self.T("saved_status", f=os.path.basename(path)))


    # ══════════════════════════════════════════════════════════════════════
    #  KAYIT SONUÇ PENCERESİ
    # ══════════════════════════════════════════════════════════════════════
    def _show_save_result(self, title, msg):
        win = tk.Toplevel(self, bg="#060d06")
        win.title(title)
        win.geometry("700x500")
        win.grab_set()
        tk.Frame(win, bg=GREEN, height=3).pack(fill="x")
        hdr = tk.Frame(win, bg="#08140a")
        hdr.pack(fill="x")
        tk.Label(hdr, text="💾  KAYIT SONUCU", font=("Courier New", 11, "bold"),
                 bg="#08140a", fg=GREEN).pack(side="left", padx=14, pady=8)
        parts = msg.split("\n\n", 2)
        summary  = parts[0] if parts else msg
        path_line= parts[1] if len(parts) > 1 else ""
        detail   = parts[2] if len(parts) > 2 else ""
        tk.Label(win, text=summary, font=("Courier New", 10, "bold"),
                 bg="#060d06", fg=GREEN, justify="left", padx=14, pady=6).pack(fill="x")
        if path_line:
            tk.Label(win, text=path_line, font=("Courier New", 8),
                     bg="#060d06", fg=ACCENT2, justify="left", padx=14).pack(fill="x")
        tk.Frame(win, bg="#1a3a1a", height=1).pack(fill="x", padx=10, pady=4)
        tk.Label(win, text="— Değişiklik Detayları —",
                 font=("Courier New", 8, "bold"), bg="#060d06", fg=FG2).pack()
        tf = tk.Frame(win, bg="#060d06")
        tf.pack(fill="both", expand=True, padx=10, pady=4)
        det_txt = tk.Text(tf, bg="#040a04", fg="#50c070", font=("Courier New", 9),
                          wrap="none", relief="flat")
        det_txt.tag_configure("hex",   foreground="#ff8800")
        det_txt.tag_configure("reloc", foreground=YELLOW)
        det_txt.tag_configure("warn",  foreground=RED, font=("Courier New", 9, "bold"))
        det_txt.tag_configure("ok",    foreground="#50c070")
        vsb = tk.Scrollbar(tf, orient="vertical",   command=det_txt.yview, bg="#08140a", width=10)
        hsb = tk.Scrollbar(tf, orient="horizontal", command=det_txt.xview, bg="#08140a", width=8)
        det_txt.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        det_txt.pack(fill="both", expand=True)
        for line in (detail or "(detay yok)").splitlines():
            if line.startswith("⚡"):
                det_txt.insert("end", line + "\n", "reloc")
            elif "HEX" in line and "0x" in line:
                det_txt.insert("end", line + "\n", "hex")
            elif "⚠" in line or "YAZILMADI" in line:
                det_txt.insert("end", line + "\n", "warn")
            else:
                det_txt.insert("end", line + "\n", "ok")
        det_txt.config(state="disabled")
        bot = tk.Frame(win, bg="#08140a", pady=6)
        bot.pack(fill="x")
        tk.Frame(win, bg="#1a3a1a", height=1).pack(fill="x")
        tk.Button(bot, text="✔  Tamam", command=win.destroy,
                  bg=GREEN, fg="#000", font=("Courier New", 10, "bold"),
                  relief="flat", cursor="hand2", width=12, pady=5,
                  activebackground=ACCENT, activeforeground="#000").pack(pady=4)
        tk.Frame(win, bg=GREEN, height=3).pack(fill="x", side="bottom")

    # ══════════════════════════════════════════════════════════════════════
    #  JSON
    # ══════════════════════════════════════════════════════════════════════
    def export_json(self):
        if not self.strings:
            messagebox.showwarning(self.T("warn_lbl"), self.T("err_load")); return
        path = filedialog.asksaveasfilename(defaultextension=".json",
                                             filetypes=[("JSON", "*.json")])
        if not path: return
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.strings, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("OK", self.T("json_saved", n=len(self.strings)))

    def import_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not path: return
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        lut     = {s['offset']: s for s in self.strings}
        updated = 0
        for item in data:
            if item['offset'] in lut and item.get('translation'):
                lut[item['offset']]['translation'] = item['translation']
                lut[item['offset']]['relocated']   = item.get('relocated', False)
                updated += 1
        if self._orig_raw:
            for s in self.strings:
                if s.get('translation'):
                    self._hv_update_rows(s)
        self._apply_filter(); self._update_stats()
        messagebox.showinfo("OK", self.T("json_loaded", n=updated))

    # ══════════════════════════════════════════════════════════════════════
    #  PE ANALİZÖR
    # ══════════════════════════════════════════════════════════════════════
    def open_pe_analyzer(self):
        win = tk.Toplevel(self, bg="#08090f")
        win.title("🧬 PE Analizör")
        win.geometry("960x700")
        tk.Frame(win, bg="#5ba8ff", height=3).pack(fill='x')
        top = tk.Frame(win, bg="#0d1420", pady=6)
        top.pack(fill='x')
        tk.Label(top, text="🧬  PE ANALİZÖR", font=("Courier New", 12, "bold"),
                 bg="#0d1420", fg="#5ba8ff").pack(side='left', padx=14)
        path_var = tk.StringVar(value="— EXE seçilmedi —")
        tk.Label(top, textvariable=path_var, font=("Courier New", 9),
                 bg="#0d1420", fg="#4a6080").pack(side='left', padx=8)
        btn_frame = tk.Frame(top, bg="#0d1420")
        btn_frame.pack(side='right', padx=10)

        body = tk.Frame(win, bg="#08090f")
        body.pack(fill='both', expand=True, padx=6, pady=4)
        left  = tk.Frame(body, bg="#08090f")
        left.pack(side='left', fill='both', expand=True)
        right = tk.Frame(body, bg="#0d1420", width=230)
        right.pack(side='right', fill='y', padx=(4, 0))
        right.pack_propagate(False)
        tk.Label(right, text="📊 ÖZET", font=("Courier New", 9, "bold"),
                 bg="#0d1420", fg="#5ba8ff").pack(pady=(10, 4))
        tk.Frame(right, bg="#1a2a40", height=1).pack(fill='x', padx=8)
        summ_txt = tk.Text(right, bg="#0d1420", fg=FG, font=("Courier New", 9),
                            wrap='word', relief='flat', state='disabled', width=28)
        summ_txt.pack(fill='both', expand=True, padx=6, pady=4)
        for tag, col in [('ok', GREEN), ('err', RED), ('warn', YELLOW), ('head', "#5ba8ff")]:
            summ_txt.tag_configure(tag, foreground=col)

        rf  = tk.Frame(left, bg="#08090f")
        rf.pack(fill='both', expand=True)
        txt = tk.Text(rf, bg="#070810", fg="#4a8060", font=("Courier New", 9),
                      wrap='none', relief='flat')
        for tag, col, bold in [
            ('ERR',  RED,       True), ('WARN', YELLOW, False), ('OK', GREEN, False),
            ('HEAD', "#5ba8ff", True), ('VAL',  "#60c8a0", False), ('DIM', "#2a4050", False),
        ]:
            txt.tag_configure(tag, foreground=col,
                              font=("Courier New", 9, "bold") if bold else ("Courier New", 9))
        vsb = tk.Scrollbar(rf, orient='vertical',   command=txt.yview, bg="#0d1420", troughcolor="#08090f", width=10)
        hsb = tk.Scrollbar(rf, orient='horizontal', command=txt.xview, bg="#0d1420", troughcolor="#08090f", width=10)
        txt.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side='right',  fill='y')
        hsb.pack(side='bottom', fill='x')
        txt.pack(fill='both', expand=True)

        bot = tk.Frame(win, bg="#0d1420", pady=6)
        bot.pack(fill='x')
        tk.Frame(win, bg="#1a2a40", height=1).pack(fill='x')
        status_lbl = tk.Label(bot, text="EXE yükleyin", font=("Courier New", 9), bg="#0d1420", fg="#2a4060")
        status_lbl.pack(side='left', padx=14)

        def save_report():
            p = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text","*.txt")], title="Raporu Kaydet", parent=win)
            if p:
                with open(p,'w',encoding='utf-8') as f: f.write(txt.get('1.0','end'))

        def auto_fix():
            cur_path = path_var.get()
            if cur_path.startswith("—"):
                messagebox.showwarning("Düzelt","Önce bir EXE yükleyin!", parent=win); return
            try:
                with open(cur_path,'rb') as f: raw = f.read()
            except Exception:
                if not self._orig_raw:
                    messagebox.showwarning("Düzelt","EXE dosyası okunamadı!", parent=win); return
                raw = bytes(self._orig_raw); cur_path = self.exe_path or cur_path

            pe_fix = PEInfo(bytes(raw)); data = pe_fix.data; fixes = []; errors = []
            try:
                sec_tab=pe_fix.sec_table; hdr_end=sec_tab+pe_fix.num_sections*40
                first_raw=min(s['rawoff'] for s in pe_fix.sections if s['rawoff']>0)
                padding=first_raw-hdr_end; file_align=pe_fix.file_align or 512
                if padding<40:
                    want_free=128; new_first=align_up(hdr_end+want_free,file_align)
                    shift=align_up(new_first-first_raw,file_align); new_first=first_raw+shift
                    old_size=len(data); new_data=bytearray(old_size+shift)
                    new_data[:first_raw]=data[:first_raw]
                    for sec in pe_fix.sections:
                        ro=sec['rawoff']; rsz=sec['rawsize']
                        if ro==0 or rsz==0: continue
                        new_data[ro+shift:ro+shift+rsz]=data[ro:ro+rsz]
                        struct.pack_into('<I',new_data,sec['hdr_off']+20,ro+shift)
                    last_s=max(pe_fix.sections,key=lambda s:s['rawoff'])
                    tail_off=last_s['rawoff']+last_s['rawsize']
                    if tail_off<old_size:
                        tail=data[tail_off:]; new_data[tail_off+shift:tail_off+shift+len(tail)]=tail
                    opt_off=pe_fix.pe_off+24; struct.pack_into('<I',new_data,opt_off+60,new_first)
                    data=new_data; fixes.append(f"✔ Header padding düzeltildi: {padding}b → {new_first-hdr_end}b (+0x{shift:X})")
            except Exception as e: errors.append(f"Header padding: {e}")
            try:
                opt_off=pe_fix.pe_off+24; struct.pack_into('<I',data,opt_off+64,0); fixes.append("✔ PE Checksum sıfırlandı")
            except Exception as e: errors.append(f"Checksum: {e}")
            try:
                opt_off=pe_fix.pe_off+24; magic=struct.unpack_from('<H',data,opt_off)[0]
                bid_off=opt_off+(184 if magic==0x10b else 200)
                if bid_off+8<=len(data):
                    bid_rva=struct.unpack_from('<I',data,bid_off)[0]
                    if bid_rva:
                        struct.pack_into('<I',data,bid_off,0); struct.pack_into('<I',data,bid_off+4,0)
                        fixes.append("✔ Bound Import temizlendi")
            except Exception as e: errors.append(f"BoundImport: {e}")
            try:
                fixed_secs=0
                for sec in pe_fix.sections:
                    so=sec['hdr_off']; flags=struct.unpack_from('<I',data,so+36)[0]
                    if not(flags&0x80000000):
                        struct.pack_into('<I',data,so+36,flags|0xC0000040); fixed_secs+=1
                if fixed_secs: fixes.append(f"✔ {fixed_secs} section yazılabilir yapıldı")
            except Exception as e: errors.append(f"Section flags: {e}")
            try:
                last_sec=pe_fix.sections[-1]
                min_image=align_up(last_sec['vaddr']+max(last_sec['vsize'],last_sec['rawsize']),pe_fix.sec_align)
                opt_off=pe_fix.pe_off+24; cur_size=struct.unpack_from('<I',data,opt_off+56)[0]
                if cur_size<min_image:
                    struct.pack_into('<I',data,opt_off+56,min_image)
                    fixes.append(f"✔ SizeOfImage düzeltildi: 0x{cur_size:X} → 0x{min_image:X}")
            except Exception as e: errors.append(f"SizeOfImage: {e}")

            if not fixes and not errors:
                messagebox.showinfo("Düzelt","Düzeltilecek bir şey bulunamadı.", parent=win); return
            summary="\n".join(fixes+[f"\u26a0 {e}" for e in errors])
            if not messagebox.askyesno("Düzelt & Kaydet",f"Yapılacak düzeltmeler:\n\n{summary}\n\nKaydet?",parent=win): return
            p=filedialog.asksaveasfilename(title="Düzeltilmiş EXE Kaydet",
                initialfile=os.path.basename(cur_path).replace('.exe','_FIXED.exe'),
                defaultextension=".exe",filetypes=[("EXE","*.exe")],parent=win)
            if not p: return
            with open(p,'wb') as f: f.write(bytes(data))
            self._log(f"PE Düzelt: {p}  fixes={len(fixes)}")
            messagebox.showinfo("✔ Kaydedildi",f"Düzeltilmiş EXE kaydedildi:\n{p}\n\n{summary}",parent=win)
            status_lbl.config(text="Yeniden analiz ediliyor…",fg=YELLOW)
            win.after(100,lambda: analyze(bytes(data),p))

        tk.Button(bot,text="🔧 Düzelt & Kaydet",command=auto_fix,bg="#1a2a10",fg=GREEN,
                  font=("Courier New",9,"bold"),relief='flat',cursor='hand2',padx=10,pady=3,
                  activebackground=GREEN,activeforeground='black').pack(side='right',padx=4)
        tk.Button(bot,text="💾 Raporu Kaydet",command=save_report,bg=BG3,fg=ACCENT2,
                  font=("Courier New",9,"bold"),relief='flat',cursor='hand2',padx=10,pady=3).pack(side='right',padx=6)

        compare_data=[None]

        def analyze(data,label):
            txt.config(state='normal'); txt.delete('1.0','end')
            summ_txt.config(state='normal'); summ_txt.delete('1.0','end')
            errs=warns=oks=0
            def w(line,tag=''): txt.insert('end',line+'\n',tag)
            def s(line,tag=''): summ_txt.insert('end',line+'\n',tag)
            def chk(cond,ok_msg,err_msg):
                nonlocal errs,oks
                if cond: w(f"  ✔  {ok_msg}",'OK'); oks+=1
                else:    w(f"  ✘  {err_msg}",'ERR'); errs+=1
                return cond
            def wrn(cond,ok_msg,warn_msg):
                nonlocal warns,oks
                if cond: w(f"  ✔  {ok_msg}",'OK'); oks+=1
                else:    w(f"  ⚠  {warn_msg}",'WARN'); warns+=1
                return cond
            w("═══ 1. DOS / MZ BAŞLIĞI ═══════════════════════════════════════",'HEAD')
            if len(data)<64: w("  ✘  Dosya çok küçük!",'ERR'); return
            chk(data[0:2]==b'MZ',"MZ imzası: 4D 5A ✔","MZ imzası YOK!")
            pe_off=struct.unpack_from('<I',data,0x3c)[0]
            w(f"  ℹ  PE header ofseti: 0x{pe_off:08X}",'VAL')
            if not chk(pe_off<len(data)-4,"PE ofseti dosya içinde",f"PE ofseti dosya dışında! 0x{pe_off:X}"): return
            w("\n═══ 2. PE BAŞLIĞI ══════════════════════════════════════════════",'HEAD')
            if not chk(data[pe_off:pe_off+4]==b'PE\x00\x00',f"PE imzası ✔ @ 0x{pe_off:08X}",f"PE imzası YOK: {data[pe_off:pe_off+4].hex()}"): return
            machine=struct.unpack_from('<H',data,pe_off+4)[0]; num_sec=struct.unpack_from('<H',data,pe_off+6)[0]
            opt_size=struct.unpack_from('<H',data,pe_off+20)[0]; chars=struct.unpack_from('<H',data,pe_off+22)[0]
            mn={0x14c:'x86',0x8664:'x64',0x1c0:'ARM'}.get(machine,'?')
            w(f"  ℹ  Machine: 0x{machine:04X} ({mn})  Sections: {num_sec}  Chars: 0x{chars:04X}",'VAL')
            chk(machine in(0x14c,0x8664,0x1c0),f"Machine: {mn}",f"Machine bilinmiyor: 0x{machine:04X}")
            chk(0<num_sec<=96,f"Section sayısı: {num_sec}",f"Section sayısı anormal: {num_sec}")
            wrn(bool(chars&0x0002),"Executable bit set","Executable bit eksik!")
            wrn(not(chars&0x2000),"DLL değil","DLL bayrağı var!")
            w("\n═══ 3. OPTİONAL BAŞLIK ═════════════════════════════════════════",'HEAD')
            opt_off=pe_off+24; magic=struct.unpack_from('<H',data,opt_off)[0]; is32=magic==0x10b
            chk(magic in(0x10b,0x20b),f"Magic: 0x{magic:04X} ({'PE32' if is32 else 'PE32+'})",f"Magic bilinmiyor: 0x{magic:04X}")
            entry_rva=struct.unpack_from('<I',data,opt_off+16)[0]
            image_base=struct.unpack_from('<I',data,opt_off+(28 if is32 else 24))[0]
            sec_align=struct.unpack_from('<I',data,opt_off+32)[0]; file_align=struct.unpack_from('<I',data,opt_off+36)[0]
            image_size=struct.unpack_from('<I',data,opt_off+56)[0]; hdr_size=struct.unpack_from('<I',data,opt_off+60)[0]
            subsystem=struct.unpack_from('<H',data,opt_off+68)[0]
            w(f"  ℹ  EntryPoint: 0x{entry_rva:08X}  ImageBase: 0x{image_base:08X}",'VAL')
            w(f"  ℹ  SecAlign: 0x{sec_align:X}  FileAlign: 0x{file_align:X}  SizeOfImage: 0x{image_size:X}",'VAL')
            w(f"  ℹ  Subsystem: {subsystem} ({'GUI' if subsystem==2 else 'CUI' if subsystem==3 else '?'})",'VAL')
            chk(file_align>=512 and file_align>0 and not(file_align&(file_align-1)),f"FileAlign: 0x{file_align:X}",f"FileAlign geçersiz: 0x{file_align:X}")
            chk(sec_align>0 and not(sec_align&(sec_align-1)),f"SecAlign: 0x{sec_align:X}",f"SecAlign geçersiz: 0x{sec_align:X}")
            w("\n═══ 4. SECTION TABLOSU ═════════════════════════════════════════",'HEAD')
            sec_tab=pe_off+24+opt_size
            chk(sec_tab+num_sec*40<=len(data),"Section tablosu dosya içinde","Section tablosu taşıyor!")
            first_raw=min((struct.unpack_from('<I',data,sec_tab+i*40+20)[0] for i in range(num_sec) if struct.unpack_from('<I',data,sec_tab+i*40+20)[0]>0),default=hdr_size)
            hdr_end=sec_tab+num_sec*40; padding=first_raw-hdr_end
            w(f"  ℹ  Header padding: {padding} byte",'VAL')
            if padding>=40: w(f"  ✔  Yeni section eklenebilir ({padding}b boş)",'OK'); oks+=1
            else: w(f"  ⚠  YER YOK — relocation çalışmaz! ({padding}b < 40b)",'WARN'); warns+=1
            w(f"\n  {'Ad':<10} {'VAddr':>10} {'VSize':>8} {'RawOff':>10} {'RawSize':>8}  Flags")
            prev_end=0
            for i in range(num_sec):
                so=sec_tab+i*40; name=data[so:so+8].rstrip(b'\x00').decode('ascii','replace')
                vsize=struct.unpack_from('<I',data,so+8)[0]; vaddr=struct.unpack_from('<I',data,so+12)[0]
                rawsize=struct.unpack_from('<I',data,so+16)[0]; rawoff=struct.unpack_from('<I',data,so+20)[0]
                flags=struct.unpack_from('<I',data,so+36)[0]
                fs=('R' if flags&0x40000000 else '.')+('W' if flags&0x80000000 else '.')+('X' if flags&0x20000000 else '.')
                w(f"  {name:<10} {vaddr:>10X} {vsize:>8X} {rawoff:>10X} {rawsize:>8X}  {fs}",'VAL')
                if rawoff>0 and rawoff+rawsize>len(data): w("       ✘ Section dosya sınırını aşıyor!",'ERR'); errs+=1
                if rawoff>0 and file_align>0 and rawoff%file_align!=0: w(f"       ⚠ RawOffset alignment uyumsuz",'WARN'); warns+=1
                if rawoff>0:
                    if rawoff<prev_end: w("       ✘ Çakışma: önceki section ile!",'ERR'); errs+=1
                    prev_end=rawoff+rawsize
            w("\n═══ 5. ENTRY POINT ═════════════════════════════════════════════",'HEAD')
            ep_file=ep_sec=None
            for i in range(num_sec):
                so=sec_tab+i*40; va=struct.unpack_from('<I',data,so+12)[0]; vsz=struct.unpack_from('<I',data,so+8)[0]
                ro=struct.unpack_from('<I',data,so+20)[0]; rsz=struct.unpack_from('<I',data,so+16)[0]
                if va<=entry_rva<va+max(vsz,rsz):
                    ep_file=ro+(entry_rva-va); ep_sec=data[so:so+8].rstrip(b'\x00').decode('ascii','replace'); break
            if ep_file is not None:
                chk(ep_file<len(data),f"EntryPoint dosya içinde: 0x{ep_file:08X} ({ep_sec})",f"EntryPoint dosya dışında: 0x{ep_file:08X}")
                if ep_file<len(data): w(f"  ℹ  İlk baytlar: {data[ep_file:ep_file+8].hex(' ')}",'VAL')
            else: w(f"  ⚠  EntryPoint 0x{entry_rva:08X} hiçbir section'a gitmiyor",'WARN'); warns+=1

            if compare_data[0] and compare_data[0]!=bytes(data):
                w("\n═══ 7. KARŞILAŞTIRMA ═══════════════════════════════════════════",'HEAD')
                b2=compare_data[0]; ml=min(len(data),len(b2))
                difs=[i for i in range(ml) if data[i]!=b2[i]]
                w(f"  ℹ  {len(data):,}b  vs  {len(b2):,}b  |  {len(difs)} byte farklı  |  boyut farkı: {len(b2)-len(data):+,}",'VAL')
                if difs:
                    blocks,gs,pr=[],difs[0],difs[0]
                    for d in difs[1:]:
                        if d>pr+1: blocks.append((gs,pr)); gs=d
                        pr=d
                    blocks.append((gs,pr))
                    for bs,be in blocks[:50]:
                        try: os_=data[bs:be+1].decode('windows-1254','replace'); ns_=b2[bs:be+1].decode('windows-1254','replace'); txt_p=f"  '{os_}' → '{ns_}'"
                        except: txt_p=""
                        w(f"  @ 0x{bs:08X}–0x{be:08X}  ({be-bs+1}b){txt_p}",'VAL')
                    if len(blocks)>50: w(f"  … +{len(blocks)-50} blok daha",'DIM')

            w("\n═══ SONUÇ ══════════════════════════════════════════════════════",'HEAD')
            w(f"  Kontroller: {oks+warns+errs}   ✔ {oks}  ⚠ {warns}  ✘ {errs}")
            if errs==0 and warns==0: w("  ✔  EXE geçerli — başlatılabilir.",'OK')
            elif errs>0: w(f"  ✘  {errs} KRİTİK HATA — EXE muhtemelen açılmıyor!",'ERR')
            else: w(f"  ⚠  Kritik hata yok, {warns} uyarı var.",'WARN')
            txt.config(state='disabled')
            s("Kontroller\n",'head'); s(f"  ✔ OK:     {oks}",'ok'); s(f"  ⚠ Uyarı: {warns}",'warn'); s(f"  ✘ Hata:  {errs}",'err')
            s(f"\nDosya\n",'head'); s(f"  {len(data)//1024} KB",'ok'); s(f"  {'PE32' if is32 else 'PE32+'}",'ok'); s(f"  Sec: {num_sec}",'ok'); s(f"  EP: 0x{entry_rva:08X}",'ok')
            s(f"\nHdr padding\n",'head'); s(f"  {padding}b",'ok' if padding>=40 else 'warn')
            s(f"\n── SONUÇ ──\n  {'✔ GEÇERLİ' if errs==0 else '✘ BOZUK!'}\n",'ok' if errs==0 else 'err')
            summ_txt.config(state='disabled')
            status_lbl.config(text=f"✔ {oks} OK  ⚠ {warns} uyarı  ✘ {errs} hata",fg=RED if errs else(YELLOW if warns else GREEN))

        def load_file():
            p=filedialog.askopenfilename(title="EXE Analiz Et",filetypes=[("EXE","*.exe"),("All","*.*")],parent=win)
            if not p: return
            with open(p,'rb') as f: raw=f.read()
            path_var.set(p); status_lbl.config(text="Analiz ediliyor…",fg=YELLOW)
            win.after(50,lambda: analyze(raw,p))

        def load_current():
            if not self._orig_raw:
                messagebox.showwarning("PE Analiz","Önce PM2'ye EXE yükleyin!",parent=win); return
            path_var.set(self.exe_path or "PM2 Orijinal")
            win.after(50,lambda: analyze(bytes(self._orig_raw),"orijinal"))

        def load_compare():
            p=filedialog.askopenfilename(title="Karşılaştırılacak EXE",filetypes=[("EXE","*.exe"),("All","*.*")],parent=win)
            if not p: return
            with open(p,'rb') as f: compare_data[0]=f.read()
            btn_cmp.config(text=f"⇄ {os.path.basename(p)}",fg=GREEN)

        def mkpb(t,cmd,col,fg_='white'):
            b=tk.Button(btn_frame,text=t,command=cmd,bg=col,fg=fg_,font=("Courier New",9,"bold"),relief='flat',cursor='hand2',padx=10,pady=4,activebackground=BG3)
            b.pack(side='left',padx=3); return b

        mkpb("📂 EXE Yükle",load_file,"#1a2a40")
        mkpb("🎯 Mevcut EXE",load_current,"#0d2a1a",GREEN)
        btn_cmp=mkpb("⇄ Karşılaştır",load_compare,"#2a1a0a",YELLOW)

    # ══════════════════════════════════════════════════════════════════════
    #  HEX DIFF
    # ══════════════════════════════════════════════════════════════════════
    def open_hex_diff(self):
        import threading
        win = tk.Toplevel(self, bg="#08060f")
        win.title("EXE Hex Fark")
        win.geometry("1140x720")
        tk.Frame(win, bg="#c080ff", height=3).pack(fill='x')
        top = tk.Frame(win, bg="#0e0a18", pady=6)
        top.pack(fill='x')
        tk.Label(top, text="⇄  HEX DIFF", font=("Courier New",11,"bold"), bg="#0e0a18", fg="#c080ff").pack(side='left', padx=12)
        raw_data=[None,None]
        name_lbls=[tk.Label(top,text="EXE 1: --",font=("Courier New",8),bg="#0e0a18",fg="#5a3a80"),
                   tk.Label(top,text="EXE 2: --",font=("Courier New",8),bg="#0e0a18",fg="#3a5a80")]
        name_lbls[0].pack(side='left',padx=6); name_lbls[1].pack(side='left',padx=6)
        stat_lbl=tk.Label(top,text="",font=("Courier New",9,"bold"),bg="#0e0a18",fg="#c080ff")
        stat_lbl.pack(side='right',padx=14)
        fbar=tk.Frame(win,bg="#0a0814",pady=4); fbar.pack(fill='x')
        ctx_var=tk.IntVar(value=3)
        tk.Label(fbar,text="Bağlam satırı:",font=("Courier New",9),bg="#0a0814",fg="#5a4a70").pack(side='left',padx=10)
        tk.Spinbox(fbar,from_=0,to=16,textvariable=ctx_var,width=3,bg="#1a1030",fg=FG,font=("Courier New",9),relief='flat',buttonbackground="#2a1a40",
                   command=lambda: start_diff() if all(raw_data) else None).pack(side='left',padx=2)
        diff_stat=tk.Label(fbar,text="İki EXE yükle → fark gösterilir",font=("Courier New",9),bg="#0a0814",fg="#4a3a60")
        diff_stat.pack(side='right',padx=14)
        prog_frame=tk.Frame(win,bg="#0a0814"); prog_frame.pack(fill='x')
        prog_bar=tk.Canvas(prog_frame,height=4,bg="#0a0814",highlightthickness=0); prog_bar.pack(fill='x')
        prog_lbl=tk.Label(prog_frame,text="",font=("Courier New",8),bg="#0a0814",fg="#6a4a90"); prog_lbl.pack(fill='x')
        def update_progress(pct,msg=""):
            w=prog_bar.winfo_width(); prog_bar.delete('all')
            prog_bar.create_rectangle(0,0,int(w*pct/100),4,fill="#c080ff",outline=""); prog_lbl.config(text=msg)
        tk.Label(win,text="  Offset      ───────────── EXE 1 (Sol) ──────────────────────────────  ASCII     | ───────────── EXE 2 (Sağ) ──────────────────────────────  ASCII",
                 font=("Courier New",8),bg="#0c0a10",fg="#2a1a40",anchor='w',padx=4).pack(fill='x')
        tk.Frame(win,bg="#2a1a40",height=1).pack(fill='x')
        mf=tk.Frame(win,bg="#08060f"); mf.pack(fill='both',expand=True)
        vsb=tk.Scrollbar(mf,orient='vertical',bg="#0e0a18",troughcolor="#08060f",width=12)
        hsb=tk.Scrollbar(mf,orient='horizontal',bg="#0e0a18",troughcolor="#08060f",width=10)
        vsb.pack(side='right',fill='y'); hsb.pack(side='bottom',fill='x')
        out=tk.Text(mf,bg="#08060f",fg="#3a2a55",font=("Courier New",9),wrap='none',relief='flat',
                    yscrollcommand=vsb.set,xscrollcommand=hsb.set,state='disabled')
        vsb.config(command=out.yview); hsb.config(command=out.xview); out.pack(fill='both',expand=True)
        for tag,col,extra in [('addr',"#2a1a40",{}),('same',"#1e1830",{}),('ctx',"#2d2248",{}),
                ('chg1',"#e04444",{'background':"#180808"}),('chg2',"#44e060",{'background':"#081308"}),
                ('as1',"#904040",{'background':"#180808"}),('as2',"#409050",{'background':"#081308"}),
                ('div',"#1e1830",{}),('bhdr',"#c080ff",{'background':"#120820",'font':("Courier New",9,"bold")}),
                ('ok',GREEN,{'font':("Courier New",11,"bold")})]:
            out.tag_configure(tag,foreground=col,**extra)
        _diff_thread=[None]; _cancel=[False]
        def asc(chunk): return ''.join(chr(b) if 0x20<=b<0x7F else '.' for b in chunk)
        def render_results(blocks,diff_offs,a,b):
            BPR=16; out.config(state='normal'); out.delete('1.0','end')
            if not diff_offs:
                out.insert('end','\n\n    ✔  İki EXE TAMAMEN AYNI — hiç fark yok!\n','ok')
                out.config(state='disabled'); stat_lbl.config(text="✔ AYNI",fg=GREEN)
                diff_stat.config(text="0 byte fark",fg=GREEN); update_progress(100,""); return
            for bi,(rs,re) in enumerate(blocks):
                db=sum(1 for i in diff_offs if rs*BPR<=i<(re+1)*BPR)
                out.insert('end',f'  BLOK {bi+1}/{len(blocks)}   0x{rs*BPR:08X} – 0x{min((re+1)*BPR-1,max(len(a),len(b))-1):08X}   ({db} byte değişti)\n','bhdr')
                for row in range(rs,re+1):
                    fo=row*BPR; ca=bytearray(BPR); cb=bytearray(BPR)
                    if fo<len(a): ca[:min(BPR,len(a)-fo)]=a[fo:fo+BPR]
                    if fo<len(b): cb[:min(BPR,len(b)-fo)]=b[fo:fo+BPR]
                    is_dr=row*BPR in{i&~(BPR-1) for i in diff_offs if rs*BPR<=i<(re+1)*BPR}
                    out.insert('end',f'  {fo:08X}  ','addr')
                    for g in range(4):
                        for k in range(4):
                            idx=g*4+k; t='chg1' if(is_dr and(fo+idx)in diff_offs) else 'ctx'
                            out.insert('end',f'{ca[idx]:02X}',t); out.insert('end',' ','same')
                        if g<3: out.insert('end','  ','same')
                    out.insert('end','  '); out.insert('end',f'|{asc(ca)}|','as1' if is_dr else 'ctx')
                    out.insert('end','  |  ','div')
                    for g in range(4):
                        for k in range(4):
                            idx=g*4+k; t='chg2' if(is_dr and(fo+idx)in diff_offs) else 'ctx'
                            out.insert('end',f'{cb[idx]:02X}',t); out.insert('end',' ','same')
                        if g<3: out.insert('end','  ','same')
                    out.insert('end','  '); out.insert('end',f'|{asc(cb)}|\n','as2' if is_dr else 'ctx')
                out.insert('end','\n')
            if len(a)!=len(b): out.insert('end',f'  BOYUT FARKI: EXE1={len(a):,}b  EXE2={len(b):,}b  ({len(b)-len(a):+,}b)\n','bhdr')
            out.config(state='disabled'); nb=len(diff_offs)
            stat_lbl.config(text=f'{nb} byte  {len(blocks)} blok',fg="#c080ff")
            diff_stat.config(text=f'{nb} byte değişti  |  {len(blocks)} blok',fg=YELLOW if nb>100 else GREEN); update_progress(100,"")
        def diff_worker(a,b,ctx):
            BPR=16; ml=min(len(a),len(b)); diff_offs=set(); CHUNK=65536; total=max(len(a),len(b))
            for si in range(0,ml,CHUNK):
                if _cancel[0]: return
                ei=min(si+CHUNK,ml)
                for i in range(si,ei):
                    if a[i]!=b[i]: diff_offs.add(i)
                win.after(0,update_progress,int(si*60/total),f"Karşılaştırılıyor… {si//1024}KB / {total//1024}KB")
            for i in range(ml,max(len(a),len(b))): diff_offs.add(i)
            if _cancel[0]: return
            win.after(0,update_progress,65,"Bloklar gruplandırılıyor…")
            diff_rows=sorted(set(i//BPR for i in diff_offs))
            show_rows=set()
            for r in diff_rows:
                for c in range(max(0,r-ctx),r+ctx+1): show_rows.add(c)
            show_rows=sorted(show_rows)
            if not show_rows: win.after(0,render_results,[],set(),a,b); return
            blocks,gs,pr=[],show_rows[0],show_rows[0]
            for r in show_rows[1:]:
                if r>pr+1: blocks.append((gs,pr)); gs=r
                pr=r
            blocks.append((gs,pr))
            if _cancel[0]: return
            win.after(0,update_progress,80,f"{len(diff_offs)} byte fark, {len(blocks)} blok…")
            win.after(0,render_results,blocks,diff_offs,a,b)
        def start_diff():
            if not all(raw_data): return
            _cancel[0]=True
            if _diff_thread[0] and _diff_thread[0].is_alive(): _diff_thread[0].join(timeout=0.1)
            _cancel[0]=False
            out.config(state='normal'); out.delete('1.0','end'); out.insert('end','  Hesaplanıyor…','ctx'); out.config(state='disabled')
            update_progress(0,"Başlıyor…"); diff_stat.config(text="Hesaplanıyor…",fg=YELLOW)
            t=threading.Thread(target=diff_worker,args=(bytes(raw_data[0]),bytes(raw_data[1]),ctx_var.get()),daemon=True)
            _diff_thread[0]=t; t.start()
        def pick(idx):
            p=filedialog.askopenfilename(title=f"EXE {idx+1} Seç",filetypes=[("EXE","*.exe"),("All","*.*")],parent=win)
            if not p: return
            try:
                with open(p,'rb') as fh: raw_data[idx]=fh.read()
                sz=len(raw_data[idx]); name_lbls[idx].config(text=f"EXE {idx+1}: {os.path.basename(p)[:28]}  ({sz//1024}KB)",fg=GREEN)
                if all(raw_data): win.after(80,start_diff)
            except Exception as e: messagebox.showerror("Hata",str(e),parent=win)
        def use_current():
            if not self._orig_raw: messagebox.showwarning("","Önce PM2'ye EXE yükleyin!",parent=win); return
            raw_data[0]=bytes(self._orig_raw); sz=len(raw_data[0])
            name_lbls[0].config(text=f"EXE 1: {os.path.basename(self.exe_path or 'mevcut.exe')[:28]}  ({sz//1024}KB)",fg=GREEN)
            if all(raw_data): win.after(80,start_diff)
        bot2=tk.Frame(win,bg="#0e0a18",pady=5); bot2.pack(fill='x',side='bottom')
        tk.Frame(win,bg="#2a1a40",height=1).pack(fill='x',side='bottom')
        def mkb(t,cmd,bg_,fg_): return tk.Button(bot2,text=t,command=cmd,bg=bg_,fg=fg_,font=("Courier New",9,"bold"),relief='flat',cursor='hand2',padx=10,pady=4,activebackground="#2a1a40",activeforeground='white')
        mkb("📂 EXE 1",lambda:pick(0),"#1a1030","#c080ff").pack(side='left',padx=6)
        mkb("🎯 Mevcut→EXE1",use_current,"#0d1a10",GREEN).pack(side='left',padx=2)
        mkb("📂 EXE 2",lambda:pick(1),"#0f1830",ACCENT2).pack(side='left',padx=6)
        mkb("🔄 Yenile",start_diff,"#1a1030","#c080ff").pack(side='left',padx=4)
        def export():
            if not all(raw_data): messagebox.showwarning("","Önce iki EXE yükleyin!",parent=win); return
            p=filedialog.asksaveasfilename(defaultextension=".txt",filetypes=[("Text","*.txt")],parent=win)
            if p:
                with open(p,'w',encoding='utf-8') as fh: fh.write(out.get('1.0','end'))
        mkb("💾 Kaydet",export,BG3,ACCENT2).pack(side='right',padx=8)
        win.protocol("WM_DELETE_WINDOW",lambda:(_cancel.__setitem__(0,True),win.destroy()))

    # ══════════════════════════════════════════════════════════════════════
    #  CREDITS
    # ══════════════════════════════════════════════════════════════════════
    def show_credits(self):
        win = tk.Toplevel(self, bg=BG)
        win.title("Credits")
        win.geometry("440x360")
        win.resizable(False, False)
        win.grab_set()
        tk.Frame(win, bg=ACCENT, height=3).pack(fill='x')
        tk.Label(win, text="⚔", font=("Courier New", 36), bg=BG, fg=ACCENT).pack(pady=(18, 4))
        tk.Label(win, text="PM2 Translation Tool", font=("Courier New", 14, "bold"), bg=BG, fg=FG).pack()
        tk.Label(win, text="v22  ·  Hex Editor + Pointer Relocation + Auto Backup",
                 font=("Courier New", 9), bg=BG, fg=FG2).pack()
        tk.Frame(win, bg=BORDER, height=1).pack(fill='x', padx=20, pady=10)
        for lbl, val, col in [
            ("Yazar / Dev :", "Mete Karace",       ACCENT),
            ("Çeviri Ekibi:", "AncaÇeviri",        ACCENT2),
            ("Oyun        :", "Princess Maker 2",  FG),
        ]:
            row = tk.Frame(win, bg=BG); row.pack(pady=3)
            tk.Label(row, text=lbl, font=("Courier New", 9), bg=BG, fg=FG2,
                     width=16, anchor='e').pack(side='left')
            tk.Label(row, text=val, font=("Courier New", 10, "bold"), bg=BG,
                     fg=col).pack(side='left', padx=8)
        tk.Frame(win, bg=BORDER, height=1).pack(fill='x', padx=20, pady=10)
        for line in [
            "v22: Hex Byte Editörü (tıkla→değiştir→Uygula)",
            "v22: _manual_patches — ham yamalar EXE kayıtta korunur",
            "v22: BUG FIX: f-string, _hv_send_selection, _hex_click, tag yenileme",
            "v21: Ctrl+Z/Y · Otomatik Yedek · Kayıt Geçmişi",
            "AncaÇeviri ~ Türk Oyun Çeviri Topluluğu",
        ]:
            tk.Label(win, text=line, font=("Courier New", 7), bg=BG, fg=FG2).pack()
        tk.Button(win, text="Kapat", command=win.destroy,
                  bg=ACCENT, fg="#000", font=("Courier New", 9, "bold"),
                  relief='flat', cursor='hand2', width=12, pady=5,
                  activebackground=GREEN).pack(pady=10)
        tk.Frame(win, bg=ACCENT, height=3).pack(fill='x', side='bottom')

    # ══════════════════════════════════════════════════════════════════════
    #  KAPATMA
    # ══════════════════════════════════════════════════════════════════════
    def _on_close(self):
        if self.unsaved:
            ans = messagebox.askyesnocancel(
                "💾 Kaydet?",
                "Kaydedilmemiş çeviriler var!\nEXE olarak kaydetmek ister misiniz?",
                icon='warning')
            if ans is True:
                self.save_exe(); self.destroy()
            elif ans is False:
                self.destroy()
        else:
            self.destroy()


# ═══════════════════════════════════════════════════════════════════════════
#  GİRİŞ NOKTASI
# ═══════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    try:
        app = PM2Translator()
        app.mainloop()
    except Exception:
        import tkinter as _tk, tkinter.messagebox as _mb
        try:
            _r = _tk.Tk(); _r.withdraw()
            _mb.showerror("Başlatma Hatası", traceback.format_exc())
            _r.destroy()
        except Exception:
            with open("pm2_crash.log", "w", encoding="utf-8") as _f:
                _f.write(f"{datetime.datetime.now()}\n{traceback.format_exc()}")