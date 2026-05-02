"""
deepcore_office_panel.py — Panel UI "DeepCore Oficina IA"
Ventana modal CustomTkinter para exportar datos a Excel, Word y PowerPoint con IA.

Uso:
    from deepcore_office_panel import PanelOficina

    # Desde cualquier programa DeepCore:
    def abrir_oficina():
        PanelOficina(
            master=root,
            programa="Inventario Pro",
            api_key=db.get_config('api_key', ''),
            get_datos=lambda: {
                'titulo': 'Reporte de Inventario',
                'columnas': ['Producto', 'Stock', 'Precio', 'Categoría'],
                'filas': db.listar_productos(),
                'kpis': {'Total productos': 142, 'Stock bajo': 8, 'Valor total': '$15,400'}
            }
        )
"""

import os
import sys
import threading
import subprocess
import customtkinter as ctk
from tkinter import messagebox


# ── Paleta DeepCore Dark ──────────────────────────────────────────────────────
C = {
    'base':    '#0F172A',
    'mantle':  '#0B1120',
    'surface0':'#1E293B',
    'surface1':'#334155',
    'surface2':'#475569',
    'overlay': '#64748B',
    'text':    '#F8FAFC',
    'subtext': '#94A3B8',
    'blue':    '#3B82F6',
    'green':   '#22C55E',
    'amber':   '#F59E0B',
    'teal':    '#14B8A6',
    'violet':  '#8B5CF6',
    'red':     '#EF4444',
    'border':  '#334155',
}

FORMATS = [
    {
        'key':   'excel',
        'label': 'Excel',
        'color': C['green'],
        'icon':  'XLS',
        'desc':  'Hoja de cálculo profesional con formato DeepCore,\n'
                 'tablas de datos, KPIs y análisis IA en pestaña separada.',
        'ext':   '.xlsx',
        'tips':  [
            'Incluye hoja "Análisis IA" con insights del negocio',
            'Filas alternas, encabezados con marca DeepCore',
            'KPIs destacados en la parte superior',
        ],
    },
    {
        'key':   'word',
        'label': 'Word',
        'color': C['blue'],
        'icon':  'DOC',
        'desc':  'Reporte ejecutivo en Word con resumen escrito por IA,\n'
                 'tablas de datos formateadas y pie de página corporativo.',
        'ext':   '.docx',
        'tips':  [
            'Resumen ejecutivo generado automáticamente por IA',
            'Tablas con colores DeepCore dark',
            'Listo para imprimir o compartir',
        ],
    },
    {
        'key':   'pptx',
        'label': 'PowerPoint',
        'color': C['amber'],
        'icon':  'PPT',
        'desc':  'Presentación lista para reuniones: portada, KPIs en cards,\n'
                 'tabla de datos y slide de recomendaciones IA.',
        'ext':   '.pptx',
        'tips':  [
            '5 slides: portada, KPIs, datos, recomendaciones IA, cierre',
            'Tema DeepCore dark profesional',
            'Slide de recomendaciones escrita por IA',
        ],
    },
]


