"""
Clientes — Gestión de base de clientes
"""
import customtkinter as ctk
from tkinter import messagebox
import database as db


class ClientesPanel(ctk.CTkFrame):
    def __init__(self, parent, C: dict):
        super().__init__(parent, fg_color='transparent')
        self.C = C
        self._build()
        self.refrescar()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color='transparent')
        hdr.pack(fill='x', padx=24, pady=(20, 0))
        ctk.CTkLabel(hdr, text='Clientes',
                     font=ctk.CTkFont(size=22, weight='bold'),
                     text_color=self.C['heading']).pack(side='left')
        ctk.CTkButton(hdr, text='Nuevo cliente', width=130, height=32,
                      corner_radius=8, fg_color=self.C['green'],
                      hover_color=self.C['teal'], text_color='#000000',
                      font=ctk.CTkFont(size=13, weight='bold'),
                      command=self._nuevo).pack(side='right')

        # Búsqueda
        barra = ctk.CTkFrame(self, fg_color='transparent')
        barra.pack(fill='x', padx=24, pady=10)
        self._entry_buscar = ctk.CTkEntry(barra, placeholder_text='Buscar por nombre o teléfono...',
                                          height=36, corner_radius=8,
                                          fg_color=self.C['surface0'], border_color=self.C['border'],
                                          border_width=1, text_color=self.C['text'],
                                          placeholder_text_color=self.C['overlay0'],
                                          font=ctk.CTkFont(size=13))
        self._entry_buscar.pack(side='left', fill='x', expand=True)
        self._entry_buscar.bind('<KeyRelease>', lambda e: self.refrescar())
        ctk.CTkFrame(self, fg_color=self.C['border'], height=1).pack(fill='x', padx=24)

        # Lista
        self._lista = ctk.CTkScrollableFrame(self, fg_color='transparent')
        self._lista.pack(fill='both', expand=True, padx=24, pady=12)
        self._lista.columnconfigure(0, weight=1)

    def refrescar(self):
        for w in self._lista.winfo_children():
            w.destroy()
        buscar = self._entry_buscar.get().strip()
        clientes = db.listar_clientes(buscar)
        if not clientes:
            ctk.CTkLabel(self._lista, text='Sin clientes registrados.',
                         font=ctk.CTkFont(size=13), text_color=self.C['overlay0']).grid(row=0, column=0, pady=30)
            return
        for i, c in enumerate(clientes):
            self._fila(dict(c), i)

    def _fila(self, c: dict, row: int):
        f = ctk.CTkFrame(self._lista, fg_color=self.C['surface0'],
                         corner_radius=10, border_width=1, border_color=self.C['border'])
        f.grid(row=row, column=0, pady=4, sticky='ew')

        inner = ctk.CTkFrame(f, fg_color='transparent')
        inner.pack(fill='both', expand=True, padx=14, pady=10)

        top = ctk.CTkFrame(inner, fg_color='transparent')
        top.pack(fill='x')
        nombre = f"{c['nombre']} {c['apellido']}".strip()
        ctk.CTkLabel(top, text=nombre,
                     font=ctk.CTkFont(size=14, weight='bold'),
                     text_color=self.C['text']).pack(side='left')
        ctk.CTkButton(top, text='Editar', width=64, height=26, corner_radius=6,
                      fg_color=self.C['surface1'], hover_color=self.C['surface2'],
                      text_color=self.C['text'], font=ctk.CTkFont(size=11),
                      command=lambda cc=c: self._editar(cc)).pack(side='right')

        datos = ctk.CTkFrame(inner, fg_color='transparent')
        datos.pack(fill='x', pady=(2, 0))
        if c['telefono']:
            ctk.CTkLabel(datos, text=c['telefono'],
                         font=ctk.CTkFont(size=12), text_color=self.C['subtext']).pack(side='left')
        if c['email']:
            ctk.CTkLabel(datos, text=f"  ·  {c['email']}",
                         font=ctk.CTkFont(size=12), text_color=self.C['overlay0']).pack(side='left')

    def _nuevo(self):
        _FormCliente(self, self.C, on_save=self.refrescar)

    def _editar(self, c: dict):
        _FormCliente(self, self.C, cliente=c, on_save=self.refrescar)


