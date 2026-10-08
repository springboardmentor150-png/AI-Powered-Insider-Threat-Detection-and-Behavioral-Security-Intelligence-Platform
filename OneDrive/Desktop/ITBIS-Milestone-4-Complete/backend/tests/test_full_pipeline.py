from fastapi.testclient import TestClient
from app.main import app
c=TestClient(app)
def h():
 r=c.post('/auth/login',json={'email':'admin@itbis.com','password':'Admin@123'}); assert r.status_code==200; return {'Authorization':'Bearer '+r.json()['access_token']}
def test_login_dashboard(): assert c.get('/dashboard/admin',headers=h()).status_code==200
def test_ingest_risk():
 x=h(); assert c.post('/logs/ingest',json={'employee_id':'EMP1001','event_type':'login'},headers=x).status_code==200; assert c.get('/risk-score/EMP1001',headers=x).status_code==200
def test_role_restriction():
 r=c.post('/auth/login',json={'email':'analyst@itbis.com','password':'Analyst@123'}); assert c.get('/dashboard/admin',headers={'Authorization':'Bearer '+r.json()['access_token']}).status_code==403
