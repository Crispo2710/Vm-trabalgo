"""
API RESTful - Sistema de Gestão de Tarefas / Projetos
Roda na VM de Back-end (Ubuntu).

Endpoints:
  Projetos:
    GET    /api/projetos
    POST   /api/projetos
    GET    /api/projetos/<id>
    PUT    /api/projetos/<id>
    DELETE /api/projetos/<id>

  Tarefas:
    GET    /api/tarefas                (?projeto_id= e ?status= opcionais)
    POST   /api/tarefas
    GET    /api/tarefas/<id>
    PUT    /api/tarefas/<id>
    DELETE /api/tarefas/<id>

  Utilitário:
    GET    /api/health
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from database import init_db, get_connection

app = Flask(__name__)
CORS(app)  # permite que o front-end (outra VM/porta) consuma a API

STATUS_VALIDOS = {"pendente", "em_andamento", "concluida"}
PRIORIDADES_VALIDAS = {"baixa", "media", "alta"}


def linha_para_dict(row):
    return dict(row)


# ---------------------------------------------------------------- health ---
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "servico": "backend-api"})


# -------------------------------------------------------------- PROJETOS ---
@app.route("/api/projetos", methods=["GET"])
def listar_projetos():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM projetos ORDER BY id DESC").fetchall()
    return jsonify([linha_para_dict(r) for r in rows])


@app.route("/api/projetos", methods=["POST"])
def criar_projeto():
    dados = request.get_json(force=True, silent=True) or {}
    nome = dados.get("nome")
    if not nome:
        return jsonify({"erro": "O campo 'nome' é obrigatório"}), 400

    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO projetos (nome, descricao) VALUES (?, ?)",
            (nome, dados.get("descricao", "")),
        )
        conn.commit()
        novo = conn.execute(
            "SELECT * FROM projetos WHERE id = ?", (cur.lastrowid,)
        ).fetchone()
    return jsonify(linha_para_dict(novo)), 201


@app.route("/api/projetos/<int:projeto_id>", methods=["GET"])
def obter_projeto(projeto_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM projetos WHERE id = ?", (projeto_id,)
        ).fetchone()
    if row is None:
        return jsonify({"erro": "Projeto não encontrado"}), 404
    return jsonify(linha_para_dict(row))


@app.route("/api/projetos/<int:projeto_id>", methods=["PUT"])
def atualizar_projeto(projeto_id):
    dados = request.get_json(force=True, silent=True) or {}
    with get_connection() as conn:
        existente = conn.execute(
            "SELECT * FROM projetos WHERE id = ?", (projeto_id,)
        ).fetchone()
        if existente is None:
            return jsonify({"erro": "Projeto não encontrado"}), 404

        nome = dados.get("nome", existente["nome"])
        descricao = dados.get("descricao", existente["descricao"])
        conn.execute(
            "UPDATE projetos SET nome = ?, descricao = ? WHERE id = ?",
            (nome, descricao, projeto_id),
        )
        conn.commit()
        atualizado = conn.execute(
            "SELECT * FROM projetos WHERE id = ?", (projeto_id,)
        ).fetchone()
    return jsonify(linha_para_dict(atualizado))


@app.route("/api/projetos/<int:projeto_id>", methods=["DELETE"])
def deletar_projeto(projeto_id):
    with get_connection() as conn:
        existente = conn.execute(
            "SELECT * FROM projetos WHERE id = ?", (projeto_id,)
        ).fetchone()
        if existente is None:
            return jsonify({"erro": "Projeto não encontrado"}), 404
        conn.execute("DELETE FROM projetos WHERE id = ?", (projeto_id,))
        conn.commit()
    return jsonify({"mensagem": "Projeto removido com sucesso"})


# --------------------------------------------------------------- TAREFAS ---
@app.route("/api/tarefas", methods=["GET"])
def listar_tarefas():
    projeto_id = request.args.get("projeto_id")
    status = request.args.get("status")

    query = "SELECT * FROM tarefas WHERE 1=1"
    params = []
    if projeto_id:
        query += " AND projeto_id = ?"
        params.append(projeto_id)
    if status:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY id DESC"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return jsonify([linha_para_dict(r) for r in rows])


@app.route("/api/tarefas", methods=["POST"])
def criar_tarefa():
    dados = request.get_json(force=True, silent=True) or {}
    titulo = dados.get("titulo")
    if not titulo:
        return jsonify({"erro": "O campo 'titulo' é obrigatório"}), 400

    status = dados.get("status", "pendente")
    prioridade = dados.get("prioridade", "media")
    if status not in STATUS_VALIDOS:
        return jsonify({"erro": f"status inválido. Use um de {STATUS_VALIDOS}"}), 400
    if prioridade not in PRIORIDADES_VALIDAS:
        return jsonify({"erro": f"prioridade inválida. Use um de {PRIORIDADES_VALIDAS}"}), 400

    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO tarefas (titulo, descricao, status, prioridade, projeto_id)
               VALUES (?, ?, ?, ?, ?)""",
            (
                titulo,
                dados.get("descricao", ""),
                status,
                prioridade,
                dados.get("projeto_id"),
            ),
        )
        conn.commit()
        nova = conn.execute(
            "SELECT * FROM tarefas WHERE id = ?", (cur.lastrowid,)
        ).fetchone()
    return jsonify(linha_para_dict(nova)), 201


