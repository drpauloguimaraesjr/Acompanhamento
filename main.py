"""Aplicação principal do sistema médico."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from api_routes import router as api_router

app = FastAPI(title="Sistema Médico")

# Monta arquivos estáticos garantindo que o diretório exista.
static_path = Path(__file__).parent / "static"
if not static_path.exists():
    static_path.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Inclui rotas da API
app.include_router(api_router)


@app.get("/", include_in_schema=False)
def read_root() -> RedirectResponse:
    """Redireciona para a interface web principal."""

    return RedirectResponse(url="/static/index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
