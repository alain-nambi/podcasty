from fastapi.security import OAuth2PasswordBearer

# Utilisé pour extraire le token du header Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")