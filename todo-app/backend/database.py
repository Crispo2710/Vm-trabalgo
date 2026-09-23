"""
Camada de acesso ao banco de dados (SQLite).
Roda na VM do Banco de Dados (Debian).
"""
import sqlite3
from contextlib import contextmanager

DB_PATH = "tarefas.db"


def init_db():
    """Cria as tabelas 'projetos' e 'tarefas' caso não existam."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS projetos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT,
                criado_em TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tarefas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descricao TEXT,
                status TEXT NOT NULL DEFAULT 'pendente',
                prioridade TEXT NOT NULL DEFAULT 'media',
                projeto_id INTEGER,
                criado_em TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (projeto_id) REFERENCES projetos (id) ON DELETE SET NULL
            )
        """)
        conn.commit()


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()
