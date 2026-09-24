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

class RemoteCursor:
    def __init__(self, res, sql=""):
        if res and isinstance(res, dict):
            self._rows = res.get("rows", [])
            self.lastrowid = res.get("lastrowid", 1)
            self.rowcount = res.get("rowcount", len(self._rows))
            cols = res.get("columns", [])
            # Simula a propriedade description do sqlite3 exigida pelo app.py
            self.description = [(c,) for c in cols] if cols else None
        else:
            self._rows = []
            self.lastrowid = 1
            self.rowcount = 0
            self.description = None
            
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
    def __init__(self):
        pass

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
