from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from configs.database import Base, engine
from configs.conf import settings
from user.routers import user
from auth_credential.routers import auth_credential
from authen.routers import authen
import uvicorn


Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.router.include_router(user.router)
app.router.include_router(auth_credential.router)
app.router.include_router(authen.router)


if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port)
    
