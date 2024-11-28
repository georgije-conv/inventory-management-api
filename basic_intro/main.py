from fastapi import FastAPI, HTTPException
from enum import Enum
from pydantic import BaseModel

app = FastAPI()

class Category(Enum):
    TOOLS = "tools"
    CONSUMABLES = "consumables"

class Item(BaseModel):
    name: str
    price: float
    count: int
    id: int
    category: Category

# note that this would typically be pulled from a database using sqlalchemy
items = {
    0: Item(name="Hammer", price=9.99, count=20, id=0, category=Category.TOOLS),
    1: Item(name="Pliers", price=5.99, count=20, id=1, category=Category.TOOLS),
    2: Item(name="Nails", price=1.99, count=100, id=2, category=Category.CONSUMABLES)
}

# endpoint for main page of url, gets all items
@app.get("/")
async def index() -> dict[str, dict[int, Item]]:
    return {"items": items}

# # defines a type alias that defines our dictionary structure
# Selection = dict[str, str | int | float | Category | None]

# endpoint for retrieving item(s) by filtering on some fields
@app.get("/items/")
async def query_item_by_qparams(
        name: str | None = None,
        price: float | None = None,
        count: int | None = None,
        category: Category | None = None,
        )-> dict[str, dict | list[Item]]:
    """
    This endpoint will return what the query was and then any
    items that meet the query.
    """
    def check_item(item: Item) -> bool:
         """Helper function. Checks if all filter criteria are met."""
         return all(
             (
                 name is None or item.name == name,
                 price is None or item.price == price,
                 count is None or item.count >= count,
                 category is None or item.category is category
             )
         )
    selection = [item for item in items.values() if check_item(item)]
    return {
        "query": {"name": name, "price": price, "count": count, "category": category},
        "selection": selection
    }


# endpoint for retrieving a specific item by its ID
@app.get("/items/{item_id}")
async def query_item_by_id(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not Found")
    return items.get(item_id)
# defines 
Selection = dict[str, str | int | float | Category | None]
@app.post("/items")
async def create_item(item: Item):
    if item.id in items:
        raise HTTPException(status_code=400, detail=f"Item {item.id} already exists")
    items[item.id] = item
    return {"Added Item": item}

# endpoint to update an items attributes
@app.put("/items/{item_id}")
async def update_item(updated_item: Item):
    item_id = updated_item.id
    if item_id not in items:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found in database.")
    items[item_id] = updated_item
    return {
        "Old Item": items.get(item_id),
        "New Item": updated_item
    }


@app.delete("/items/{item_id}")  # Make sure this is your exact path
async def delete_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found in database.")
    item = items.get(item_id)
    items.pop(item_id)
    return {"Deleted Item": item}








