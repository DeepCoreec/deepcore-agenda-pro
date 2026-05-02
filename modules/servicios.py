"""
Servicios y Profesionales — Catálogo y configuración
"""
import customtkinter as ctk
from tkinter import messagebox
import database as db

COLORES = ['#3B82F6','#22C55E','#C084FC','#F59E0B','#14B8A6','#EF4444','#818CF8','#38BDF8']


class ServiciosPanel(ctk.CTkFrame):
    def __init__(self, parent, C: dict):
        super().__init__(parent, fg_color='transparent')
        self.C = C
        self._build()
        self.refrescar()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color='transparent')
        hdr.pack(fill='x', padx=24, pady=(20, 0))
        ctk.CTkLabel(hdr, text='Servicios y Profesionales',
                     font=ctk.CTkFont(size=22, weight='bold'),
                     text_color=self.C['heading']).pack(side='left')

        ctk.CTkFrame(self, fg_color=self.C['border'], height=1).pack(fill='x', padx=24, pady=10)

        cols = ctk.CTkFrame(self, fg_color='transparent')
        cols.pack(fill='both', expand=True, padx=24, pady=(0, 16))
        cols.columnconfigure(0, weight=1)
        cols.columnconfigure(1, weight=1)

        # Servicios
        self._frame_sv = ctk.CTkFrame(cols, fg_color=self.C['surface0'],
                                       corner_radius=12, border_width=1, border_color=self.C['border'])
        self._frame_sv.grid(row=0, column=0, padx=(0, 8), sticky='nsew')

        sv_hdr = ctk.CTkFrame(self._frame_sv, fg_color='transparent')
        sv_hdr.pack(fill='x', padx=16, pady=(14, 8))
        ctk.CTkLabel(sv_hdr, text='Servicios',
                     font=ctk.CTkFont(size=15, weight='bold'),
                     text_color=self.C['text']).pack(side='left')
        ctk.CTkButton(sv_hdr, text='Agregar', width=80, height=28, corner_radius=6,
                      fg_color=self.C['green'], hover_color=self.C['teal'], text_color='#000000',
                      font=ctk.CTkFont(size=12, weight='bold'),
                      command=self._nuevo_servicio).pack(side='right')

        ctk.CTkFrame(self._frame_sv, fg_color=self.C['border'], height=1).pack(fill='x', padx=16)
        self._lista_sv = ctk.CTkScrollableFrame(self._frame_sv, fg_color='transparent', height=400)
        self._lista_sv.pack(fill='both', expand=True, padx=8, pady=8)
        self._lista_sv.columnconfigure(0, weight=1)

        # Profesionales
        self._frame_pr = ctk.CTkFrame(cols, fg_color=self.C['surface0'],
                                       corner_radius=12, border_width=1, border_color=self.C['border'])
        self._frame_pr.grid(row=0, column=1, padx=(8, 0), sticky='nsew')

        pr_hdr = ctk.CTkFrame(self._frame_pr, fg_color='transparent')
        pr_hdr.pack(fill='x', padx=16, pady=(14, 8))
        ctk.CTkLabel(pr_hdr, text='Profesionales',
                     font=ctk.CTkFont(size=15, weight='bold'),
                     text_color=self.C['text']).pack(side='left')
        ctk.CTkButton(pr_hdr, text='Agregar', width=80, height=28, corner_radius=6,
                      fg_color=self.C['blue'], hover_color=self.C['indigo'], text_color='#FFFFFF',
                      font=ctk.CTkFont(size=12, weight='bold'),
                      command=self._nuevo_prof).pack(side='right')

        ctk.CTkFrame(self._frame_pr, fg_color=self.C['border'], height=1).pack(fill='x', padx=16)
        self._lista_pr = ctk.CTkScrollableFrame(self._frame_pr, fg_color='transparent', height=400)
        self._lista_pr.pack(fill='both', expand=True, padx=8, pady=8)
        self._lista_pr.columnconfigure(0, weight=1)

    def refrescar(self):
        for w in self._lista_sv.winfo_children():
            w.destroy()
        for w in self._lista_pr.winfo_children():
            w.destroy()

        for i, s in enumerate(db.listar_servicios(solo_activos=False)):
            self._fila_servicio(dict(s), i)
        for i, p in enumerate(db.listar_profesionales(solo_activos=False)):
            self._fila_prof(dict(p), i)

    def _fila_servicio(self, s: dict, row: int):
        f = ctk.CTkFrame(self._lista_sv, fg_color=self.C['base'],
                         corner_radius=8, border_width=1, border_color=self.C['border'])
        f.grid(row=row, column=0, pady=3, sticky='ew')

        color_dot = ctk.CTkFrame(f, fg_color=s['color'] or self.C['blue'],
                                  width=6, corner_radius=0)
        color_dot.pack(side='left', fill='y')

        inner = ctk.CTkFrame(f, fg_color='transparent')
        inner.pack(side='left', fill='both', expand=True, padx=10, pady=8)

        top = ctk.CTkFrame(inner, fg_color='transparent')
        top.pack(fill='x')
        ctk.CTkLabel(top, text=s['nombre'],
                     font=ctk.CTkFont(size=13, weight='bold'),
                     text_color=self.C['text']).pack(side='left')
        ctk.CTkButton(top, text='Editar', width=54, height=22, corner_radius=5,
                      fg_color=self.C['surface1'], hover_color=self.C['surface2'],
                      text_color=self.C['subtext'], font=ctk.CTkFont(size=10),
                      command=lambda ss=s: self._editar_servicio(ss)).pack(side='right')

        ctk.CTkLabel(inner, text=f"{s['duracion_min']} min · ${s['precio']:.2f}",
                     font=ctk.CTkFont(size=11), text_color=self.C['subtext']).pack(anchor='w')

    def _fila_prof(self, p: dict, row: int):
        f = ctk.CTkFrame(self._lista_pr, fg_color=self.C['base'],
                         corner_radius=8, border_width=1, border_color=self.C['border'])
        f.grid(row=row, column=0, pady=3, sticky='ew')

        inner = ctk.CTkFrame(f, fg_color='transparent')
        inner.pack(fill='both', expand=True, padx=12, pady=8)

        top = ctk.CTkFrame(inner, fg_color='transparent')
        top.pack(fill='x')
        ctk.CTkLabel(top, text=p['nombre'],
                     font=ctk.CTkFont(size=13, weight='bold'),
                     text_color=self.C['text']).pack(side='left')
        ctk.CTkButton(top, text='Editar', width=54, height=22, corner_radius=5,
                      fg_color=self.C['surface1'], hover_color=self.C['surface2'],
                      text_color=self.C['subtext'], font=ctk.CTkFont(size=10),
                      command=lambda pp=p: self._editar_prof(pp)).pack(side='right')

        ctk.CTkLabel(inner,
                     text=f"{p['especialidad'] or 'General'} · {p['horario_inicio']}–{p['horario_fin']}",
                     font=ctk.CTkFont(size=11), text_color=self.C['subtext']).pack(anchor='w')

    def _nuevo_servicio(self):
        _FormServicio(self, self.C, on_save=self.refrescar)

    def _editar_servicio(self, s: dict):
        _FormServicio(self, self.C, servicio=s, on_save=self.refrescar)

    def _nuevo_prof(self):
        _FormProfesional(self, self.C, on_save=self.refrescar)

    def _editar_prof(self, p: dict):
        _FormProfesional(self, self.C, profesional=p, on_save=self.refrescar)


