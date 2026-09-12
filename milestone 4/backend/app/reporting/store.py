import json, sqlite3
from datetime import datetime, timezone
from pathlib import Path
BASE = Path(__file__).resolve().parents[2]
DB_PATH = BASE / 'data' / 'reporting.db'
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
class EventStore:
    def __init__(self, db_path=DB_PATH): self.db_path=str(db_path); self._init_db()
    def _conn(self):
        c=sqlite3.connect(self.db_path,timeout=10); c.row_factory=sqlite3.Row; return c
    def _init_db(self):
        with self._conn() as c:
            c.executescript('''
            CREATE TABLE IF NOT EXISTS projects(project_id TEXT PRIMARY KEY,name TEXT NOT NULL,site_id TEXT NOT NULL,project_type TEXT DEFAULT 'commercial',location TEXT DEFAULT '',owner TEXT DEFAULT '',manager TEXT DEFAULT '',created_at TEXT NOT NULL,updated_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,project_id TEXT NOT NULL,payload TEXT NOT NULL,timestamp TEXT NOT NULL,received_at TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS idx_events_project ON events(project_id);
            ''')
    def create_project(self,p):
        now=datetime.now(timezone.utc).isoformat()
        with self._conn() as c:
            c.execute('INSERT INTO projects(project_id,name,site_id,project_type,location,owner,manager,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?)',(p['project_id'],p['name'],p['site_id'],p.get('project_type','commercial'),p.get('location',''),p.get('owner',''),p.get('manager',''),now,now))
        return self.project(p['project_id'])
    def project(self,pid):
        with self._conn() as c:
            r=c.execute('SELECT * FROM projects WHERE project_id=?',(pid,)).fetchone(); return dict(r) if r else None
    def add(self,e):
        now=datetime.now(timezone.utc).isoformat(); e=dict(e); e['received_at']=now; e['timestamp']=e.get('timestamp') or now
        if not self.project(e['project_id']): raise ValueError(f"Project '{e['project_id']}' does not exist. Create/select the project first.")
        with self._conn() as c:
            cur=c.execute('INSERT INTO events(project_id,payload,timestamp,received_at) VALUES(?,?,?,?)',(e['project_id'],json.dumps(e,ensure_ascii=False),e['timestamp'],now)); e['id']=cur.lastrowid
            c.execute('UPDATE projects SET updated_at=? WHERE project_id=?',(now,e['project_id']))
        return e
    def for_project(self,pid):
        with self._conn() as c: rows=c.execute('SELECT payload FROM events WHERE project_id=? ORDER BY id ASC',(pid,)).fetchall()
        return [json.loads(r['payload']) for r in rows]
    def projects(self):
        with self._conn() as c:
            rows=c.execute('SELECT p.*, COUNT(e.id) event_count FROM projects p LEFT JOIN events e ON p.project_id=e.project_id GROUP BY p.project_id ORDER BY p.updated_at DESC').fetchall()
        return [dict(r) for r in rows]
    def delete_project(self,pid):
        with self._conn() as c: c.execute('DELETE FROM events WHERE project_id=?',(pid,)); c.execute('DELETE FROM projects WHERE project_id=?',(pid,))
