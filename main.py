import requests
import json
import os
from datetime import datetime

GRAFANA_URL = os.environ.get("GRAFANA_URL", "http://localhost:3000")
API_KEY = os.environ.get("API_KEY", "")
if API_KEY == "":
    print("could not get API_KEY ")
    exit(1)
BACKUP_DIR = "./backups"


def backup() -> bool:
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.get(f"{GRAFANA_URL}/api/search", headers=headers)
    if response.status_code != 200:
        print(
            f"Erro ao acionar a rota='{GRAFANA_URL}/api/search' http status_code={response.status_code}")
        return False
    dashboards = response.json()

    for dashboard in dashboards:
        uid = dashboard["uid"]
        title = dashboard["title"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        response = requests.get(
            f"{GRAFANA_URL}/api/dashboards/uid/{uid}", headers=headers)
        if response.status_code != 200:
            print(
                f"Erro ao acionar a rota='{GRAFANA_URL}/api/dashboards/uid/{uid}' http status_code={response.status_code}")
            return False
        dashboard_details = response.json()

        with open(f"{BACKUP_DIR}/{title}_{uid}_{timestamp}.json", "w") as f:
            json.dump(dashboard_details, f, indent=4)
        print(f"Backup do dashboard '{title}' concluído.")

    return True


if __name__ == "__main__":
    if not backup():
        print("Backup não foi realizado, verifique permisssões/acessos")
        exit(0)
    print("Backup realizado com sucesso")
