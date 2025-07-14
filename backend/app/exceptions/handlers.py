from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from jose import JWTError
from starlette.status import HTTP_401_UNAUTHORIZED
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Postcast API", version="1.0.0")

@app.exception_handler(JWTError)
async def jwt_error_handler(request: Request, exc: JWTError):
    return JSONResponse(
        status_code=HTTP_401_UNAUTHORIZED,
        content={"detail": "Token invalide ou expiré. Veuillez vous reconnecter."}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Pour laisser les erreurs classiques passer (ex: User not found)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
