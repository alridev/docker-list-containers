from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import docker
import requests

app = FastAPI()
client = docker.from_env()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

def get_containers_info():
    for container in client.containers.list(all=True):
            if container.name == 'show-containers':
                project_select = container.labels.get('com.docker.compose.project', '')

    containers_info = []
    added = []
    for container in client.containers.list():
        if container.name in added:
            continue
        project = container.labels.get('com.docker.compose.project', '')
        if project_select == project:
            for port, bindings in container.attrs['NetworkSettings']['Ports'].items():
                if bindings:
                    for binding in bindings:
                        url = f"http://umbrel.local:{binding['HostPort']}"
                        containers_info.append({
                            "name": container.name,
                            "url": url,
                            "url_name": f"{binding['HostPort']}",
                            "status": container.status == 'running',
                        })
                        added.append(container.name)
    return containers_info

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    containers = get_containers_info()
    return templates.TemplateResponse("index.html", {"request": request, "containers": containers})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
