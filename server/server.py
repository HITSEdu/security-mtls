from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import ssl


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/hello/{name}")
async def say_hello(name: str, request: Request):
    return {"message": f"Hello {name}"}


uvicorn.run(
    app,
    host="127.0.0.1",
    port=8443,
    ssl_keyfile="cert/server/server-key.pem",
    ssl_certfile="cert/server/server-cert.pem",
    ssl_ca_certs="cert/ca/ca-cert.pem",
    ssl_cert_reqs=ssl.CERT_NONE
    # ssl_cert_reqs=ssl.CERT_REQUIRED
)