class _FormCliente(ctk.CTkToplevel):
    def __init__(self, master, C: dict, cliente: dict = None, on_save=None):
        super().__init__(master)
        self.C = C
        self._cliente = cliente
        self._on_save = on_save
        self.title('Nuevo cliente' if not cliente else 'Editar cliente')
        self.geometry('420x440')
        self.configure(fg_color=C['base'])
        self.grab_set()
        self.resizable(False, False)
        self.after(10, self._centrar)
        self._build()

    def _centrar(self):
        self.update_idletasks()
        x = self.master.winfo_rootx() + (self.master.winfo_width() // 2) - 210
        y = self.master.winfo_rooty() + (self.master.winfo_height() // 2) - 220
        self.geometry(f'+{x}+{y}')

    def _field(self, parent, label, placeholder=''):
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=11, weight='bold'),
                     text_color=self.C['subtext']).pack(anchor='w', pady=(10, 2))
        e = ctk.CTkEntry(parent, placeholder_text=placeholder, height=36, corner_radius=8,
                         fg_color=self.C['surface0'], border_color=self.C['border'],
                         border_width=1, text_color=self.C['text'],
                         placeholder_text_color=self.C['overlay0'],
                         font=ctk.CTkFont(size=13))
        e.pack(fill='x')
        return e

    def _build(self):
        ctk.CTkFrame(self, fg_color=self.C['green'], height=3, corner_radius=0).pack(fill='x')
        body = ctk.CTkFrame(self, fg_color='transparent')
        body.pack(fill='both', expand=True, padx=24, pady=16)

        ctk.CTkLabel(body, text='Nuevo cliente' if not self._cliente else 'Editar cliente',
                     font=ctk.CTkFont(size=17, weight='bold'),
                     text_color=self.C['text']).pack(anchor='w', pady=(0, 6))

        row = ctk.CTkFrame(body, fg_color='transparent')
        row.pack(fill='x')
        col1 = ctk.CTkFrame(row, fg_color='transparent')
        col1.pack(side='left', expand=True, fill='x', padx=(0, 6))
        col2 = ctk.CTkFrame(row, fg_color='transparent')
        col2.pack(side='left', expand=True, fill='x')
        self._e_nombre   = self._field(col1, 'Nombre', 'Nombre')
        self._e_apellido = self._field(col2, 'Apellido', 'Apellido')
        self._e_tel      = self._field(body, 'Teléfono', '0991234567')
        self._e_email    = self._field(body, 'Email', 'correo@ejemplo.com')

        ctk.CTkLabel(body, text='Notas', font=ctk.CTkFont(size=11, weight='bold'),
                     text_color=self.C['subtext']).pack(anchor='w', pady=(10, 2))
        self._txt_notas = ctk.CTkTextbox(body, height=60, fg_color=self.C['surface0'],
                                          border_color=self.C['border'], border_width=1,
                                          text_color=self.C['text'], font=ctk.CTkFont(size=13))
        self._txt_notas.pack(fill='x')

        if self._cliente:
            self._e_nombre.insert(0, self._cliente['nombre'])
            self._e_apellido.insert(0, self._cliente['apellido'] or '')
            self._e_tel.insert(0, self._cliente['telefono'] or '')
            self._e_email.insert(0, self._cliente['email'] or '')
            if self._cliente['notas']:
                self._txt_notas.insert('1.0', self._cliente['notas'])

        btn_row = ctk.CTkFrame(body, fg_color='transparent')
        btn_row.pack(fill='x', pady=(14, 0))
        ctk.CTkButton(btn_row, text='Guardar', width=140, height=36, corner_radius=8,
                      fg_color=self.C['green'], hover_color=self.C['teal'], text_color='#000000',
                      font=ctk.CTkFont(size=13, weight='bold'),
                      command=self._guardar).pack(side='left')
        ctk.CTkButton(btn_row, text='Cancelar', width=90, height=36, corner_radius=8,
                      fg_color='transparent', hover_color=self.C['surface1'],
                      border_width=1, border_color=self.C['border'], text_color=self.C['subtext'],
                      font=ctk.CTkFont(size=13), command=self.destroy).pack(side='left', padx=8)
        if self._cliente:
            ctk.CTkButton(btn_row, text='Eliminar', width=90, height=36, corner_radius=8,
                          fg_color='transparent', hover_color=self.C['red'],
                          border_width=1, border_color=self.C['red'], text_color=self.C['red'],
                          font=ctk.CTkFont(size=13), command=self._eliminar).pack(side='right')

    def _guardar(self):
        nombre = self._e_nombre.get().strip()
        if not nombre:
            messagebox.showerror('Error', 'El nombre es obligatorio.', parent=self)
            return
        kwargs = dict(
            nombre=nombre,
            apellido=self._e_apellido.get().strip(),
            telefono=self._e_tel.get().strip(),
            email=self._e_email.get().strip(),
            notas=self._txt_notas.get('1.0', 'end').strip()
        )
        if self._cliente:
            db.actualizar_cliente(self._cliente['id'], **kwargs)
        else:
            db.crear_cliente(**kwargs)
        if self._on_save:
            self._on_save()
        self.destroy()

    def _eliminar(self):
        if messagebox.askyesno('Eliminar', f"¿Eliminar a {self._cliente['nombre']}?", parent=self):
            db.eliminar_cliente(self._cliente['id'])
            if self._on_save:
                self._on_save()
            self.destroy()
