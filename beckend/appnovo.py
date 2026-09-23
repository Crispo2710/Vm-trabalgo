
"""API RESTful - Gestao de Tarefas/Projetos (VM Debian)."""
import sqlite3
from contextlib import contextmanager
from flask import Flask, jsonify, request
from flask_cors import CORS
from database import init_db, DB_PATH

app = Flask(__name__)
CORS(app)

STATUS_VALIDOS      = {"pendente", "em_andamento", "concluida"}
PRIORIDADES_VALIDAS = {"baixa", "media", "alta"}


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def d(row):
    return None if row is None else dict(zip(row.keys(), row))


def erro(msg, code=400):
    return jsonify({"erro": msg}), code


def valida_sp(status, prioridade):
    if status not in STATUS_VALIDOS:
        return erro(f"status invalido. Use {sorted(STATUS_VALIDOS)}")
    if prioridade not in PRIORIDADES_VALIDAS:
        return erro(f"prioridade invalida. Use {sorted(PRIORIDADES_VALIDAS)}")


def json_body():
    return request.get_json(force=True, silent=True) or {}


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "servico": "backend-api"})


# ---- PROJETOS ----
@app.route("/api/projetos")
def listar_projetos():
    with get_db() as c:
        return jsonify([d(r) for r in c.execute("SELECT * FROM projetos ORDER BY id DESC")])


@app.route("/api/projetos", methods=["POST"])
def criar_projeto():
    dados = json_body()
    if not dados.get("nome"):
        return erro("O campo nome e obrigatorio")
    with get_db() as c:
        novo = c.execute("INSERT INTO projetos (nome, descricao) VALUES (?, ?) RETURNING *",
                         (dados["nome"], dados.get("descricao", ""))).fetchone()
    return jsonify(d(novo)), 201


@app.route("/api/projetos/<int:pid>")
def obter_projeto(pid):
    with get_db() as c:
        row = c.execute("SELECT * FROM projetos WHERE id = ?", (pid,)).fetchone()
    return jsonify(d(row)) if row else erro("Projeto nao encontrado", 404)


@app.route("/api/projetos/<int:pid>", methods=["PUT"])
def atualizar_projeto(pid):
    dados = json_body()
    with get_db() as c:
        ex = c.execute("SELECT * FROM projetos WHERE id = ?", (pid,)).fetchone()
        if not ex:
            return erro("Projeto nao encontrado", 404)
        up = c.execute("UPDATE projetos SET nome = ?, descricao = ? WHERE id = ? RETURNING *",
                       (dados.get("nome", ex["nome"]), dados.get("descricao", ex["descricao"]), pid)).fetchone()
    return jsonify(d(up))


@app.route("/api/projetos/<int:pid>", methods=["DELETE"])
def deletar_projeto(pid):
    with get_db() as c:
        cur = c.execute("DELETE FROM projetos WHERE id = ?", (pid,))
    return jsonify({"mensagem": "Projeto removido com sucesso"}) if cur.rowcount else erro("Projeto nao encontrado", 404)


# ---- TAREFAS ----
@app.route("/api/tarefas")
def listar_tarefas():
    q, p = "SELECT * FROM tarefas WHERE 1=1", []
    if (pid := request.args.get("projeto_id")) is not None:
        try:
            p.append(int(pid)); q += " AND projeto_id = ?"
        except ValueError:
            return erro("projeto_id deve ser inteiro")
    if (st := request.args.get("status")) is not None:
        q += " AND status = ?"; p.append(st)
    try:
        lim = min(int(request.args.get("limite", 50)), 200)
        off = int(request.args.get("offset", 0))
        if lim < 1 or off < 0:
            raise ValueError
    except ValueError:
        return erro("limite e offset devem ser inteiros positivos")
    q += " ORDER BY id DESC LIMIT ? OFFSET ?"; p += [lim, off]
    with get_db() as c:
        return jsonify([d(r) for r in c.execute(q, p)])


@app.route("/api/tarefas", methods=["POST"])
def criar_tarefa():
    dados = json_body()
    if not dados.get("titulo"):
        return erro("O campo titulo e obrigatorio")
    st, pr = dados.get("status", "pendente"), dados.get("prioridade", "media")
    if (err := valida_sp(st, pr)):
        return err
    pid = dados.get("projeto_id")
    with get_db() as c:
        if pid is not None and not c.execute("SELECT 1 FROM projetos WHERE id = ?", (pid,)).fetchone():
            return erro("projeto_id nao existe")
        nova = c.execute("INSERT INTO tarefas (titulo, descricao, status, prioridade, projeto_id) VALUES (?, ?, ?, ?, ?) RETURNING *",
                         (dados["titulo"], dados.get("descricao", ""), st, pr, pid)).fetchone()
    return jsonify(d(nova)), 201


@app.route("/api/tarefas/<int:tid>")
def obter_tarefa(tid):
    with get_db() as c:
        row = c.execute("SELECT * FROM tarefas WHERE id = ?", (tid,)).fetchone()
    return jsonify(d(row)) if row else erro("Tarefa nao encontrada", 404)


@app.route("/api/tarefas/<int:tid>", methods=["PUT"])
def atualizar_tarefa(tid):
    dados = json_body()
    with get_db() as c:
        ex = c.execute("SELECT * FROM tarefas WHERE id = ?", (tid,)).fetchone()
        if not ex:
            return erro("Tarefa nao encontrada", 404)
        st, pr = dados.get("status", ex["status"]), dados.get("prioridade", ex["prioridade"])
        if (err := valida_sp(st, pr)):
            return err
        up = c.execute("UPDATE tarefas SET titulo = ?, descricao = ?, status = ?, prioridade = ?, projeto_id = ? WHERE id = ? RETURNING *",
                       (dados.get("titulo", ex["titulo"]), dados.get("descricao", ex["descricao"]),
                        st, pr, dados.get("projeto_id", ex["projeto_id"]), tid)).fetchone()
    return jsonify(d(up))


@app.route("/api/tarefas/<int:tid>", methods=["DELETE"])
def deletar_tarefa(tid):
    with get_db() as c:
        cur = c.execute("DELETE FROM tarefas WHERE id = ?", (tid,))
    return jsonify({"mensagem": "Tarefa removida com sucesso"}) if cur.rowcount else erro("Tarefa nao encontrada", 404)


@app.errorhandler(404)
def _404(e):
    return jsonify({"erro": "Recurso nao encontrado"}), 404


@app.errorhandler(500)
def _500(e):
    return jsonify({"erro": "Erro interno do servidor"}), 500


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)