class _FormServicio(ctk.CTkToplevel):
    def __init__(self, master, C, servicio=None, on_save=None):
        super().__init__(master)
        self.C = C
        self._sv = servicio
        self._on_save = on_save
        self._color = servicio['color'] if servicio else COLORES[0]
        self.title('Servicio')
        self.geometry('380x380')
        self.configure(fg_color=C['base'])
        self.grab_set()
        self.resizable(False, False)
        self.after(10, lambda: self.geometry(
            f'+{self.master.winfo_rootx()+self.master.winfo_width()//2-190}+'
            f'{self.master.winfo_rooty()+self.master.winfo_height()//2-190}'))
        self._build()

    def _build(self):
        ctk.CTkFrame(self, fg_color=self.C['blue'], height=3).pack(fill='x')
        body = ctk.CTkFrame(self, fg_color='transparent')
        body.pack(fill='both', expand=True, padx=20, pady=16)

        def field(lbl, ph=''):
            ctk.CTkLabel(body, text=lbl, font=ctk.CTkFont(size=11, weight='bold'),
                         text_color=self.C['subtext']).pack(anchor='w', pady=(8, 2))
            e = ctk.CTkEntry(body, placeholder_text=ph, height=34, corner_radius=8,
                             fg_color=self.C['surface0'], border_color=self.C['border'],
                             border_width=1, text_color=self.C['text'],
                             placeholder_text_color=self.C['overlay0'],
                             font=ctk.CTkFont(size=13))
            e.pack(fill='x')
            return e

        self._e_nombre = field('Nombre del servicio', 'ej: Corte de cabello')
        row = ctk.CTkFrame(body, fg_color='transparent')
        row.pack(fill='x')
        c1 = ctk.CTkFrame(row, fg_color='transparent')
        c1.pack(side='left', expand=True, fill='x', padx=(0, 6))
        c2 = ctk.CTkFrame(row, fg_color='transparent')
        c2.pack(side='left', expand=True, fill='x')

        ctk.CTkLabel(c1, text='Duración (min)', font=ctk.CTkFont(size=11, weight='bold'),
                     text_color=self.C['subtext']).pack(anchor='w', pady=(8, 2))
        self._e_dur = ctk.CTkEntry(c1, placeholder_text='30', height=34, corner_radius=8,
                                    fg_color=self.C['surface0'], border_color=self.C['border'],
                                    border_width=1, text_color=self.C['text'],
                                    font=ctk.CTkFont(size=13))
        self._e_dur.pack(fill='x')

        ctk.CTkLabel(c2, text='Precio ($)', font=ctk.CTkFont(size=11, weight='bold'),
                     text_color=self.C['subtext']).pack(anchor='w', pady=(8, 2))
        self._e_precio = ctk.CTkEntry(c2, placeholder_text='0.00', height=34, corner_radius=8,
                                       fg_color=self.C['surface0'], border_color=self.C['border'],
                                       border_width=1, text_color=self.C['text'],
                                       font=ctk.CTkFont(size=13))
        self._e_precio.pack(fill='x')

        ctk.CTkLabel(body, text='Color', font=ctk.CTkFont(size=11, weight='bold'),
                     text_color=self.C['subtext']).pack(anchor='w', pady=(8, 4))
        paleta = ctk.CTkFrame(body, fg_color='transparent')
        paleta.pack(anchor='w')
        self._color_btns = []
        for col in COLORES:
            b = ctk.CTkButton(paleta, text='', width=28, height=28, corner_radius=14,
                              fg_color=col, hover_color=col,
                              command=lambda c=col: self._sel_color(c))
            b.pack(side='left', padx=3)
            self._color_btns.append((b, col))

        if self._sv:
            self._e_nombre.insert(0, self._sv['nombre'])
            self._e_dur.insert(0, str(self._sv['duracion_min']))
            self._e_precio.insert(0, str(self._sv['precio']))

        btn_row = ctk.CTkFrame(body, fg_color='transparent')
        btn_row.pack(fill='x', pady=(16, 0))
        ctk.CTkButton(btn_row, text='Guardar', width=120, height=34, corner_radius=8,
                      fg_color=self.C['green'], hover_color=self.C['teal'], text_color='#000000',
                      font=ctk.CTkFont(size=13, weight='bold'),
                      command=self._guardar).pack(side='left')
        ctk.CTkButton(btn_row, text='Cancelar', width=90, height=34, corner_radius=8,
                      fg_color='transparent', hover_color=self.C['surface1'],
                      border_width=1, border_color=self.C['border'], text_color=self.C['subtext'],
                      font=ctk.CTkFont(size=13), command=self.destroy).pack(side='left', padx=8)

    def _sel_color(self, color: str):
        self._color = color

    def _guardar(self):
        nombre = self._e_nombre.get().strip()
        if not nombre:
            messagebox.showerror('Error', 'El nombre es obligatorio.', parent=self)
            return
        try:
            dur = int(self._e_dur.get() or 30)
            precio = float(self._e_precio.get() or 0)
        except ValueError:
            messagebox.showerror('Error', 'Duración y precio deben ser números.', parent=self)
            return
        if self._sv:
            db.actualizar_servicio(self._sv['id'], nombre, dur, precio, self._color)
        else:
            db.crear_servicio(nombre, dur, precio, self._color)
        if self._on_save:
            self._on_save()
        self.destroy()


