# Sistema de Gestão de Tarefas — RESTful (Python)

Aplicação de To-Do List / Gestão de Projetos, dividida em 3 partes que
correspondem exatamente às 3 máquinas virtuais do exercício:

| VM  | Papel          | SO sugerido | Pasta       |
|-----|----------------|-------------|-------------|
| VM1 | Banco de Dados | Debian      | `backend/` (SQLite embutido no back-end) |
| VM2 | Front-end      | Ubuntu      | `frontend/` |
| VM3 | Back-end       | Ubuntu      | `backend/`  |

> Observação: para simplificar, o SQLite roda junto com o back-end (VM3).
> Se quiserem separar de fato o Banco de Dados em uma VM própria (VM1),
> basta trocar `database.py` para usar PostgreSQL/MySQL e apontar a
> conexão para o IP da VM1 — a estrutura do código já isola essa camada.

## 1. Back-end (API RESTful) — instalar na VM de back-end

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

A API sobe em `http://0.0.0.0:5000`. Teste rapidamente:

```bash
curl http://SEU_IP:5000/api/health
curl -X POST http://SEU_IP:5000/api/projetos -H "Content-Type: application/json" -d '{"nome":"Projeto A"}'
curl http://SEU_IP:5000/api/tarefas
```

## 2. Front-end — instalar na VM de front-end

```bash
cd frontend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export BACKEND_URL="http://IP_DA_VM_BACKEND:5000"
python3 app.py
```

Acesse pelo navegador: `http://IP_DA_VM_FRONTEND:8080`

## 3. Configuração de rede (placa em modo Bridge)

Como as VMs vão se comunicar entre si e a placa de rede precisa estar em
modo **Bridge** (conforme anotado no quadro):

1. Nas configurações de cada VM, mude o adaptador de rede de NAT para **Bridge**.
2. Isso faz cada VM pegar um IP na mesma rede do roteador físico.
3. Descubra o IP de cada VM com `ip a` (ou `ifconfig`).
4. Use o IP da VM de back-end na variável `BACKEND_URL` do front-end.
5. Garanta que a porta 5000 (back-end) esteja liberada no firewall:
   `sudo ufw allow 5000`

## Endpoints da API (CRUD completo)

**Projetos**
- `GET /api/projetos`
- `POST /api/projetos`
- `GET /api/projetos/<id>`
- `PUT /api/projetos/<id>`
- `DELETE /api/projetos/<id>`

**Tarefas**
- `GET /api/tarefas` (filtros opcionais `?status=` e `?projeto_id=`)
- `POST /api/tarefas`
- `GET /api/tarefas/<id>`
- `PUT /api/tarefas/<id>`
- `DELETE /api/tarefas/<id>`

## Por que essa arquitetura atende ao exercício

- **RESTful**: cada recurso (`projetos`, `tarefas`) tem sua própria URL,
  e as operações usam os verbos HTTP corretos (GET, POST, PUT, DELETE) —
  ou seja, CRUD completo.
- **Separação Front/Back**: o front-end nunca acessa o banco diretamente;
  ele só fala com o back-end via HTTP/JSON, exatamente como duas VMs
  distintas se comunicariam pela rede.
- **Leve e simples**: usa apenas Flask + SQLite, sem dependências pesadas,
  fácil de rodar em qualquer VM Debian/Ubuntu.
