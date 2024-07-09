from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import docker
import requests
import os

app = FastAPI()
client = docker.from_env()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Get the list of container names from an environment variable
# It should be a comma-separated string
depends_on_containers = os.getenv('DEPENDS_ON_CONTAINERS', '').split(',')

def get_containers_info():
    containers_info = []
    for container in client.containers.list():
        if container.name not in depends_on_containers:
            continue
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
    return containers_info

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    containers = get_containers_info()
    return templates.TemplateResponse("index.html", {"request": request, "containers": containers})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
