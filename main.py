from fastapi import FastAPI, HTTPException 
from typing import List
from pymongo import MongoClient
import uvicorn

app = FastAPI()

client = MongoClient("mongodb+srv://productDbUser:productDbUser@inventory.k2cklgh.mongodb.net/")
db = client["products_inventory"]
collection = db["products"]

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/items")
def get_items():
    items = list(collection.find())
    return items

@app.get("/items/{item_id}")
def get_item(item_id: int):
    item = collection.find_one({"_id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.post("/items")
def create_item(item_id: int, name: str, qty: int):
    if collection.find_one({"_id": item_id}):
        raise HTTPException(status_code=400, detail="Item already exists")
    item = {"_id": item_id, "name": name, "qty": qty}
    collection.insert_one(item)
    return item

@app.put("/items/{item_id}")
def update_item(item_id: int, name: str, qty: int):
    item = collection.find_one({"_id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    collection.update_one({"_id": item_id}, {"$set": {"name": name, "qty": qty}})
    item["name"] = name
    item["qty"] = qty
    return item

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    item = collection.find_one({"_id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    collection.delete_one({"_id": item_id})
    return {"message": "Item deleted"}

@app.post("/inventory/manage")
def manage_inventory(item_updates: List[dict]):
    for update in item_updates:
        item_id = update["item_id"]
        qty = update["qty"]
        item = collection.find_one({"_id": item_id})
        if not item:
            raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
        new_qty = item["qty"] + qty
        collection.update_one({"_id": item_id}, {"$set": {"qty": new_qty}})
        item["qty"] = new_qty
    return list(collection.find())