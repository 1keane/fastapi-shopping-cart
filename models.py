from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

# SQLAlchemy model representing the 'carts' table
class Cart(Base):
    __tablename__ = 'carts'
    id = Column(Integer, primary_key=True, index=True)
    # One-to-many relationship with ItemsInCart
    items = relationship("ItemsInCart", back_populates="cart")

# SQLAlchemy model representing the 'items' table
class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Integer)
    # One-to-many relationship with ItemsInCart
    carts = relationship("ItemsInCart", back_populates="item")

# SQLAlchemy model representing the 'items_in_cart' table
class ItemsInCart(Base):
    __tablename__ = 'items_in_cart'
    cart_id = Column(Integer, ForeignKey('carts.id'), primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'), primary_key=True)
    quantity = Column(Integer, default=1)
    # Many-to-one relationship with Cart
    cart = relationship("Cart", back_populates="items")
    # Many-to-one relationship with Item
    item = relationship("Item", back_populates="carts")