class _FormProfesional(ctk.CTkToplevel):
    def __init__(self, master, C, profesional=None, on_save=None):
        super().__init__(master)
        self.C = C
        self._pr = profesional
        self._on_save = on_save
        self.title('Profesional')
        self.geometry('380x320')
        self.configure(fg_color=C['base'])
        self.grab_set()
        self.resizable(False, False)
        self.after(10, lambda: self.geometry(
            f'+{self.master.winfo_rootx()+self.master.winfo_width()//2-190}+'
            f'{self.master.winfo_rooty()+self.master.winfo_height()//2-160}'))
        self._build()

    def _build(self):
        HORAS = [f'{h:02d}:00' for h in range(6, 22)]
        ctk.CTkFrame(self, fg_color=self.C['blue'], height=3).pack(fill='x')
        body = ctk.CTkFrame(self, fg_color='transparent')
        body.pack(fill='both', expand=True, padx=20, pady=16)

        def field(lbl, ph=''):
            ctk.CTkLabel(body, text=lbl, font=ctk.CTkFont(size=11, weight='bold'),
                         text_color=self.C['subtext']).pack(anchor='w', pady=(8, 2))
            e = ctk.CTkEntry(body, placeholder_text=ph, height=34, corner_radius=8,
                             fg_color=self.C['surface0'], border_color=self.C['border'],
                             border_width=1, text_color=self.C['text'],
                             placeholder_text_color=self.C['overlay0'],
                             font=ctk.CTkFont(size=13))
            e.pack(fill='x')
            return e

        self._e_nombre = field('Nombre completo', 'Dr. Juan Pérez')
        self._e_esp    = field('Especialidad', 'General, Odontología, Estética...')

        row = ctk.CTkFrame(body, fg_color='transparent')
        row.pack(fill='x')
        c1 = ctk.CTkFrame(row, fg_color='transparent')
        c1.pack(side='left', expand=True, fill='x', padx=(0, 6))
        c2 = ctk.CTkFrame(row, fg_color='transparent')
        c2.pack(side='left', expand=True, fill='x')

        ctk.CTkLabel(c1, text='Horario inicio', font=ctk.CTkFont(size=11, weight='bold'),
                     text_color=self.C['subtext']).pack(anchor='w', pady=(8, 2))
        self._combo_ini = ctk.CTkComboBox(c1, values=HORAS,
                                           fg_color=self.C['surface0'], border_color=self.C['border'],
                                           button_color=self.C['surface1'], text_color=self.C['text'],
                                           dropdown_fg_color=self.C['surface0'],
                                           dropdown_text_color=self.C['text'],
                                           font=ctk.CTkFont(size=13))
        self._combo_ini.pack(fill='x')

        ctk.CTkLabel(c2, text='Horario fin', font=ctk.CTkFont(size=11, weight='bold'),
                     text_color=self.C['subtext']).pack(anchor='w', pady=(8, 2))
        self._combo_fin = ctk.CTkComboBox(c2, values=HORAS,
                                           fg_color=self.C['surface0'], border_color=self.C['border'],
                                           button_color=self.C['surface1'], text_color=self.C['text'],
                                           dropdown_fg_color=self.C['surface0'],
                                           dropdown_text_color=self.C['text'],
                                           font=ctk.CTkFont(size=13))
        self._combo_fin.pack(fill='x')

        if self._pr:
            self._e_nombre.insert(0, self._pr['nombre'])
            self._e_esp.insert(0, self._pr['especialidad'] or '')
            self._combo_ini.set(self._pr['horario_inicio'])
            self._combo_fin.set(self._pr['horario_fin'])
        else:
            self._combo_ini.set('08:00')
            self._combo_fin.set('18:00')

        btn_row = ctk.CTkFrame(body, fg_color='transparent')
        btn_row.pack(fill='x', pady=(16, 0))
        ctk.CTkButton(btn_row, text='Guardar', width=120, height=34, corner_radius=8,
                      fg_color=self.C['green'], hover_color=self.C['teal'], text_color='#000000',
                      font=ctk.CTkFont(size=13, weight='bold'),
                      command=self._guardar).pack(side='left')
        ctk.CTkButton(btn_row, text='Cancelar', width=90, height=34, corner_radius=8,
                      fg_color='transparent', hover_color=self.C['surface1'],
                      border_width=1, border_color=self.C['border'], text_color=self.C['subtext'],
                      font=ctk.CTkFont(size=13), command=self.destroy).pack(side='left', padx=8)

    def _guardar(self):
        nombre = self._e_nombre.get().strip()
        if not nombre:
            messagebox.showerror('Error', 'El nombre es obligatorio.', parent=self)
            return
        if self._pr:
            db.actualizar_profesional(self._pr['id'], nombre, self._e_esp.get().strip(),
                                      self._combo_ini.get(), self._combo_fin.get())
        else:
            db.crear_profesional(nombre, self._e_esp.get().strip(),
                                 self._combo_ini.get(), self._combo_fin.get())
        if self._on_save:
            self._on_save()
        self.destroy()
