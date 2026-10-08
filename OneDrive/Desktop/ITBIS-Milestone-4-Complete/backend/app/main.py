from fastapi import FastAPI,HTTPException,Depends,Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import io,secrets
app=FastAPI(title='ITBIS API',version='4.0.0')
app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:3000','http://127.0.0.1:3000'],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
USERS=[{'id':1,'username':'admin','email':'admin@itbis.com','role':'admin','status':'Active'},{'id':2,'username':'manager1','email':'manager@itbis.com','role':'security_manager','status':'Active'},{'id':3,'username':'analyst1','email':'analyst@itbis.com','role':'security_analyst','status':'Active'},{'id':4,'username':'soc1','email':'soc@itbis.com','role':'soc_engineer','status':'Active'}]
EMPLOYEES=[{'employee_id':'EMP1001','name':'Aarav Sharma','department':'Finance','risk_score':82,'risk_level':'High'},{'employee_id':'EMP1002','name':'Priya Patil','department':'Engineering','risk_score':34,'risk_level':'Low'},{'employee_id':'EMP1003','name':'Rohan Deshmukh','department':'Sales','risk_score':67,'risk_level':'Medium'},{'employee_id':'EMP1004','name':'Neha Kulkarni','department':'HR','risk_score':22,'risk_level':'Low'},{'employee_id':'EMP1005','name':'Vikram Joshi','department':'IT','risk_score':91,'risk_level':'Critical'}]
LOGS=[{'id':1,'employee_id':'EMP1001','event_type':'Login','timestamp':'2026-10-08 09:30','details':'New device login','severity':'Normal'},{'id':2,'employee_id':'EMP1005','event_type':'File Download','timestamp':'2026-10-08 09:25','details':'Large archive downloaded','severity':'High'},{'id':3,'employee_id':'EMP1003','event_type':'File Access','timestamp':'2026-10-08 09:18','details':'Sensitive folder accessed','severity':'Medium'}]
INCIDENTS=[{'id':'INC-008','employee_id':'EMP1005','title':'Abnormal data download','status':'open','severity':'critical','created':'2026-10-08 08:55'},{'id':'INC-007','employee_id':'EMP1001','title':'Unusual login location','status':'open','severity':'high','created':'2026-10-08 08:20'},{'id':'INC-006','employee_id':'EMP1003','title':'Repeated sensitive file access','status':'resolved','severity':'medium','created':'2026-10-07 17:40'}]
AUDIT=[{'time':'10:15 AM','user':'admin','action':'Login','details':'Successful login'},{'time':'09:42 AM','user':'manager1','action':'View Report','details':'Insider threat report'},{'time':'08:30 AM','user':'analyst1','action':'Check Anomaly','details':'EMP1001 flagged'},{'time':'07:55 AM','user':'soc1','action':'Create Incident','details':'Incident INC-008'}]
TOKENS={}
class Login(BaseModel): email:str; password:str
class LogIn(BaseModel): employee_id:str; event_type:str; details:str=''; severity:str='Normal'
def user(authorization:Optional[str]=Header(None)):
 if not authorization or not authorization.startswith('Bearer '): raise HTTPException(401,'Not authenticated')
 u=TOKENS.get(authorization.split(' ',1)[1])
 if not u: raise HTTPException(401,'Invalid token')
 return u
def admin(u=Depends(user)):
 if u['role']!='admin': raise HTTPException(403,'Admin access required')
 return u
def report_role(u=Depends(user)):
 if u['role'] not in ('admin','security_manager'): raise HTTPException(403,'Admin or Security Manager access required')
 return u
@app.get('/')
def root(): return {'status':'ok','milestone':'M4','message':'ITBIS backend is running'}
@app.get('/health')
def health(): return {'status':'healthy'}
@app.post('/auth/login')
def login(x:Login):
 pw={'admin@itbis.com':'Admin@123','manager@itbis.com':'Manager@123','analyst@itbis.com':'Analyst@123','soc@itbis.com':'Soc@123'}
 if pw.get(x.email)!=x.password: raise HTTPException(401,'Invalid email or password')
 u=next(v for v in USERS if v['email']==x.email); t=secrets.token_urlsafe(32); TOKENS[t]=u
 return {'access_token':t,'token_type':'bearer','role':u['role'],'username':u['username']}
