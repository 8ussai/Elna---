from fastapi.security import OAuth2PasswordBearer


SQLALCHEMY_DATABASE_URL = "sqlite:///./elna.db"

SECRET_KEY = "DEVELOPMENT_TEST_KEY" 
ALGORITHM = "HS256"               
ACCESS_TOKEN_EXPIRE_MINUTES = 30  

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")