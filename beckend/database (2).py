"""
Camada de acesso ao banco de dados (SQLite via HTTP Server).
Roda na VM do Banco de Dados (Debian) na porta 5001.
"""
import sqlite3
from contextlib import contextmanager
from flask import Flask, jsonify, request

app = Flask(__name__)
DB_PATH = "tarefas.db"

@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()

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

@app.route('/db/query', methods=['POST'])
def executar_query():
    dados = request.get_json()
    sql = dados.get("sql")
    params = dados.get("params", [])
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        
        if sql.strip().upper().startswith("SELECT"):
            rows = [dict(row) for row in cursor.fetchall()]
            return jsonify({"resultado": rows})
        else:
            return jsonify({"lastrowid": cursor.lastrowid, "sucesso": True})

if __name__ == '__main__':
    init_db()
    # Roda na porta 5001 e escuta em toda a rede bridge
    app.run(host='0.0.0.0', port=5001, debug=True)