@app.route("/api/tarefas/<int:tarefa_id>", methods=["GET"])
def obter_tarefa(tarefa_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM tarefas WHERE id = ?", (tarefa_id,)
        ).fetchone()
    if row is None:
        return jsonify({"erro": "Tarefa não encontrada"}), 404
    return jsonify(linha_para_dict(row))


@app.route("/api/tarefas/<int:tarefa_id>", methods=["PUT"])
def atualizar_tarefa(tarefa_id):
    dados = request.get_json(force=True, silent=True) or {}
    with get_connection() as conn:
        existente = conn.execute(
            "SELECT * FROM tarefas WHERE id = ?", (tarefa_id,)
        ).fetchone()
        if existente is None:
            return jsonify({"erro": "Tarefa não encontrada"}), 404

        status = dados.get("status", existente["status"])
        prioridade = dados.get("prioridade", existente["prioridade"])
        if status not in STATUS_VALIDOS:
            return jsonify({"erro": f"status inválido. Use um de {STATUS_VALIDOS}"}), 400
        if prioridade not in PRIORIDADES_VALIDAS:
            return jsonify({"erro": f"prioridade inválida. Use um de {PRIORIDADES_VALIDAS}"}), 400

        conn.execute(
            """UPDATE tarefas
               SET titulo = ?, descricao = ?, status = ?, prioridade = ?, projeto_id = ?
               WHERE id = ?""",
            (
                dados.get("titulo", existente["titulo"]),
                dados.get("descricao", existente["descricao"]),
                status,
                prioridade,
                dados.get("projeto_id", existente["projeto_id"]),
                tarefa_id,
            ),
        )
        conn.commit()
        atualizada = conn.execute(
            "SELECT * FROM tarefas WHERE id = ?", (tarefa_id,)
        ).fetchone()
    return jsonify(linha_para_dict(atualizada))


@app.route("/api/tarefas/<int:tarefa_id>", methods=["DELETE"])
def deletar_tarefa(tarefa_id):
    with get_connection() as conn:
        existente = conn.execute(
            "SELECT * FROM tarefas WHERE id = ?", (tarefa_id,)
        ).fetchone()
        if existente is None:
            return jsonify({"erro": "Tarefa não encontrada"}), 404
        conn.execute("DELETE FROM tarefas WHERE id = ?", (tarefa_id,))
        conn.commit()
    return jsonify({"mensagem": "Tarefa removida com sucesso"})


if __name__ == "__main__":
    init_db()
    # host 0.0.0.0 para aceitar conexões de outras VMs (front-end)
    app.run(host="0.0.0.0", port=5000, debug=True)
