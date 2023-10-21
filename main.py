from typing import Union
from enum import Enum
import random
import string

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

class User(BaseModel):
    id: str

class JobStatus(str, Enum):
    created = "created"
    running = "running"
    completed = "completed"
    failed = "failed"

class Job(BaseModel):
    id: str
    input_url: str
    output_url: str
    status: JobStatus

@app.get("/")
def read_root():
    return {"status": "ok"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}


@app.post("/users")
def create_user(user: User):
    user.id = generate_random_id()
    return {"user_id": user.id}


def generate_random_id() -> str:
    return ''.join(random.choices(string.ascii_letters, k=12))