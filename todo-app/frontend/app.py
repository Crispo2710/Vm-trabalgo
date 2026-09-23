"""
Front-end - Sistema de Gestão de Tarefas / Projetos
Roda na VM de Front-end (Ubuntu).

Não acessa o banco diretamente: consome a API RESTful do back-end
(VM de back-end) via HTTP, usando a biblioteca 'requests'.

Configuração:
  Defina a variável de ambiente BACKEND_URL com o IP:porta da VM de back-end.
  Exemplo:  export BACKEND_URL="http://192.168.1.20:5000"
"""
import os
import requests
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "troque-esta-chave-em-producao"

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:5000")


def api_get(path, params=None):
    r = requests.get(f"{BACKEND_URL}{path}", params=params, timeout=5)
    r.raise_for_status()
    return r.json()


def api_post(path, data):
    r = requests.post(f"{BACKEND_URL}{path}", json=data, timeout=5)
    return r


def api_put(path, data):
    r = requests.put(f"{BACKEND_URL}{path}", json=data, timeout=5)
    return r


def api_delete(path):
    r = requests.delete(f"{BACKEND_URL}{path}", timeout=5)
    return r


# ------------------------------------------------------------------ HOME ---
@app.route("/")
def index():
    filtro_status = request.args.get("status", "")
    filtro_projeto = request.args.get("projeto_id", "")

    try:
        projetos = api_get("/api/projetos")
        params = {}
        if filtro_status:
            params["status"] = filtro_status
        if filtro_projeto:
            params["projeto_id"] = filtro_projeto
        tarefas = api_get("/api/tarefas", params=params)
    except requests.exceptions.RequestException:
        flash("Não foi possível conectar ao back-end. Verifique BACKEND_URL.", "erro")
        projetos, tarefas = [], []

    projetos_por_id = {p["id"]: p["nome"] for p in projetos}
    return render_template(
        "index.html",
        tarefas=tarefas,
        projetos=projetos,
        projetos_por_id=projetos_por_id,
        filtro_status=filtro_status,
        filtro_projeto=filtro_projeto,
    )


# --------------------------------------------------------------- TAREFAS ---
@app.route("/tarefas/nova", methods=["GET", "POST"])
def nova_tarefa():
    if request.method == "POST":
        payload = {
            "titulo": request.form["titulo"],
            "descricao": request.form.get("descricao", ""),
            "status": request.form.get("status", "pendente"),
            "prioridade": request.form.get("prioridade", "media"),
            "projeto_id": request.form.get("projeto_id") or None,
        }
        resp = api_post("/api/tarefas", payload)
        if resp.status_code == 201:
            flash("Tarefa criada com sucesso!", "sucesso")
            return redirect(url_for("index"))
        flash(f"Erro ao criar tarefa: {resp.json().get('erro')}", "erro")

    projetos = api_get("/api/projetos")
    return render_template("form_tarefa.html", tarefa=None, projetos=projetos)


@app.route("/tarefas/<int:tarefa_id>/editar", methods=["GET", "POST"])
def editar_tarefa(tarefa_id):
    if request.method == "POST":
        payload = {
            "titulo": request.form["titulo"],
            "descricao": request.form.get("descricao", ""),
            "status": request.form.get("status", "pendente"),
            "prioridade": request.form.get("prioridade", "media"),
            "projeto_id": request.form.get("projeto_id") or None,
        }
        resp = api_put(f"/api/tarefas/{tarefa_id}", payload)
        if resp.status_code == 200:
            flash("Tarefa atualizada com sucesso!", "sucesso")
            return redirect(url_for("index"))
        flash(f"Erro ao atualizar tarefa: {resp.json().get('erro')}", "erro")

    tarefa = api_get(f"/api/tarefas/{tarefa_id}")
    projetos = api_get("/api/projetos")
    return render_template("form_tarefa.html", tarefa=tarefa, projetos=projetos)


@app.route("/tarefas/<int:tarefa_id>/excluir", methods=["POST"])
def excluir_tarefa(tarefa_id):
    api_delete(f"/api/tarefas/{tarefa_id}")
    flash("Tarefa removida.", "sucesso")
    return redirect(url_for("index"))


# -------------------------------------------------------------- PROJETOS ---
@app.route("/projetos", methods=["GET", "POST"])
def projetos_view():
    if request.method == "POST":
        payload = {
            "nome": request.form["nome"],
            "descricao": request.form.get("descricao", ""),
        }
        resp = api_post("/api/projetos", payload)
        if resp.status_code == 201:
            flash("Projeto criado com sucesso!", "sucesso")
        else:
            flash("Erro ao criar projeto.", "erro")
        return redirect(url_for("projetos_view"))

    projetos = api_get("/api/projetos")
    return render_template("projetos.html", projetos=projetos)


@app.route("/projetos/<int:projeto_id>/excluir", methods=["POST"])
def excluir_projeto(projeto_id):
    api_delete(f"/api/projetos/{projeto_id}")
    flash("Projeto removido.", "sucesso")
    return redirect(url_for("projetos_view"))


if __name__ == "__main__":
    # host 0.0.0.0 para poder ser acessado pela rede (placa em modo Bridge)
    app.run(host="0.0.0.0", port=8080, debug=True)
