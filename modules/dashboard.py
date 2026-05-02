"""
Dashboard — Vista general de hoy y KPIs
"""
import customtkinter as ctk
from datetime import date, datetime
import database as db


class DashboardPanel(ctk.CTkFrame):
    def __init__(self, parent, C: dict):
        super().__init__(parent, fg_color='transparent')
        self.C = C
        self._build()
        self.refrescar()

    def _build(self):
        # Cabecera
        hdr = ctk.CTkFrame(self, fg_color='transparent')
        hdr.pack(fill='x', padx=24, pady=(20, 0))
        ctk.CTkLabel(hdr, text='Dashboard',
                     font=ctk.CTkFont(size=22, weight='bold'),
                     text_color=self.C['heading']).pack(side='left')
        ctk.CTkLabel(hdr, text='Vista general de hoy',
                     font=ctk.CTkFont(size=12),
                     text_color=self.C['overlay0']).pack(side='left', padx=(12, 0), pady=(6, 0))
        ctk.CTkButton(hdr, text='Actualizar', width=90, height=28,
                      corner_radius=8, fg_color=self.C['surface0'],
                      hover_color=self.C['surface1'], text_color=self.C['text'],
                      font=ctk.CTkFont(size=11), command=self.refrescar).pack(side='right')

        ctk.CTkFrame(self, fg_color=self.C['border'], height=1).pack(fill='x', padx=24, pady=12)

        # KPI cards
        self._frame_kpis = ctk.CTkFrame(self, fg_color='transparent')
        self._frame_kpis.pack(fill='x', padx=24, pady=(0, 16))
        for i in range(4):
            self._frame_kpis.columnconfigure(i, weight=1, uniform='kpi')

        # Citas de hoy
        ctk.CTkLabel(self, text='CITAS DE HOY',
                     font=ctk.CTkFont(size=10, weight='bold'),
                     text_color=self.C['overlay0']).pack(anchor='w', padx=24, pady=(0, 8))

        self._frame_citas = ctk.CTkScrollableFrame(
            self, fg_color='transparent', height=320)
        self._frame_citas.pack(fill='both', expand=True, padx=24, pady=(0, 16))
        self._frame_citas.columnconfigure(0, weight=1)

    def _kpi_card(self, titulo, valor, color, col):
        card = ctk.CTkFrame(self._frame_kpis, fg_color=self.C['surface0'],
                            corner_radius=12, border_width=1, border_color=self.C['border'])
        card.grid(row=0, column=col, padx=6, sticky='nsew')
        ctk.CTkFrame(card, fg_color=color, height=3, corner_radius=0).pack(fill='x')
        inner = ctk.CTkFrame(card, fg_color='transparent')
        inner.pack(fill='both', expand=True, padx=14, pady=10)
        ctk.CTkLabel(inner, text=titulo, font=ctk.CTkFont(size=10),
                     text_color=self.C['subtext']).pack(anchor='w')
        ctk.CTkLabel(inner, text=str(valor), font=ctk.CTkFont(size=28, weight='bold'),
                     text_color=color).pack(anchor='w', pady=(2, 0))

    def _cita_row(self, cita, row):
        color = cita['servicio_color'] or self.C['blue']
        estado_colors = {
            'pendiente': self.C['amber'],
            'confirmada': self.C['blue'],
            'completada': self.C['green'],
            'cancelada': self.C['red'],
            'no_asistio': self.C['overlay0'],
        }
        ec = estado_colors.get(cita['estado'], self.C['subtext'])

        f = ctk.CTkFrame(self._frame_citas, fg_color=self.C['surface0'],
                         corner_radius=10, border_width=1, border_color=self.C['border'])
        f.grid(row=row, column=0, pady=4, sticky='ew')

        # Barra de color del servicio
        ctk.CTkFrame(f, fg_color=color, width=4, corner_radius=0).pack(side='left', fill='y')

        inner = ctk.CTkFrame(f, fg_color='transparent')
        inner.pack(side='left', fill='both', expand=True, padx=12, pady=8)

        row1 = ctk.CTkFrame(inner, fg_color='transparent')
        row1.pack(fill='x')
        ctk.CTkLabel(row1, text=f"{cita['hora_inicio']} – {cita['hora_fin']}",
                     font=ctk.CTkFont(size=13, weight='bold'),
                     text_color=self.C['text']).pack(side='left')
        ctk.CTkLabel(row1, text=cita['estado'].upper(),
                     font=ctk.CTkFont(size=9, weight='bold'),
                     text_color=ec).pack(side='right')

        row2 = ctk.CTkFrame(inner, fg_color='transparent')
        row2.pack(fill='x', pady=(2, 0))
        cliente = cita['cliente_nombre'] or 'Sin cliente'
        servicio = cita['servicio_nombre'] or 'Sin servicio'
        ctk.CTkLabel(row2, text=cliente,
                     font=ctk.CTkFont(size=12, weight='bold'),
                     text_color=self.C['text']).pack(side='left')
        ctk.CTkLabel(row2, text=f'· {servicio}',
                     font=ctk.CTkFont(size=12),
                     text_color=self.C['subtext']).pack(side='left', padx=(6, 0))
        if cita['profesional_nombre']:
            ctk.CTkLabel(row2, text=cita['profesional_nombre'],
                         font=ctk.CTkFont(size=11),
                         text_color=self.C['overlay0']).pack(side='right')

    def refrescar(self):
        for w in self._frame_kpis.winfo_children():
            w.destroy()
        for w in self._frame_citas.winfo_children():
            w.destroy()

        kpis = db.kpis_hoy()
        self._kpi_card('Citas hoy',        kpis['citas_hoy'],      self.C['blue'],   0)
        self._kpi_card('Pendientes',        kpis['pendientes'],     self.C['amber'],  1)
        self._kpi_card('Completadas',       kpis['completadas'],    self.C['green'],  2)
        self._kpi_card(f'Ingresos hoy',    f"${kpis['ingreso_hoy']:.2f}", self.C['teal'], 3)

        hoy = date.today().isoformat()
        citas = db.listar_citas(fecha=hoy)
        if not citas:
            ctk.CTkLabel(self._frame_citas, text='Sin citas programadas para hoy.',
                         font=ctk.CTkFont(size=13), text_color=self.C['overlay0']).grid(row=0, column=0, pady=30)
        else:
            for i, cita in enumerate(citas):
                self._cita_row(dict(cita), i)
