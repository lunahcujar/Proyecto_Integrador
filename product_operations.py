import csv
from typing import List, Optional
from models import product
from datetime import datetime

PRODUCTS_FILENAME = "products.csv"
product_fields = ["id", "name", "categoria", "type_skin", "ingredients", "price"]


def new_product(product: product) -> product:
    products = read_all_products()
    product_with_id = product
    write_product_into_csv(product_with_id)
    return product_with_id


def write_product_into_csv(product: product):
    with open(PRODUCTS_FILENAME, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=product_fields)
        writer.writerow(product.model_dump())


def modify_product_by_name(name: str, product_data: dict) -> Optional[product]:
    products = read_all_products()
    updated_product = None

    for idx, p in enumerate(products):
        if p.name.lower() == name.lower():
            if product_data.get("name") is not None:
                products[idx].name = product_data["name"]
            if product_data.get("categoria") is not None:
                products[idx].categoria = product_data["categoria"]
            if product_data.get("type_skin") is not None:
                products[idx].type_skin = product_data["type_skin"]
            if product_data.get("ingredients") is not None:
                products[idx].ingredients = product_data["ingredients"]
            if product_data.get("price") is not None:
                products[idx].price = product_data["price"]

            updated_product = products[idx]
            break

    if updated_product:
        with open(PRODUCTS_FILENAME, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=product_fields)
            writer.writeheader()
            for p in products:
                writer.writerow(p.model_dump())

        return updated_product

    return None


def read_all_products() -> List[product]:
    products = []
    try:
        with open(PRODUCTS_FILENAME, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                products.append(product(
                    id=int(row["id"]),
                    name=row["name"],
                    categoria=row["categoria"],
                    type_skin=row["type_skin"],
                    ingredients=row["ingredients"],
                    price=float(row["price"])
                ))
    except FileNotFoundError:
        pass
    return products
