from sqlalchemy.orm import Session
from models import *

def create_product(db: Session, p: Product):
    db_product = Product(name=p.name, skin=p.skin, ingredients=p.ingredients, price=p.price)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_all_products(db: Session):
    return db.query(Product).all()

def get_product_by_name(db: Session, product_name: str):
    return db.query(Product).filter(Product.name == product_name).first()

def update_product(db: Session, product_name: str, updated_data: dict):
    db_product = db.query(Product).filter(Product.name == product_name).first()
    if db_product:
        db_product.name = updated_data.get('name', db_product.name)
        db_product.skin = updated_data.get('skin', db_product.skin)
        db_product.ingredients = updated_data.get('ingredients', db_product.ingredients)
        db_product.price = updated_data.get('price', db_product.price)
        db.commit()
        db.refresh(db_product)
        return db_product
    return None

def delete_product(db: Session, product_name: str):
    db_product = db.query(Product).filter(Product.name == product_name).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return db_product
    return None