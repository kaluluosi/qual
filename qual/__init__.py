from fastapi import FastAPI
from uvicorn import run


app = FastAPI()



def serve():
    run(app)