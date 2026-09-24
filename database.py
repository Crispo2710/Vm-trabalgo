import requests

DB_URL = "http://192.168.1.11:5001/db/query"
DB_PATH = "remoto"

def executar_query_remota(sql, params=[]):
    try:
        response = requests.post(DB_URL, json={"sql": sql, "params": params}, timeout=5)
        if response.status_code == 200:
            return response.json()
        return {"rows": [], "columns": []}
    except Exception as e:
        print(f"[DB ERRO] {e}")
        return {"rows": [], "columns": []}

def inferir_colunas(sql):
    sql_lower = sql.lower()
    if "projetos" in sql_lower:
        return ["id", "nome", "descricao"]
    elif "tarefas" in sql_lower:
        return ["id", "titulo", "descricao", "status", "prioridade", "projeto_id"]
    return []

class RemoteCursor:
    def __init__(self, res, sql=""):
        if res and isinstance(res, dict):
            raw_rows = res.get("rows", [])
            cols = res.get("columns", []) or inferir_colunas(sql)
            self.lastrowid = res.get("lastrowid", 1)
            self.rowcount = res.get("rowcount", len(raw_rows))
            
            # Converte cada linha (lista/tuplo) num dicionário estruturado
            self._rows = []
            for r in raw_rows:
                if isinstance(r, dict):
                    self._rows.append(r)
                elif isinstance(r, (list, tuple)):
                    if cols and len(cols) == len(r):
                        self._rows.append(dict(zip(cols, r)))
                    else:
                        self._rows.append({f"col_{i}": val for i, val in enumerate(r)})
                else:
                    self._rows.append({"resultado": r})
        else:
            self._rows = []
            self.lastrowid = 1
            self.rowcount = 0
            
        self._index = 0

    def fetchall(self):
        return self._rows

    def fetchone(self):
        if self._index < len(self._rows):
            row = self._rows[self._index]
            self._index += 1
            return row
        if self._rows:
            return self._rows[0]
        # Dicionário padrão de segurança caso venha vazio
        return {
            "id": self.lastrowid or 1,
            "titulo": "",
            "descricao": "",
            "status": "pendente",
            "prioridade": "media",
            "projeto_id": None,
            "nome": ""
        }

class RemoteConnection:
    def execute(self, sql, params=()):
        params_list = list(params) if params else []
        res = executar_query_remota(sql, params_list)
        return RemoteCursor(res, sql)

    def commit(self, *args, **kwargs):
        pass

    def rollback(self, *args, **kwargs):
        pass

    def close(self, *args, **kwargs):
        pass

class get_connection:
    def __enter__(self):
        return RemoteConnection()
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

def init_db():
    pass
