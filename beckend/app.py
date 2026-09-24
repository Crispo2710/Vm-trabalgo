import requests

DB_URL = "http://192.168.1.11:5001/db/query"
DB_PATH = "remoto"

def executar_query_remota(sql, params=[]):
    try:
        response = requests.post(DB_URL, json={"sql": sql, "params": params}, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro no servidor de base de dados: {response.text}")
            return None
    except Exception as e:
        print(f"Falha de conexão com a VM de Banco: {e}")
        return None

def inferir_colunas(sql):
    """Mapeia os nomes das colunas com base na tabela acedida na query."""
    sql_lower = sql.lower()
    if "projetos" in sql_lower:
        return ["id", "nome", "descricao"]
    elif "tarefas" in sql_lower:
        return ["id", "titulo", "descricao", "status", "prioridade", "projeto_id"]
    return []

class RemoteCursor:
    def __init__(self, res, sql=""):
        if res and isinstance(res, dict):
            rows = res.get("rows", [])
            cols = res.get("columns") or res.get("cols") or inferir_colunas(sql)
            self.lastrowid = res.get("lastrowid")
            self.rowcount = res.get("rowcount", len(rows))
        else:
            rows, cols, self.lastrowid, self.rowcount = [], inferir_colunas(sql), None, 0

        self._rows = []
        for r in rows:
            if isinstance(r, dict):
                self._rows.append(dict(r))
            elif isinstance(r, (list, tuple)):
                chaves = cols if (cols and len(cols) == len(r)) else [f"col_{i}" for i in range(len(r))]
                self._rows.append(dict(zip(chaves, r)))
            else:
                self._rows.append({"resultado": r})
        
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
        return None

class RemoteConnection:
    def execute(self, sql, params=()):
        params_list = list(params) if params else []
        res = executar_query_remota(sql, params_list)
        return RemoteCursor(res, sql)

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass

class get_connection:
    def __enter__(self):
        return RemoteConnection()
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

def init_db():
    pass
