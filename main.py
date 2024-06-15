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
FOLDER_TITLE = os.environ.get("FOLDER_TITLE", "")
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


def get_dashboard(dashboard: dict):
    uid = dashboard["uid"]
    title = dashboard["title"]

    response = requests.get(
        f"{GRAFANA_URL}/api/dashboards/uid/{uid}", headers=HEADERS)
    if response.status_code != 200:
        print(
            f"Erro ao acionar a rota='{GRAFANA_URL}/api/dashboards/uid/{uid}' http status_code={response.status_code}")
        raise ConnectionRefusedError

    return response.json(), title, uid


def write_json(data: dict, title: str, uid: str):
    with open(f"{BACKUP_DIR}/{title}_{uid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
        json.dump(data, f, indent=4)
    print(f"Backup do dashboard '{title}' concluído.")


def backup() -> bool:
    try:
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)

        response = requests.get(f"{GRAFANA_URL}/api/search", headers=HEADERS)
        if response.status_code != 200:
            print(
                f"Erro ao acionar a rota='{GRAFANA_URL}/api/search' http status_code={response.status_code}")
            raise ConnectionAbortedError

        dashboards: list[dict] = response.json()

        for dashboard in dashboards:
            if FOLDER_TITLE != "":
                if dashboard.get("folderTitle"):
                    dashboard_json, title, uid = get_dashboard(dashboard)
                    write_json(dashboard_json, title, uid)
            else:
                dashboard_json, title, uid = get_dashboard(dashboard)
                write_json(dashboard_json, title, uid)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    if not backup():
        print("Backup não foi realizado, verifique permisssões/acessos")
        exit(1)
    print("Backup realizado com sucesso")
