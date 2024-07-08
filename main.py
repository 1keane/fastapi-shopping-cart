from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, init_db
from models import Cart, Item, ItemsInCart
from pydantic import BaseModel
from typing import List

# Create a FastAPI application instance
app = FastAPI()

# Event handler to initialize the database when the application starts
@app.on_event("startup")
def on_startup():
    init_db()

# Pydantic model to validate item data for creating a new item
class ItemCreate(BaseModel):
    name: str
    price: int

# Pydantic model to validate cart data for creating a new cart, including a list of items
class CartCreate(BaseModel):
    items: List[ItemCreate] = []

# Endpoint to create a new shopping cart
@app.post("/carts/")
def create_cart(cart: CartCreate, db: Session = Depends(get_db)):
    db_cart = Cart()
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    for item in cart.items:
        db_item = db.query(Item).filter(Item.name == item.name).first()
        if not db_item:
            db_item = Item(name=item.name, price=item.price)
            db.add(db_item)
            db.commit()
            db.refresh(db_item)
        items_in_cart = ItemsInCart(cart_id=db_cart.id, item_id=db_item.id, quantity=1)
        db.add(items_in_cart)
        db.commit()
    return db_cart

# Endpoint to get all shopping carts
@app.get("/carts/")
def get_all_carts(db: Session = Depends(get_db)):
    return db.query(Cart).all()

# Endpoint to delete a shopping cart by ID
@app.delete("/carts/{cart_id}")
def delete_cart(cart_id: int, db: Session = Depends(get_db)):
    cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    db.delete(cart)
    db.commit()
    return {"message": "Cart deleted"}

# Endpoint to create a new item
@app.post("/items/")
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = Item(name=item.name, price=item.price)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# Endpoint to update an existing item by ID
@app.put("/items/{item_id}")
def update_item(item_id: int, item: ItemCreate, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db_item.name = item.name
    db_item.price = item.price
    db.commit()
    db.refresh(db_item)
    return db_item

# Endpoint to get an item by ID
@app.get("/items/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

# Endpoint to delete an item by ID
@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted"}

# Endpoint to get all items in a specific cart by cart ID
@app.get("/carts/{cart_id}/items/")
def get_items_in_cart(cart_id: int, db: Session = Depends(get_db)):
    return db.query(ItemsInCart).filter(ItemsInCart.cart_id == cart_id).all()

# Endpoint to add an item to a specific cart by cart ID
@app.post("/carts/{cart_id}/items/")
def add_item_to_cart(cart_id: int, item: ItemCreate, db: Session = Depends(get_db)):
    cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    db_item = db.query(Item).filter(Item.name == item.name).first()
    if not db_item:
        db_item = Item(name=item.name, price=item.price)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
    items_in_cart = db.query(ItemsInCart).filter(ItemsInCart.cart_id == cart_id, ItemsInCart.item_id == db_item.id).first()
    if items_in_cart:
        items_in_cart.quantity += 1
    else:
        items_in_cart = ItemsInCart(cart_id=cart_id, item_id=db_item.id, quantity=1)
        db.add(items_in_cart)
    db.commit()
    return items_in_cart

# Healthcheck endpoint to return the status of the service and summary statistics
@app.get("/healthcheck/")
def healthcheck(db: Session = Depends(get_db)):
    carts = db.query(Cart).count()
    items = db.query(Item).count()
    items_in_cart = db.query(ItemsInCart).all()
    total_items = sum([item.quantity for item in items_in_cart])
    item_counts = {item.item_id: item.quantity for item in items_in_cart}
    return {
        "status": "healthy",
        "number_of_carts": carts,
        "number_of_items": items,
        "item_counts": item_counts,
        "total_items_in_carts": total_items
    }

