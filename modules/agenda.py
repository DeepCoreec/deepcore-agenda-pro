"""
Agenda — Vista semanal y formulario de nueva cita
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from datetime import date, datetime, timedelta
import database as db


ESTADOS = ['pendiente', 'confirmada', 'completada', 'cancelada', 'no_asistio']
ESTADO_LABELS = {
    'pendiente': 'Pendiente', 'confirmada': 'Confirmada',
    'completada': 'Completada', 'cancelada': 'Cancelada', 'no_asistio': 'No asistió'
}
HORAS = [f'{h:02d}:{m:02d}' for h in range(7, 21) for m in (0, 30)]


class AgendaPanel(ctk.CTkFrame):
    def __init__(self, parent, C: dict):
        super().__init__(parent, fg_color='transparent')
        self.C = C
        self._semana_inicio = self._lunes_actual()
        self._build()
        self.refrescar()

    def _lunes_actual(self) -> date:
        hoy = date.today()
        return hoy - timedelta(days=hoy.weekday())

    def _build(self):
        # Cabecera
        hdr = ctk.CTkFrame(self, fg_color='transparent')
        hdr.pack(fill='x', padx=24, pady=(20, 0))
        ctk.CTkLabel(hdr, text='Agenda',
                     font=ctk.CTkFont(size=22, weight='bold'),
                     text_color=self.C['heading']).pack(side='left')

        ctk.CTkButton(hdr, text='Nueva cita', width=110, height=32,
                      corner_radius=8, fg_color=self.C['green'],
                      hover_color=self.C['teal'], text_color='#000000',
                      font=ctk.CTkFont(size=13, weight='bold'),
                      command=self._nueva_cita).pack(side='right')

        # Navegación de semana
        nav = ctk.CTkFrame(hdr, fg_color='transparent')
        nav.pack(side='right', padx=12)
        ctk.CTkButton(nav, text='<', width=32, height=32, corner_radius=8,
                      fg_color=self.C['surface0'], hover_color=self.C['surface1'],
                      text_color=self.C['text'],
                      command=lambda: self._navegar(-7)).pack(side='left')
        self._lbl_semana = ctk.CTkLabel(nav, text='', font=ctk.CTkFont(size=12),
                                         text_color=self.C['subtext'], width=140)
        self._lbl_semana.pack(side='left', padx=6)
        ctk.CTkButton(nav, text='>', width=32, height=32, corner_radius=8,
                      fg_color=self.C['surface0'], hover_color=self.C['surface1'],
                      text_color=self.C['text'],
                      command=lambda: self._navegar(7)).pack(side='left')
        ctk.CTkButton(nav, text='Hoy', width=50, height=32, corner_radius=8,
                      fg_color=self.C['surface0'], hover_color=self.C['surface1'],
                      text_color=self.C['text'],
                      command=self._ir_hoy).pack(side='left', padx=(4, 0))

        ctk.CTkFrame(self, fg_color=self.C['border'], height=1).pack(fill='x', padx=24, pady=10)

        # Grid de la semana
        self._grid_frame = ctk.CTkScrollableFrame(self, fg_color='transparent')
        self._grid_frame.pack(fill='both', expand=True, padx=24, pady=(0, 16))

    def _navegar(self, dias: int):
        self._semana_inicio += timedelta(days=dias)
        self.refrescar()

    def _ir_hoy(self):
        self._semana_inicio = self._lunes_actual()
        self.refrescar()

    def refrescar(self):
        for w in self._grid_frame.winfo_children():
            w.destroy()

        dias = [self._semana_inicio + timedelta(days=i) for i in range(7)]
        hoy = date.today()
        fin_semana = self._semana_inicio + timedelta(days=6)
        self._lbl_semana.configure(
            text=f'{self._semana_inicio.strftime("%d %b")} – {fin_semana.strftime("%d %b %Y")}')

        citas = db.citas_semana(self._semana_inicio.isoformat())
        citas_por_dia: dict[str, list] = {}
        for c in citas:
            citas_por_dia.setdefault(c['fecha'], []).append(dict(c))

        DIAS_ES = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        self._grid_frame.columnconfigure(0, weight=0, minsize=50)
        for i in range(7):
            self._grid_frame.columnconfigure(i + 1, weight=1, uniform='day')

        # Encabezados de día
        for col, d in enumerate(dias):
            es_hoy = (d == hoy)
            bg = self.C['blue'] if es_hoy else self.C['surface0']
            tc = '#000000' if es_hoy else self.C['text']
            f = ctk.CTkFrame(self._grid_frame, fg_color=bg, corner_radius=8,
                             border_width=1, border_color=self.C['border'])
            f.grid(row=0, column=col + 1, padx=2, pady=(0, 6), sticky='ew')
            ctk.CTkLabel(f, text=DIAS_ES[col],
                         font=ctk.CTkFont(size=10), text_color=tc).pack()
            ctk.CTkLabel(f, text=d.strftime('%d'),
                         font=ctk.CTkFont(size=16, weight='bold'), text_color=tc).pack()

        # Franjas horarias
        horas_display = [f'{h:02d}:00' for h in range(8, 20)]
        for fila, hora in enumerate(horas_display):
            # Etiqueta de hora
            ctk.CTkLabel(self._grid_frame, text=hora,
                         font=ctk.CTkFont(size=10), text_color=self.C['overlay0'],
                         width=44).grid(row=fila + 1, column=0, padx=(0, 4), pady=1, sticky='n')
            # Celda de cada día
            for col, d in enumerate(dias):
                fecha_str = d.isoformat()
                citas_hora = [c for c in citas_por_dia.get(fecha_str, [])
                              if c['hora_inicio'][:2] == hora[:2]]
                bg = self.C['surface0'] if (fila % 2 == 0) else self.C['crust'] if hasattr(self.C, 'crust') else self.C['mantle']
                celda = ctk.CTkFrame(self._grid_frame, fg_color=self.C['surface0'],
                                     corner_radius=4, border_width=1,
                                     border_color=self.C['border'], height=44)
                celda.grid(row=fila + 1, column=col + 1, padx=2, pady=1, sticky='nsew')
                celda.grid_propagate(False)
                for cita in citas_hora[:2]:
                    color = cita.get('servicio_color') or self.C['blue']
                    cb = ctk.CTkButton(celda,
                                       text=f"{cita['hora_inicio']} {cita['cliente_nombre'] or ''}",
                                       font=ctk.CTkFont(size=9),
                                       fg_color=color, hover_color=color,
                                       text_color='#FFFFFF', height=20, corner_radius=4,
                                       anchor='w',
                                       command=lambda c=cita: self._ver_cita(c))
                    cb.pack(fill='x', padx=2, pady=1)

    def _nueva_cita(self):
        _FormularioCita(self, self.C, on_save=self.refrescar)

    def _ver_cita(self, cita: dict):
        _FormularioCita(self, self.C, cita=cita, on_save=self.refrescar)


class _FormularioCita(ctk.CTkToplevel):
    def __init__(self, master, C: dict, cita: dict = None, on_save=None):
        super().__init__(master)
        self.C = C
        self._cita = cita
        self._on_save = on_save
        self.title('Nueva cita' if not cita else 'Editar cita')
        self.geometry('500x580')
        self.configure(fg_color=C['base'])
        self.grab_set()
        self.resizable(False, False)
        self.after(10, self._centrar)
        self._build()

    def _centrar(self):
        self.update_idletasks()
        x = self.master.winfo_rootx() + (self.master.winfo_width() // 2) - 250
        y = self.master.winfo_rooty() + (self.master.winfo_height() // 2) - 290
        self.geometry(f'+{x}+{y}')

    def _entry(self, parent, placeholder='', width=200):
        return ctk.CTkEntry(parent, placeholder_text=placeholder, width=width,
                            fg_color=self.C['surface0'], border_color=self.C['border'],
                            border_width=1, text_color=self.C['text'],
                            placeholder_text_color=self.C['overlay0'],
                            font=ctk.CTkFont(size=13))

    def _label(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=11, weight='bold'),
                     text_color=self.C['subtext']).pack(anchor='w', pady=(10, 2))

    def _build(self):
        ctk.CTkFrame(self, fg_color=self.C['blue'], height=3, corner_radius=0).pack(fill='x')
        body = ctk.CTkScrollableFrame(self, fg_color='transparent')
        body.pack(fill='both', expand=True, padx=24, pady=16)

        ctk.CTkLabel(body, text='Nueva cita' if not self._cita else 'Editar cita',
                     font=ctk.CTkFont(size=18, weight='bold'),
                     text_color=self.C['text']).pack(anchor='w', pady=(0, 16))

        # Cliente
        self._label(body, 'Cliente')
        clientes = db.listar_clientes()
        self._clientes_map = {f"{c['nombre']} {c['apellido']} ({c['telefono'] or 'sin tel.'})": c['id'] for c in clientes}
        self._combo_cliente = ctk.CTkComboBox(body, values=list(self._clientes_map.keys()),
                                               fg_color=self.C['surface0'], border_color=self.C['border'],
                                               button_color=self.C['surface1'], text_color=self.C['text'],
                                               dropdown_fg_color=self.C['surface0'],
                                               dropdown_text_color=self.C['text'],
                                               width=440, font=ctk.CTkFont(size=13))
        self._combo_cliente.pack(fill='x')

        # Servicio
        self._label(body, 'Servicio')
        servicios = db.listar_servicios()
        self._servicios_map = {f"{s['nombre']} ({s['duracion_min']}min — ${s['precio']:.2f})": s['id'] for s in servicios}
        self._combo_servicio = ctk.CTkComboBox(body, values=list(self._servicios_map.keys()),
                                                fg_color=self.C['surface0'], border_color=self.C['border'],
                                                button_color=self.C['surface1'], text_color=self.C['text'],
                                                dropdown_fg_color=self.C['surface0'],
                                                dropdown_text_color=self.C['text'],
                                                width=440, font=ctk.CTkFont(size=13))
        self._combo_servicio.pack(fill='x')

        # Profesional
        self._label(body, 'Profesional')
        profs = db.listar_profesionales()
        self._profs_map = {p['nombre']: p['id'] for p in profs}
        self._profs_map['(Sin asignar)'] = None
        vals_prof = ['(Sin asignar)'] + [p['nombre'] for p in profs]
        self._combo_prof = ctk.CTkComboBox(body, values=vals_prof,
                                            fg_color=self.C['surface0'], border_color=self.C['border'],
                                            button_color=self.C['surface1'], text_color=self.C['text'],
                                            dropdown_fg_color=self.C['surface0'],
                                            dropdown_text_color=self.C['text'],
                                            width=440, font=ctk.CTkFont(size=13))
        self._combo_prof.pack(fill='x')

        # Fecha y hora
        row_dt = ctk.CTkFrame(body, fg_color='transparent')
        row_dt.pack(fill='x', pady=(0, 0))
        col1 = ctk.CTkFrame(row_dt, fg_color='transparent')
        col1.pack(side='left', expand=True, fill='x', padx=(0, 8))
        col2 = ctk.CTkFrame(row_dt, fg_color='transparent')
        col2.pack(side='left', expand=True, fill='x', padx=(0, 8))
        col3 = ctk.CTkFrame(row_dt, fg_color='transparent')
        col3.pack(side='left', expand=True, fill='x')

        self._label(col1, 'Fecha')
        self._entry_fecha = self._entry(col1, 'YYYY-MM-DD')
        self._entry_fecha.pack(fill='x')

        self._label(col2, 'Hora inicio')
        self._combo_inicio = ctk.CTkComboBox(col2, values=HORAS,
                                              fg_color=self.C['surface0'], border_color=self.C['border'],
                                              button_color=self.C['surface1'], text_color=self.C['text'],
                                              dropdown_fg_color=self.C['surface0'],
                                              dropdown_text_color=self.C['text'],
                                              font=ctk.CTkFont(size=13))
        self._combo_inicio.pack(fill='x')

        self._label(col3, 'Hora fin')
        self._combo_fin = ctk.CTkComboBox(col3, values=HORAS,
                                           fg_color=self.C['surface0'], border_color=self.C['border'],
                                           button_color=self.C['surface1'], text_color=self.C['text'],
                                           dropdown_fg_color=self.C['surface0'],
                                           dropdown_text_color=self.C['text'],
                                           font=ctk.CTkFont(size=13))
        self._combo_fin.pack(fill='x')

        # Estado (si editando)
        if self._cita:
            self._label(body, 'Estado')
            self._combo_estado = ctk.CTkComboBox(body,
                                                  values=[ESTADO_LABELS[e] for e in ESTADOS],
                                                  fg_color=self.C['surface0'], border_color=self.C['border'],
                                                  button_color=self.C['surface1'], text_color=self.C['text'],
                                                  dropdown_fg_color=self.C['surface0'],
                                                  dropdown_text_color=self.C['text'],
                                                  width=440, font=ctk.CTkFont(size=13))
            self._combo_estado.pack(fill='x')
            self._combo_estado.set(ESTADO_LABELS.get(self._cita['estado'], 'Pendiente'))

        # Notas
        self._label(body, 'Notas (opcional)')
        self._txt_notas = ctk.CTkTextbox(body, height=70, fg_color=self.C['surface0'],
                                          border_color=self.C['border'], border_width=1,
                                          text_color=self.C['text'], font=ctk.CTkFont(size=13))
        self._txt_notas.pack(fill='x')

        # Pre-llenar si editando
        if self._cita:
            self._entry_fecha.insert(0, self._cita['fecha'])
            self._combo_inicio.set(self._cita['hora_inicio'])
            self._combo_fin.set(self._cita['hora_fin'])
            if self._cita['notas']:
                self._txt_notas.insert('1.0', self._cita['notas'])
        else:
            self._entry_fecha.insert(0, date.today().isoformat())
            self._combo_inicio.set('09:00')
            self._combo_fin.set('09:30')

        # Botones
        btn_row = ctk.CTkFrame(body, fg_color='transparent')
        btn_row.pack(fill='x', pady=(16, 4))
        ctk.CTkButton(btn_row, text='Guardar', width=160, height=38, corner_radius=8,
                      fg_color=self.C['green'], hover_color=self.C['teal'], text_color='#000000',
                      font=ctk.CTkFont(size=13, weight='bold'),
                      command=self._guardar).pack(side='left')
        ctk.CTkButton(btn_row, text='Cancelar', width=100, height=38, corner_radius=8,
                      fg_color='transparent', hover_color=self.C['surface1'],
                      border_width=1, border_color=self.C['border'], text_color=self.C['subtext'],
                      font=ctk.CTkFont(size=13), command=self.destroy).pack(side='left', padx=10)
        if self._cita:
            ctk.CTkButton(btn_row, text='Eliminar', width=100, height=38, corner_radius=8,
                          fg_color='transparent', hover_color=self.C['red'],
                          border_width=1, border_color=self.C['red'], text_color=self.C['red'],
                          font=ctk.CTkFont(size=13), command=self._eliminar).pack(side='right')

    def _guardar(self):
        fecha = self._entry_fecha.get().strip()
        inicio = self._combo_inicio.get()
        fin = self._combo_fin.get()
        cliente_key = self._combo_cliente.get()
        servicio_key = self._combo_servicio.get()
        prof_key = self._combo_prof.get()
        notas = self._txt_notas.get('1.0', 'end').strip()

        if not fecha or not inicio or not fin:
            messagebox.showerror('Error', 'Fecha y hora son obligatorias.', parent=self)
            return

        cliente_id  = self._clientes_map.get(cliente_key)
        servicio_id = self._servicios_map.get(servicio_key)
        prof_id     = self._profs_map.get(prof_key)

        if self._cita:
            db.actualizar_cita(self._cita['id'], cliente_id, servicio_id, prof_id,
                               fecha, inicio, fin, notas)
            # Actualizar estado
            estado_label = self._combo_estado.get()
            estado_key = next((k for k, v in ESTADO_LABELS.items() if v == estado_label), 'pendiente')
            db.actualizar_estado_cita(self._cita['id'], estado_key)
        else:
            db.crear_cita(cliente_id, servicio_id, prof_id, fecha, inicio, fin, notas)

        if self._on_save:
            self._on_save()
        self.destroy()

    def _eliminar(self):
        if messagebox.askyesno('Eliminar cita', '¿Eliminar esta cita?', parent=self):
            db.eliminar_cita(self._cita['id'])
            if self._on_save:
                self._on_save()
            self.destroy()
