import httpx

with httpx.Client(base_url="http://localhost:8000") as client:
    # 1. Test Analyst with role 'analyst'
    res_login = client.post("/auth/login", params={"email": "analyst.test@itbis.local", "password": "analyst123"})
    print("Login analyst.test:", res_login.status_code)
    token = res_login.json()["access_token"]
    role = res_login.json()["role"]
    headers = {"Authorization": f"Bearer {token}"}
    res_dash = client.get("/dashboard/analyst", headers=headers)
    print(f"GET /dashboard/analyst as role '{role}': HTTP {res_dash.status_code}")
    assert res_dash.status_code == 200

    # 2. Test SOC with role 'soc_engineer' (and 'soc')
    res_login_soc = client.post("/auth/login", params={"email": "soc1@company.com", "password": "soc123"})
    print("Login soc1:", res_login_soc.status_code)
    token_soc = res_login_soc.json()["access_token"]
    role_soc = res_login_soc.json()["role"]
    headers_soc = {"Authorization": f"Bearer {token_soc}"}
    res_dash_soc = client.get("/dashboard/soc", headers=headers_soc)
    print(f"GET /dashboard/soc as role '{role_soc}': HTTP {res_dash_soc.status_code}")
    assert res_dash_soc.status_code == 200

    # 3. Test Manager with role 'security_manager' (and 'manager')
    res_login_mgr = client.post("/auth/login", params={"email": "manager@itbis.local", "password": "manager123"})
    print("Login manager:", res_login_mgr.status_code)
    token_mgr = res_login_mgr.json()["access_token"]
    role_mgr = res_login_mgr.json()["role"]
    headers_mgr = {"Authorization": f"Bearer {token_mgr}"}
    res_dash_mgr = client.get("/dashboard/manager", headers=headers_mgr)
    print(f"GET /dashboard/manager as role '{role_mgr}': HTTP {res_dash_mgr.status_code}")
    assert res_dash_mgr.status_code == 200

    # 4. Test Admin
    res_login_adm = client.post("/auth/login", params={"email": "admin@itbis.local", "password": "admin123"})
    print("Login admin:", res_login_adm.status_code)
    token_adm = res_login_adm.json()["access_token"]
    role_adm = res_login_adm.json()["role"]
    headers_adm = {"Authorization": f"Bearer {token_adm}"}
    res_dash_adm = client.get("/dashboard/admin", headers=headers_adm)
    print(f"GET /dashboard/admin as role '{role_adm}': HTTP {res_dash_adm.status_code}")
    assert res_dash_adm.status_code == 200

print("\n>>> ALL LIVE HTTP DASHBOARD CHECKS PASSED (HTTP 200) FOR ALL ROLES!")
