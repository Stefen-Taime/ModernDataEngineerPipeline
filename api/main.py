from fastapi import FastAPI, HTTPException, Depends, status, Request, Query
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from concurrent_log_handler import ConcurrentRotatingFileHandler
import logging
import os
import uvicorn
from typing import Optional
from routes.routes import router as auth_router
from models.models import User
import sys
from pathlib import Path
from elasticsearch import AsyncElasticsearch


sys.path.append(str(Path(__file__).parent.absolute()))


# Load environment variables
load_dotenv()

# Database Configuration
MONGO_URI = os.getenv('MONGO_URI')
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ELASTICSEARCH_URL = os.getenv('ELASTICSEARCH_URL')


app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(MONGO_URI)
    app.mongodb = app.mongodb_client['kafka-topic']
    app.news_collection = app.mongodb['rss_news']  
    app.token_user_db = app.mongodb_client['tokenUser']
    app.elasticsearch = AsyncElasticsearch(ELASTICSEARCH_URL)

@app.on_event("shutdown")
async def shutdown_event():
    app.mongodb_client.close()
    await app.elasticsearch.close()


# Logging Configuration
def setup_logging():
    logger = logging.getLogger("MyLogger")
    log_file = "app.log"
    rotate_handler = ConcurrentRotatingFileHandler(log_file, "a", 512 * 1024, 5)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    rotate_handler.setFormatter(formatter)
    logger.addHandler(rotate_handler)
    return logger

logger = setup_logging()

app.include_router(auth_router)

# OAuth2 Configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# User Authentication
async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)) -> Optional[User]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

        db = request.app.token_user_db
        db_user = await db["users"].find_one({"username": username})
        if db_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        db_user["id"] = str(db_user["_id"])
        del db_user["_id"]

        return User(**db_user)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

@app.get('/news/{news_id}')
async def get_news(news_id: str, request: Request, current_user: User = Depends(get_current_user)):
    news_collection = request.app.news_collection
    news_article = await news_collection.find_one({'_id': news_id})
    if news_article:
        return news_article
    raise HTTPException(status_code=404, detail="News article not found")

@app.get('/news')
async def get_all_news(request: Request, page: int = 1, page_size: int = 100, current_user: User = Depends(get_current_user)):
    news_collection = request.app.news_collection
    skip = (page - 1) * page_size
    news_articles_cursor = news_collection.find().skip(skip).limit(page_size)
    news_articles = await news_articles_cursor.to_list(length=page_size)
    return news_articles

@app.delete('/news/{news_id}')
async def delete_news(news_id: str, request: Request, current_user: User = Depends(get_current_user)):
    news_collection = request.app.news_collection
    result = await news_collection.delete_one({'_id': news_id})
    if result.deleted_count:
        return {"message": "News article deleted successfully"}
    raise HTTPException(status_code=404, detail="News article not found")

@app.put('/news/{news_id}')
async def update_news(news_id: str, data: dict, request: Request, current_user: User = Depends(get_current_user)):
    news_collection = request.app.news_collection
    result = await news_collection.update_one({'_id': news_id}, {'$set': data})
    if result.matched_count:
        return {"message": "News article updated successfully"}
    raise HTTPException(status_code=404, detail="News article not found")

@app.delete('/news')
async def delete_all_news(request: Request, current_user: User = Depends(get_current_user)):
    news_collection = request.app.news_collection
    result = await news_collection.delete_many({})
    return {"message": f"All news articles deleted. Count: {result.deleted_count}"}



@app.get('/api/v1/news/')
async def get_news(request: Request, search: str = None, language: str = None):
    query_body = {"query": {"bool": {}}}

    must_conditions = []
    if search:
        if "|" in search:
            field, value = search.split("|", 1)
            must_conditions.append({"match": {f"document.{field}": value}})
        else:
            must_conditions.append({"multi_match": {"query": search, "fields": ["document.title", "document.description", "document.author"]}})

    if language:
        must_conditions.append({"match": {"document.language": language}})

    if must_conditions:
        query_body["query"]["bool"]["must"] = must_conditions

    response = await request.app.elasticsearch.search(index="rss_news", body=query_body)
    return response["hits"]["hits"]

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="debug"
    )
