"""
DeepCore Agenda Pro v1.0.0
Sistema de gestión de citas y turnos para negocios ecuatorianos.
"""
import ctypes as _ctypes, sys as _sys
if _sys.platform == 'win32':
    _cw = _ctypes.windll.kernel32.GetConsoleWindow()
    if _cw: _ctypes.windll.user32.ShowWindow(_cw, 0)

import os as _os2, traceback as _tb2
def _on_crash(_t, _v, _tb):
    try:
        _d = _os2.path.join(_os2.environ.get('APPDATA', _os2.path.expanduser('~')), 'DeepCore')
        _os2.makedirs(_d, exist_ok=True)
        open(_os2.path.join(_d, 'crash_agenda.log'), 'w', encoding='utf-8').write(
            ''.join(_tb2.format_exception(_t, _v, _tb)))
    except Exception: pass
    try:
        import tkinter as _tk2
        _r2 = _tk2.Tk(); _r2.withdraw()
        _tk2.messagebox.showerror("Error", f"Error al iniciar:\n\n{_v}")
        _r2.destroy()
    except Exception: pass
_sys.excepthook = _on_crash

import sys, os, json, threading, webbrowser, urllib.request as _urllib
from datetime import datetime, date

APP_VERSION    = '1.0.0'
_REPO_RELEASES = 'https://api.github.com/repos/DeepCoreec/deepcore-agenda-pro/releases/latest'

import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk

import database as db
from theme import C
from modules.licencia import validar_llave, estado_licencia, llave_guardada, guardar_llave, get_hardware_id
from modules.dashboard import DashboardPanel
from modules.agenda    import AgendaPanel
from modules.clientes  import ClientesPanel
from modules.servicios import ServiciosPanel

ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('dark-blue')

# ── Ventana de login / licencia ───────────────────────────────────────────────

class VentanaLicencia(ctk.CTkToplevel):
    def __init__(self, master, on_ok):
        super().__init__(master)
        self.on_ok = on_ok
        self.title('DeepCore Agenda Pro — Activación')
        self.geometry('440x320')
        self.configure(fg_color=C['base'])
        self.grab_set()
        self.resizable(False, False)
        self.protocol('WM_DELETE_WINDOW', lambda: master.destroy())
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 440) // 2
        y = (self.winfo_screenheight() - 320) // 2
        self.geometry(f'+{x}+{y}')
        self._build()

    def _build(self):
        ctk.CTkFrame(self, fg_color=C['blue'], height=3, corner_radius=0).pack(fill='x')
        body = ctk.CTkFrame(self, fg_color='transparent')
        body.pack(fill='both', expand=True, padx=32, pady=24)

        # Badge
        badge = ctk.CTkFrame(body, fg_color=C['blue'], corner_radius=8, width=40, height=30)
        badge.pack(anchor='w', pady=(0, 14))
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text='DC', font=ctk.CTkFont(size=13, weight='bold'),
                     text_color=C['base']).place(relx=.5, rely=.5, anchor='center')

        ctk.CTkLabel(body, text='DeepCore Agenda Pro',
                     font=ctk.CTkFont(size=20, weight='bold'),
                     text_color=C['text']).pack(anchor='w')
        ctk.CTkLabel(body, text='Ingresa tu clave de licencia para continuar.',
                     font=ctk.CTkFont(size=12), text_color=C['subtext']).pack(anchor='w', pady=(4, 20))

        self._entry = ctk.CTkEntry(body, placeholder_text='XXXX-XXXX-XXXX-XXXX',
                                    height=40, corner_radius=8,
                                    fg_color=C['surface0'], border_color=C['border'],
                                    border_width=1, text_color=C['text'],
                                    placeholder_text_color=C['overlay0'],
                                    font=ctk.CTkFont(size=15))
        self._entry.pack(fill='x')
        self._entry.bind('<Return>', lambda e: self._activar())

        self._lbl_msg = ctk.CTkLabel(body, text='', font=ctk.CTkFont(size=11),
                                      text_color=C['red'])
        self._lbl_msg.pack(anchor='w', pady=(6, 0))

        btn_row = ctk.CTkFrame(body, fg_color='transparent')
        btn_row.pack(fill='x', pady=(10, 0))
        ctk.CTkButton(btn_row, text='Activar', width=160, height=38, corner_radius=8,
                      fg_color=C['green'], hover_color=C['teal'], text_color='#000000',
                      font=ctk.CTkFont(size=14, weight='bold'),
                      command=self._activar).pack(side='left')
        ctk.CTkButton(btn_row, text='Comprar licencia', width=140, height=38, corner_radius=8,
                      fg_color='transparent', hover_color=C['surface1'],
                      border_width=1, border_color=C['border'], text_color=C['subtext'],
                      font=ctk.CTkFont(size=13),
                      command=lambda: webbrowser.open('https://deepcore.ec')).pack(side='left', padx=10)

        ctk.CTkLabel(body, text=f'Hardware ID: {get_hardware_id()}',
                     font=ctk.CTkFont(size=9), text_color=C['overlay0']).pack(anchor='w', pady=(16, 0))

    def _activar(self):
        key = self._entry.get().strip()
        if not key:
            return
        self._lbl_msg.configure(text='Verificando...', text_color=C['subtext'])
        self.update()
        valida, msg = validar_llave(key)
        if valida:
            guardar_llave(key)
            self.after(200, lambda: (self.destroy(), self.on_ok()))
        else:
            self._lbl_msg.configure(text=msg, text_color=C['red'])


