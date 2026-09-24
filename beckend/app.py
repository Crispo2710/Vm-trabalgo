import requests

DB_URL = "http://192.168.1.11:5001/db/query"

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

class MockRow(dict):
    """Permite acesso aos campos tanto por chave dicionário como por índice se necessário."""
    pass

class RemoteCursor:
    def __init__(self, res):
        if res and isinstance(res, dict):
            rows = res.get("rows", [])
            cols = res.get("columns", [])
            self.lastrowid = res.get("lastrowid")
            self.rowcount = res.get("rowcount", len(rows))
        else:
            rows, cols, self.lastrowid, self.rowcount = [], [], None, 0

        self._rows = []
        for r in rows:
            if isinstance(r, dict):
                self._rows.append(MockRow(r))
            elif isinstance(r, (list, tuple)) and cols:
                self._rows.append(MockRow(zip(cols, r)))
            else:
                self._rows.append(MockRow())
        
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
        # Fallback seguro caso venha vazio (ex: recém-criado)
        return MockRow({
            "id": self.lastrowid or 1,
            "titulo": "Tarefa Recém-Criada",
            "descricao": "",
            "status": "pendente",
            "prioridade": "media",
            "projeto_id": None,
            "nome": "Projeto Padrão"
        })

class RemoteConnection:
    def __init__(self):
        self.cursor_obj = None

    def execute(self, sql, params=()):
        params_list = list(params) if params else []
        res = executar_query_remota(sql, params_list)
        self.cursor_obj = RemoteCursor(res)
        return self.cursor_obj

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
