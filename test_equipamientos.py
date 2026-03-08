import requests
import json

# Login
login_resp = requests.post(
    "http://localhost:8000/api/auth/login/",
    json={"email": "test@example.com", "password": "SecurePass123!"},
)
token = login_resp.json()["access"]

# Get equipamientos
headers = {"Authorization": f"Bearer {token}"}
resp = requests.get(
    "http://localhost:8000/api/auth/equipamientos/?limit=10", headers=headers
)
data = resp.json()

print(f"Response type: {type(data)}")
print(f"Response content (first 500 chars): {str(data)[:500]}")

# Check if it's a list or dict with count
if isinstance(data, dict) and "count" in data:
    print(f'✅ Total equipamientos: {data["count"]}')
    for item in data["results"]:
        print(f'  - ID {item["id"]}: {item["nombre"]} ({item["categoria_display"]})')
elif isinstance(data, list):
    print(f"✅ Total equipamientos (lista): {len(data)}")
    for item in data[:10]:
        print(
            f'  - ID {item.get("id")}: {item.get("nombre")} ({item.get("categoria_display")})'
        )