class PanelOficina(ctk.CTkToplevel):
    """
    Ventana modal "DeepCore Oficina IA".
    Muestra 3 formatos (Excel, Word, PPT) con descripción y genera con IA.
    """

    def __init__(self, master, programa: str, api_key: str, get_datos,
                 width: int = 720, height: int = 560):
        """
        Args:
            master:    Ventana padre (ctk.CTk o CTkToplevel)
            programa:  Nombre del programa (ej: "Inventario Pro")
            api_key:   Clave Anthropic para IA (puede ser '' para deshabilitar IA)
            get_datos: Callable sin args que devuelve dict con claves:
                       titulo, columnas, filas, kpis (opcional), subtitulo (opcional)
        """
        super().__init__(master)
        self.programa  = programa
        self.api_key   = api_key
        self.get_datos = get_datos
        self._fmt_sel  = 'excel'
        self._busy     = False

        self.title(f'DeepCore Oficina IA — {programa}')
        self.geometry(f'{width}x{height}')
        self.resizable(False, False)
        self.configure(fg_color=C['base'])
        self.grab_set()
        self.lift()
        self.focus_force()

        # Centrar en ventana padre
        self.update_idletasks()
        px = master.winfo_x() + (master.winfo_width()  // 2) - (width  // 2)
        py = master.winfo_y() + (master.winfo_height() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{px}+{py}')

        self._build_ui()

    # ── Construcción de UI ────────────────────────────────────────────────────

    def _build_ui(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color=C['mantle'], height=56, corner_radius=0)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)

        badge = ctk.CTkFrame(hdr, fg_color=C['blue'], corner_radius=6, width=42, height=26)
        badge.pack(side='left', padx=(16, 10), pady=15)
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text='DC', font=ctk.CTkFont(size=12, weight='bold'),
                     text_color=C['base']).place(relx=0.5, rely=0.5, anchor='center')

        ctk.CTkLabel(hdr, text='Oficina IA',
                     font=ctk.CTkFont(size=15, weight='bold'),
                     text_color=C['text']).pack(side='left')
        ctk.CTkLabel(hdr, text=f'— {self.programa}',
                     font=ctk.CTkFont(size=13),
                     text_color=C['subtext']).pack(side='left', padx=(6, 0))

        ai_badge_color = C['green'] if self.api_key else C['overlay']
        ai_text = '● IA activa' if self.api_key else '○ IA desactivada'
        ctk.CTkLabel(hdr, text=ai_text,
                     font=ctk.CTkFont(size=11),
                     text_color=ai_badge_color).pack(side='right', padx=20)

        ctk.CTkFrame(self, fg_color=C['border'], height=1).pack(fill='x')

        # Body
        body = ctk.CTkFrame(self, fg_color='transparent')
        body.pack(fill='both', expand=True, padx=20, pady=16)

        # ── Selector de formato (izquierda) ───────────────────────────────────
        left = ctk.CTkFrame(body, fg_color='transparent', width=200)
        left.pack(side='left', fill='y', padx=(0, 12))
        left.pack_propagate(False)

        ctk.CTkLabel(left, text='FORMATO',
                     font=ctk.CTkFont(size=9, weight='bold'),
                     text_color=C['overlay']).pack(anchor='w', pady=(0, 8))

        self._fmt_btns = {}
        for fmt in FORMATS:
            btn = self._fmt_card(left, fmt)
            btn.pack(fill='x', pady=4)
            self._fmt_btns[fmt['key']] = btn

        # ── Panel derecho (detalle + acción) ───────────────────────────────────
        right = ctk.CTkFrame(body, fg_color=C['surface0'],
                             corner_radius=12, border_width=1,
                             border_color=C['border'])
        right.pack(side='left', fill='both', expand=True)
        self._right = right
        self._build_detail()

        # ── Seleccionar Excel por defecto ─────────────────────────────────────
        self._select_format('excel')

    def _fmt_card(self, parent, fmt: dict) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(parent, fg_color=C['surface0'],
                             corner_radius=10, border_width=1,
                             border_color=C['border'], cursor='hand2')

        inner = ctk.CTkFrame(frame, fg_color='transparent')
        inner.pack(fill='x', padx=12, pady=10)

        # Badge de formato
        badge_frame = ctk.CTkFrame(inner, fg_color=fmt['color'],
                                   corner_radius=6, width=40, height=26)
        badge_frame.pack(side='left', padx=(0, 10))
        badge_frame.pack_propagate(False)
        ctk.CTkLabel(badge_frame, text=fmt['icon'],
                     font=ctk.CTkFont(size=9, weight='bold'),
                     text_color=C['base']).place(relx=0.5, rely=0.5, anchor='center')

        ctk.CTkLabel(inner, text=fmt['label'],
                     font=ctk.CTkFont(size=13, weight='bold'),
                     text_color=C['text']).pack(side='left')

        frame.bind('<Button-1>', lambda e, k=fmt['key']: self._select_format(k))
        inner.bind('<Button-1>', lambda e, k=fmt['key']: self._select_format(k))
        for w in inner.winfo_children():
            w.bind('<Button-1>', lambda e, k=fmt['key']: self._select_format(k))

        frame._fmt_key = fmt['key']
        return frame

    def _build_detail(self):
        for w in self._right.winfo_children():
            w.destroy()

        fmt = next(f for f in FORMATS if f['key'] == self._fmt_sel)

        # Barra de color superior
        bar = ctk.CTkFrame(self._right, fg_color=fmt['color'],
                            height=4, corner_radius=0)
        bar.pack(fill='x')

        content = ctk.CTkFrame(self._right, fg_color='transparent')
        content.pack(fill='both', expand=True, padx=20, pady=16)

        # Badge grande
        row = ctk.CTkFrame(content, fg_color='transparent')
        row.pack(fill='x', pady=(0, 12))
        badge = ctk.CTkFrame(row, fg_color=fmt['color'],
                              corner_radius=8, width=56, height=34)
        badge.pack(side='left', padx=(0, 12))
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text=fmt['icon'],
                     font=ctk.CTkFont(size=13, weight='bold'),
                     text_color=C['base']).place(relx=0.5, rely=0.5, anchor='center')

        ctk.CTkLabel(row, text=f'Exportar a {fmt["label"]} {fmt["ext"]}',
                     font=ctk.CTkFont(size=16, weight='bold'),
                     text_color=C['text']).pack(side='left')

        # Descripción
        ctk.CTkLabel(content, text=fmt['desc'],
                     font=ctk.CTkFont(size=12),
                     text_color=C['subtext'],
                     justify='left',
                     anchor='w').pack(fill='x', pady=(0, 12))

        # Tips
        tips_frame = ctk.CTkFrame(content, fg_color=C['mantle'],
                                   corner_radius=8, border_width=1,
                                   border_color=C['border'])
        tips_frame.pack(fill='x', pady=(0, 16))
        ctk.CTkLabel(tips_frame, text='QUE INCLUYE',
                     font=ctk.CTkFont(size=9, weight='bold'),
                     text_color=C['overlay']).pack(anchor='w', padx=12, pady=(10, 4))
        for tip in fmt['tips']:
            row_tip = ctk.CTkFrame(tips_frame, fg_color='transparent')
            row_tip.pack(fill='x', padx=12, pady=2)
            ctk.CTkLabel(row_tip, text='●',
                         font=ctk.CTkFont(size=8),
                         text_color=fmt['color']).pack(side='left', padx=(0, 6))
            ctk.CTkLabel(row_tip, text=tip,
                         font=ctk.CTkFont(size=11),
                         text_color=C['text']).pack(side='left')
        ctk.CTkFrame(tips_frame, fg_color='transparent', height=8).pack()

        # Nota IA
        if not self.api_key:
            nota = ctk.CTkFrame(content, fg_color='#1C1A12',
                                 corner_radius=8, border_width=1,
                                 border_color=C['amber'])
            nota.pack(fill='x', pady=(0, 12))
            ctk.CTkLabel(nota,
                         text='Sin API key: el archivo se generará sin análisis IA.\n'
                              'Agrega tu clave en Configuración → IA para activarla.',
                         font=ctk.CTkFont(size=11),
                         text_color=C['amber'],
                         justify='left').pack(padx=12, pady=8, anchor='w')

        # Ruta de destino
        ctk.CTkLabel(content,
                     text=f'Destino: ~/Documents/DeepCore/Exports/',
                     font=ctk.CTkFont(size=10),
                     text_color=C['overlay']).pack(anchor='w', pady=(0, 12))

        # Spinner / estado
        self._lbl_estado = ctk.CTkLabel(content, text='',
                                         font=ctk.CTkFont(size=12),
                                         text_color=C['green'])
        self._lbl_estado.pack(anchor='w', pady=(0, 6))

        self._progress = ctk.CTkProgressBar(content, height=4,
                                             corner_radius=2,
                                             fg_color=C['surface1'],
                                             progress_color=fmt['color'])
        self._progress.pack(fill='x', pady=(0, 12))
        self._progress.set(0)

        # Botón generar
        self._btn_gen = ctk.CTkButton(
            content,
            text=f'Generar {fmt["label"]} con IA' if self.api_key else f'Generar {fmt["label"]}',
            height=42,
            corner_radius=8,
            fg_color=fmt['color'],
            hover_color=C['teal'],
            text_color=C['base'],
            font=ctk.CTkFont(size=14, weight='bold'),
            command=self._generar,
        )
        self._btn_gen.pack(fill='x')

    def _select_format(self, key: str):
        if self._busy:
            return
        self._fmt_sel = key
        for k, btn in self._fmt_btns.items():
            fmt = next(f for f in FORMATS if f['key'] == k)
            if k == key:
                btn.configure(fg_color=C['surface1'],
                              border_color=fmt['color'])
            else:
                btn.configure(fg_color=C['surface0'],
                              border_color=C['border'])
        self._build_detail()

    # ── Generación ────────────────────────────────────────────────────────────

    def _generar(self):
        if self._busy:
            return
        self._busy = True
        self._btn_gen.configure(state='disabled', text='Generando...')
        self._lbl_estado.configure(text='Preparando datos...', text_color=C['subtext'])
        self._progress.set(0.05)
        self.update()
        threading.Thread(target=self._generar_bg, daemon=True).start()

    def _generar_bg(self):
        try:
            datos = self.get_datos()
            self._set_estado('Procesando datos...', 0.2)

            titulo   = datos.get('titulo', f'Reporte {self.programa}')
            columnas = datos.get('columnas', [])
            filas    = datos.get('filas', [])
            kpis     = datos.get('kpis')
            subtitulo= datos.get('subtitulo', '')

            try:
                from deepcore_office import exportar_excel, exportar_word, exportar_pptx
            except ImportError:
                import importlib.util, pathlib
                p = pathlib.Path(__file__).parent
                spec = importlib.util.spec_from_file_location(
                    'deepcore_office', p / 'deepcore_office.py')
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                exportar_excel = mod.exportar_excel
                exportar_word  = mod.exportar_word
                exportar_pptx  = mod.exportar_pptx

            if self.api_key:
                self._set_estado('Analizando con IA...', 0.4)
            else:
                self._set_estado('Generando archivo...', 0.5)

            kwargs = dict(
                titulo=titulo, columnas=columnas, filas=filas,
                kpis=kpis, programa=self.programa,
                api_key=self.api_key, subtitulo=subtitulo,
            )

            if self._fmt_sel == 'excel':
                self._set_estado('Creando Excel...', 0.7)
                ruta = exportar_excel(**kwargs)
            elif self._fmt_sel == 'word':
                self._set_estado('Redactando Word...', 0.7)
                ruta = exportar_word(**kwargs)
            else:
                self._set_estado('Diseñando presentación...', 0.7)
                ruta = exportar_pptx(**kwargs)

            self._set_estado('Listo.', 1.0, color=C['green'])
            self.after(200, lambda: self._done(ruta))

        except Exception as e:
            self._set_estado(f'Error: {e}', 0, color=C['red'])
            self._busy = False
            self.after(0, lambda: self._btn_gen.configure(state='normal',
                                                           text=self._btn_label()))

    def _set_estado(self, texto: str, progreso: float, color: str = None):
        self.after(0, lambda: [
            self._lbl_estado.configure(text=texto, text_color=color or C['subtext']),
            self._progress.set(progreso),
        ])

    def _btn_label(self) -> str:
        fmt = next(f for f in FORMATS if f['key'] == self._fmt_sel)
        return f'Generar {fmt["label"]} con IA' if self.api_key else f'Generar {fmt["label"]}'

    def _done(self, ruta: str):
        self._busy = False
        fmt = next(f for f in FORMATS if f['key'] == self._fmt_sel)

        # Actualizar botón a "Abrir archivo"
        self._btn_gen.configure(
            state='normal',
            text='Abrir archivo',
            fg_color=C['surface1'],
            hover_color=C['surface2'],
            text_color=C['text'],
            command=lambda: self._abrir(ruta),
        )

        # Botón adicional para abrir carpeta
        self._lbl_estado.configure(
            text=f'Guardado en: .../{os.path.basename(ruta)}',
            text_color=C['green'],
        )

        if messagebox.askyesno(
            'Archivo generado',
            f'El archivo fue creado exitosamente:\n\n{os.path.basename(ruta)}\n\n'
            '¿Deseas abrirlo ahora?',
            parent=self,
        ):
            self._abrir(ruta)

    def _abrir(self, ruta: str):
        try:
            if sys.platform == 'win32':
                os.startfile(ruta)
            elif sys.platform == 'darwin':
                subprocess.run(['open', ruta])
            else:
                subprocess.run(['xdg-open', ruta])
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo abrir el archivo:\n{e}', parent=self)


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIÓN DE CONVENIENCIA
# ═══════════════════════════════════════════════════════════════════════════════

def abrir_panel_oficina(master, programa: str, api_key: str, get_datos):
    """
    Abre el panel de Oficina IA. Función directa para usar desde cualquier programa.

    Ejemplo:
        abrir_panel_oficina(
            master=self,
            programa="Inventario Pro",
            api_key=db.get_config('api_key', ''),
            get_datos=lambda: {
                'titulo': 'Inventario Actual',
                'columnas': ['Producto', 'Stock', 'Precio'],
                'filas': [[p['nombre'], p['stock'], p['precio']] for p in db.listar_productos()],
                'kpis': {
                    'Total productos': len(db.listar_productos()),
                    'Stock crítico': db.count_stock_bajo(),
                },
            }
        )
    """
    PanelOficina(master, programa=programa, api_key=api_key, get_datos=get_datos)
