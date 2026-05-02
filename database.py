"""
DeepCore Agenda Pro — Base de datos SQLite
"""
import os, sqlite3, sys
from datetime import date, datetime, timedelta

def _db_path() -> str:
    if getattr(sys, 'frozen', False):
        base = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'DeepCore Agenda Pro')
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, 'agenda.db')

DB_PATH = _db_path()

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA foreign_keys=ON')
    return conn

def init_db():
    with get_conn() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS config (
            key   TEXT PRIMARY KEY,
            value TEXT
        );
        CREATE TABLE IF NOT EXISTS clientes (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre    TEXT NOT NULL,
            apellido  TEXT DEFAULT '',
            telefono  TEXT DEFAULT '',
            email     TEXT DEFAULT '',
            notas     TEXT DEFAULT '',
            creado    TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS servicios (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre       TEXT NOT NULL,
            duracion_min INTEGER DEFAULT 30,
            precio       REAL    DEFAULT 0,
            color        TEXT    DEFAULT '#3B82F6',
            activo       INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS profesionales (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre         TEXT NOT NULL,
            especialidad   TEXT DEFAULT '',
            horario_inicio TEXT DEFAULT '08:00',
            horario_fin    TEXT DEFAULT '18:00',
            activo         INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS citas (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id     INTEGER REFERENCES clientes(id) ON DELETE SET NULL,
            servicio_id    INTEGER REFERENCES servicios(id) ON DELETE SET NULL,
            profesional_id INTEGER REFERENCES profesionales(id) ON DELETE SET NULL,
            fecha          TEXT NOT NULL,
            hora_inicio    TEXT NOT NULL,
            hora_fin       TEXT NOT NULL,
            estado         TEXT DEFAULT 'pendiente',
            notas          TEXT DEFAULT '',
            creado         TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE INDEX IF NOT EXISTS idx_citas_fecha ON citas(fecha);
        CREATE INDEX IF NOT EXISTS idx_citas_estado ON citas(estado);
        ''')
        # Datos de muestra si está vacío
        row = c.execute('SELECT COUNT(*) FROM servicios').fetchone()[0]
        if row == 0:
            c.executemany(
                'INSERT INTO servicios (nombre,duracion_min,precio,color) VALUES (?,?,?,?)',
                [
                    ('Consulta general',    30, 20.0, '#3B82F6'),
                    ('Corte de cabello',    45, 12.0, '#22C55E'),
                    ('Limpieza facial',     60, 30.0, '#C084FC'),
                    ('Manicure',            40, 10.0, '#F59E0B'),
                    ('Revisión técnica',    60, 25.0, '#14B8A6'),
                ]
            )
            c.execute(
                'INSERT INTO profesionales (nombre,especialidad) VALUES (?,?)',
                ('Dr. Principal', 'General')
            )

# ── Config ─────────────────────────────────────────────────────────────────────

def get_config(key: str, default: str = '') -> str:
    with get_conn() as c:
        row = c.execute('SELECT value FROM config WHERE key=?', (key,)).fetchone()
        return row['value'] if row else default

def set_config(key: str, value: str):
    with get_conn() as c:
        c.execute('INSERT OR REPLACE INTO config (key,value) VALUES (?,?)', (key, value))

# ── Clientes ───────────────────────────────────────────────────────────────────

def listar_clientes(buscar: str = '') -> list:
    with get_conn() as c:
        if buscar:
            q = f'%{buscar}%'
            return c.execute(
                'SELECT * FROM clientes WHERE nombre LIKE ? OR apellido LIKE ? OR telefono LIKE ? ORDER BY nombre',
                (q, q, q)
            ).fetchall()
        return c.execute('SELECT * FROM clientes ORDER BY nombre').fetchall()

def crear_cliente(nombre, apellido='', telefono='', email='', notas='') -> int:
    with get_conn() as c:
        cur = c.execute(
            'INSERT INTO clientes (nombre,apellido,telefono,email,notas) VALUES (?,?,?,?,?)',
            (nombre, apellido, telefono, email, notas)
        )
        return cur.lastrowid

def actualizar_cliente(id, nombre, apellido, telefono, email, notas):
    with get_conn() as c:
        c.execute(
            'UPDATE clientes SET nombre=?,apellido=?,telefono=?,email=?,notas=? WHERE id=?',
            (nombre, apellido, telefono, email, notas, id)
        )

def eliminar_cliente(id: int):
    with get_conn() as c:
        c.execute('DELETE FROM clientes WHERE id=?', (id,))

# ── Servicios ──────────────────────────────────────────────────────────────────

def listar_servicios(solo_activos=True) -> list:
    with get_conn() as c:
        if solo_activos:
            return c.execute('SELECT * FROM servicios WHERE activo=1 ORDER BY nombre').fetchall()
        return c.execute('SELECT * FROM servicios ORDER BY nombre').fetchall()

def crear_servicio(nombre, duracion_min=30, precio=0.0, color='#3B82F6') -> int:
    with get_conn() as c:
        cur = c.execute(
            'INSERT INTO servicios (nombre,duracion_min,precio,color) VALUES (?,?,?,?)',
            (nombre, duracion_min, precio, color)
        )
        return cur.lastrowid

def actualizar_servicio(id, nombre, duracion_min, precio, color, activo=1):
    with get_conn() as c:
        c.execute(
            'UPDATE servicios SET nombre=?,duracion_min=?,precio=?,color=?,activo=? WHERE id=?',
            (nombre, duracion_min, precio, color, activo, id)
        )

# ── Profesionales ──────────────────────────────────────────────────────────────

def listar_profesionales(solo_activos=True) -> list:
    with get_conn() as c:
        if solo_activos:
            return c.execute('SELECT * FROM profesionales WHERE activo=1 ORDER BY nombre').fetchall()
        return c.execute('SELECT * FROM profesionales ORDER BY nombre').fetchall()

def crear_profesional(nombre, especialidad='', inicio='08:00', fin='18:00') -> int:
    with get_conn() as c:
        cur = c.execute(
            'INSERT INTO profesionales (nombre,especialidad,horario_inicio,horario_fin) VALUES (?,?,?,?)',
            (nombre, especialidad, inicio, fin)
        )
        return cur.lastrowid

def actualizar_profesional(id, nombre, especialidad, inicio, fin, activo=1):
    with get_conn() as c:
        c.execute(
            'UPDATE profesionales SET nombre=?,especialidad=?,horario_inicio=?,horario_fin=?,activo=? WHERE id=?',
            (nombre, especialidad, inicio, fin, activo, id)
        )

# ── Citas ──────────────────────────────────────────────────────────────────────

def listar_citas(fecha: str = None, estado: str = None) -> list:
    with get_conn() as c:
        q = '''
        SELECT ci.*,
               cl.nombre || ' ' || cl.apellido AS cliente_nombre,
               cl.telefono AS cliente_tel,
               se.nombre AS servicio_nombre, se.color AS servicio_color,
               pr.nombre AS profesional_nombre
        FROM citas ci
        LEFT JOIN clientes cl ON ci.cliente_id = cl.id
        LEFT JOIN servicios se ON ci.servicio_id = se.id
        LEFT JOIN profesionales pr ON ci.profesional_id = pr.id
        WHERE 1=1
        '''
        params = []
        if fecha:
            q += ' AND ci.fecha = ?'
            params.append(fecha)
        if estado:
            q += ' AND ci.estado = ?'
            params.append(estado)
        q += ' ORDER BY ci.fecha, ci.hora_inicio'
        return c.execute(q, params).fetchall()

def citas_semana(fecha_inicio: str) -> list:
    d = datetime.strptime(fecha_inicio, '%Y-%m-%d')
    fin = (d + timedelta(days=6)).strftime('%Y-%m-%d')
    with get_conn() as c:
        return c.execute('''
        SELECT ci.*,
               cl.nombre || ' ' || cl.apellido AS cliente_nombre,
               se.nombre AS servicio_nombre, se.color AS servicio_color,
               pr.nombre AS profesional_nombre
        FROM citas ci
        LEFT JOIN clientes cl ON ci.cliente_id = cl.id
        LEFT JOIN servicios se ON ci.servicio_id = se.id
        LEFT JOIN profesionales pr ON ci.profesional_id = pr.id
        WHERE ci.fecha BETWEEN ? AND ?
        ORDER BY ci.fecha, ci.hora_inicio
        ''', (fecha_inicio, fin)).fetchall()

def crear_cita(cliente_id, servicio_id, profesional_id, fecha, hora_inicio, hora_fin, notas='') -> int:
    with get_conn() as c:
        cur = c.execute(
            'INSERT INTO citas (cliente_id,servicio_id,profesional_id,fecha,hora_inicio,hora_fin,notas) VALUES (?,?,?,?,?,?,?)',
            (cliente_id, servicio_id, profesional_id, fecha, hora_inicio, hora_fin, notas)
        )
        return cur.lastrowid

def actualizar_estado_cita(id: int, estado: str):
    with get_conn() as c:
        c.execute('UPDATE citas SET estado=? WHERE id=?', (estado, id))

def actualizar_cita(id, cliente_id, servicio_id, profesional_id, fecha, hora_inicio, hora_fin, notas):
    with get_conn() as c:
        c.execute(
            'UPDATE citas SET cliente_id=?,servicio_id=?,profesional_id=?,fecha=?,hora_inicio=?,hora_fin=?,notas=? WHERE id=?',
            (cliente_id, servicio_id, profesional_id, fecha, hora_inicio, hora_fin, notas, id)
        )

def eliminar_cita(id: int):
    with get_conn() as c:
        c.execute('DELETE FROM citas WHERE id=?', (id,))

# ── KPIs / Dashboard ──────────────────────────────────────────────────────────

def kpis_hoy() -> dict:
    hoy = date.today().isoformat()
    with get_conn() as c:
        total_hoy = c.execute("SELECT COUNT(*) FROM citas WHERE fecha=?", (hoy,)).fetchone()[0]
        completadas_hoy = c.execute("SELECT COUNT(*) FROM citas WHERE fecha=? AND estado='completada'", (hoy,)).fetchone()[0]
        pendientes_hoy = c.execute("SELECT COUNT(*) FROM citas WHERE fecha=? AND estado IN ('pendiente','confirmada')", (hoy,)).fetchone()[0]
        ingreso_hoy = c.execute("""
            SELECT COALESCE(SUM(s.precio),0)
            FROM citas ci JOIN servicios s ON ci.servicio_id=s.id
            WHERE ci.fecha=? AND ci.estado='completada'
        """, (hoy,)).fetchone()[0]
        total_clientes = c.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
        mes = hoy[:7]
        ingreso_mes = c.execute("""
            SELECT COALESCE(SUM(s.precio),0)
            FROM citas ci JOIN servicios s ON ci.servicio_id=s.id
            WHERE ci.fecha LIKE ? AND ci.estado='completada'
        """, (f'{mes}%',)).fetchone()[0]
    return {
        'citas_hoy': total_hoy,
        'completadas': completadas_hoy,
        'pendientes': pendientes_hoy,
        'ingreso_hoy': round(ingreso_hoy, 2),
        'total_clientes': total_clientes,
        'ingreso_mes': round(ingreso_mes, 2),
    }

init_db()
