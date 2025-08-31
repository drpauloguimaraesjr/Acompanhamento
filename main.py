from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api_routes import router as api_router

app = FastAPI(title="Sistema Médico")

# Monta arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Inclui rotas da API
app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "Bem-vindo ao Sistema Médico"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)