@app.get('/dashboard/admin')
def dashboard(u=Depends(admin)):
 roles={}
 for x in USERS: roles[x['role']]=roles.get(x['role'],0)+1
 return {'user_count':len(USERS),'employee_count':len(EMPLOYEES),'total_incidents':len(INCIDENTS),'open_incidents':sum(i['status']=='open' for i in INCIDENTS),'users_by_role':roles,'recent_users':USERS,'audit_trail':AUDIT,'system_health':[{'name':'API Server','status':'Healthy','uptime':'99.9%'},{'name':'PostgreSQL','status':'Healthy','uptime':'99.8%'},{'name':'MongoDB','status':'Healthy','uptime':'99.8%'},{'name':'ML Model','status':'Healthy','uptime':'99.7%'}]}
@app.get('/users')
def users(u=Depends(user)): return USERS
@app.get('/employees')
def employees(u=Depends(user)): return EMPLOYEES
@app.get('/logs')
def logs(u=Depends(user)): return LOGS
@app.post('/logs/ingest')
def ingest(x:LogIn,u=Depends(user)):
 item={'id':len(LOGS)+1,'employee_id':x.employee_id,'event_type':x.event_type,'timestamp':'now','details':x.details,'severity':x.severity}; LOGS.insert(0,item); return {'status':'ok','log':item}
@app.get('/anomalies')
def anomalies(u=Depends(user)): return [{'id':'AN-101','employee_id':'EMP1005','type':'Abnormal Download','score':.94,'severity':'Critical'},{'id':'AN-100','employee_id':'EMP1001','type':'Unusual Login','score':.78,'severity':'High'},{'id':'AN-099','employee_id':'EMP1003','type':'Sensitive Access','score':.63,'severity':'Medium'}]
@app.get('/risk-score/{eid}')
def risk(eid:str,u=Depends(user)):
 x=next((e for e in EMPLOYEES if e['employee_id']==eid),None)
 if not x: raise HTTPException(404,'Employee not found')
 return x
@app.get('/incidents')
def incidents(u=Depends(user)): return INCIDENTS
@app.get('/notifications')
def notifications(u=Depends(user)): return [{'id':1,'message':'Critical alert for EMP1005','channel':'in_app','severity':'critical'},{'id':2,'message':'High-risk activity detected for EMP1001','channel':'in_app','severity':'high'}]
@app.get('/reports/insider-threat/excel')
def excel(u=Depends(report_role)):
 import pandas as pd
 b=io.BytesIO(); pd.DataFrame(EMPLOYEES).to_excel(b,index=False,sheet_name='Insider Threat Report'); b.seek(0)
 return StreamingResponse(b,media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',headers={'Content-Disposition':'attachment; filename=insider_threat_report.xlsx'})
@app.get('/reports/insider-threat/pdf')
def pdf(u=Depends(report_role)):
 from reportlab.platypus import SimpleDocTemplate,Table,Paragraph
 from reportlab.lib.pagesizes import A4
 from reportlab.lib.styles import getSampleStyleSheet
 b=io.BytesIO(); doc=SimpleDocTemplate(b,pagesize=A4); d=[['Employee ID','Name','Department','Risk Score','Risk Level']]+[[e['employee_id'],e['name'],e['department'],e['risk_score'],e['risk_level']] for e in EMPLOYEES]; doc.build([Paragraph('ITBIS Insider Threat Report',getSampleStyleSheet()['Title']),Table(d)]); b.seek(0)
 return StreamingResponse(b,media_type='application/pdf',headers={'Content-Disposition':'attachment; filename=insider_threat_report.pdf'})