# ── Ventana principal ─────────────────────────────────────────────────────────

class DeepCoreAgenda(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f'DeepCore Agenda Pro v{APP_VERSION}')
        self.geometry('1200x720')
        self.minsize(900, 600)
        self.configure(fg_color=C['base'])
        self._panel_activo = None
        self._panels: dict = {}
        self._nav_btns: dict = {}
        self._build_ui()
        self.after(500,  self._verificar_licencia)
        self.after(3000, self._verificar_actualizacion)

    # ── Layout ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Topbar
        topbar = ctk.CTkFrame(self, fg_color=C['mantle'], height=52, corner_radius=0)
        topbar.pack(side='top', fill='x')
        topbar.pack_propagate(False)
        ctk.CTkFrame(topbar, fg_color=C['border'], height=1).place(relx=0, rely=1.0, relwidth=1.0, anchor='sw')

        badge = ctk.CTkFrame(topbar, fg_color=C['blue'], corner_radius=7, width=34, height=26)
        badge.pack(side='left', padx=(16, 10), pady=13)
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text='DC', font=ctk.CTkFont(size=12, weight='bold'),
                     text_color=C['base']).place(relx=.5, rely=.5, anchor='center')

        ctk.CTkLabel(topbar, text='DeepCore Agenda Pro',
                     font=ctk.CTkFont(size=15, weight='bold'),
                     text_color=C['text']).pack(side='left')

        # Botón Oficina IA
        ctk.CTkButton(topbar, text='Oficina IA', width=90, height=28, corner_radius=7,
                      fg_color='#0F4C21', hover_color='#16A34A', text_color='#22C55E',
                      font=ctk.CTkFont(size=12, weight='bold'),
                      command=self._abrir_oficina).pack(side='right', padx=16)

        self._lbl_lic = ctk.CTkLabel(topbar, text='', font=ctk.CTkFont(size=10),
                                      text_color=C['subtext'])
        self._lbl_lic.pack(side='right', padx=8)

        ctk.CTkLabel(topbar, text=f'v{APP_VERSION}', font=ctk.CTkFont(size=10),
                     text_color=C['overlay0']).pack(side='right', padx=4)

        # Body
        body = ctk.CTkFrame(self, fg_color='transparent', corner_radius=0)
        body.pack(fill='both', expand=True)

        # Sidebar
        sidebar = ctk.CTkFrame(body, fg_color=C['mantle'], width=200, corner_radius=0)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        ctk.CTkFrame(body, fg_color=C['border'], width=1).pack(side='left', fill='y')

        # Contenido
        self._content = ctk.CTkFrame(body, fg_color=C['base'], corner_radius=0)
        self._content.pack(side='left', fill='both', expand=True)

        # Navegación
        ctk.CTkLabel(sidebar, text='MENÚ PRINCIPAL',
                     font=ctk.CTkFont(size=9, weight='bold'),
                     text_color=C['overlay0']).pack(anchor='w', padx=20, pady=(20, 8))

        nav_items = [
            ('dashboard', 'Dashboard'),
            ('agenda',    'Agenda'),
            ('clientes',  'Clientes'),
            ('servicios', 'Servicios'),
        ]
        for key, label in nav_items:
            btn = ctk.CTkButton(sidebar, text=label, anchor='w', height=38, corner_radius=8,
                                fg_color='transparent', hover_color=C['surface0'],
                                text_color=C['subtext'], font=ctk.CTkFont(size=13),
                                command=lambda k=key: self._nav(k))
            btn.pack(fill='x', padx=10, pady=2)
            self._nav_btns[key] = btn

        # Versión en sidebar
        ctk.CTkLabel(sidebar, text=f'DeepCore Agenda Pro\nv{APP_VERSION}',
                     font=ctk.CTkFont(size=9), text_color=C['overlay0'],
                     justify='left').pack(side='bottom', anchor='w', padx=20, pady=14)

        self._nav('dashboard')

    def _nav(self, key: str):
        if key not in self._panels:
            constructores = {
                'dashboard': DashboardPanel,
                'agenda':    AgendaPanel,
                'clientes':  ClientesPanel,
                'servicios': ServiciosPanel,
            }
            self._panels[key] = constructores[key](self._content, C)

        if self._panel_activo:
            self._panel_activo.pack_forget()

        self._panels[key].pack(fill='both', expand=True)
        self._panel_activo = self._panels[key]

        for k, btn in self._nav_btns.items():
            if k == key:
                btn.configure(fg_color=C['surface0'], text_color=C['blue'],
                              font=ctk.CTkFont(size=13, weight='bold'))
            else:
                btn.configure(fg_color='transparent', text_color=C['subtext'],
                              font=ctk.CTkFont(size=13))

        # Refrescar si el panel tiene ese método
        panel = self._panels[key]
        if hasattr(panel, 'refrescar'):
            panel.refrescar()

    # ── Licencia ─────────────────────────────────────────────────────────────

    def _verificar_licencia(self):
        key = llave_guardada()
        if not key:
            VentanaLicencia(self, on_ok=self._post_licencia)
            return
        estado = estado_licencia(key)
        if not estado['valida']:
            VentanaLicencia(self, on_ok=self._post_licencia)
        else:
            self._post_licencia(key=key, estado=estado)

    def _post_licencia(self, key: str = None, estado: dict = None):
        if key is None:
            key = llave_guardada()
        if estado is None and key:
            estado = estado_licencia(key)
        if estado:
            dias = estado.get('dias', 0)
            color = estado.get('color', C['green'])
            self._lbl_lic.configure(text=f'● Licencia activa · {dias}d', text_color=color)
            if estado.get('advertir'):
                messagebox.showwarning('Licencia próxima a vencer',
                                       f"{estado.get('mensaje')}\n\nRenueva en deepcore.ec", parent=self)

    # ── Actualización ─────────────────────────────────────────────────────────

    def _verificar_actualizacion(self):
        def _check():
            try:
                req = _urllib.Request(_REPO_RELEASES, headers={'User-Agent': 'DeepCore-Agenda/1.0'})
                with _urllib.urlopen(req, timeout=6) as r:
                    data = json.loads(r.read(65536))
                tag = data.get('tag_name', '').lstrip('v')
                if tag and tag > APP_VERSION:
                    self.after(0, lambda: self._notif_update(tag, data.get('html_url', '')))
            except Exception:
                pass
        threading.Thread(target=_check, daemon=True).start()

    def _notif_update(self, nueva: str, url: str):
        if messagebox.askyesno('Actualización disponible',
                               f'Nueva versión v{nueva} disponible.\n¿Descargar ahora?', parent=self):
            if url:
                webbrowser.open(url)

    # ── Oficina IA ────────────────────────────────────────────────────────────

    def _abrir_oficina(self):
        try:
            from deepcore_office_panel import PanelOficina
            api_key = db.get_config('api_key', '')

            def _get_datos():
                kpis = db.kpis_hoy()
                citas = db.listar_citas()
                filas = []
                for c in citas[:200]:
                    filas.append([
                        c['fecha'], c['hora_inicio'],
                        c['cliente_nombre'] or '–',
                        c['servicio_nombre'] or '–',
                        c['profesional_nombre'] or '–',
                        c['estado']
                    ])
                return {
                    'titulo': 'Reporte de Agenda',
                    'subtitulo': f'DeepCore Agenda Pro — {date.today().strftime("%d/%m/%Y")}',
                    'columnas': ['Fecha', 'Hora', 'Cliente', 'Servicio', 'Profesional', 'Estado'],
                    'filas': filas,
                    'kpis': {
                        'Citas hoy': kpis['citas_hoy'],
                        'Completadas': kpis['completadas'],
                        'Pendientes': kpis['pendientes'],
                        f'Ingreso hoy': f"${kpis['ingreso_hoy']:.2f}",
                        'Clientes': kpis['total_clientes'],
                        f'Ingreso mes': f"${kpis['ingreso_mes']:.2f}",
                    }
                }

            PanelOficina(self, programa='Agenda Pro', api_key=api_key, get_datos=_get_datos)
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo abrir Oficina IA:\n{e}', parent=self)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app = DeepCoreAgenda()
    app.mainloop()
