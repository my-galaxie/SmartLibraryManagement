from mangum import Mangum
from main import app

# AWS Lambda Handler
handler = Mangum(app, lifespan="off")
