import os
from decimal import Decimal
from typing import Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.models import Address, Cart, CartItem, Category, Inventory, Order, OrderItem, Payment, Product, User
from app.schemas import (
    AddressBase,
    CartItemCreate,
    CartOut,
    CheckoutRequest,
    DashboardSummary,
    LoginRequest,
    OrderOut,
    ProductOut,
    UserCreate,
    UserOut,
)

app = FastAPI(title="ShopSphere API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)


def seed_product_catalog(db: Session) -> None:
    if db.query(Product).count() > 0:
        return

    categories = {
        "Electronics": Category(name="Electronics", description="Consumer electronics and smart devices"),
        "Home": Category(name="Home", description="Home essentials and office accessories"),
        "Accessories": Category(name="Accessories", description="Accessories and small upgrades"),
    }
    db.add_all(categories.values())
    db.commit()

    cat_map = {name: cat for name, cat in categories.items()}
    products = [
        Product(
            sku="ELE-LAP-100",
            name="Aurora Pro Laptop",
            description="14-inch productivity laptop with 16GB RAM and 512GB SSD.",
            price=Decimal("1199.99"),
            category_id=cat_map["Electronics"].id,
            image_url="https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=800&q=80",
        ),
        Product(
            sku="ELE-HEAD-200",
            name="Nimbus Headphones",
            description="Wireless noise-cancelling headphones with immersive sound.",
            price=Decimal("249.50"),
            category_id=cat_map["Electronics"].id,
            image_url="https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=800&q=80",
        ),
        Product(
            sku="HOME-LAMP-300",
            name="Luma Desk Lamp",
            description="Modern adjustable desk light with USB-C charging port.",
            price=Decimal("89.00"),
            category_id=cat_map["Home"].id,
            image_url="https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=800&q=80",
        ),
        Product(
            sku="ACC-KEY-440",
            name="Evergreen Mechanical Keyboard",
            description="Compact keyboard with tactile switches and RGB backlighting.",
            price=Decimal("129.99"),
            category_id=cat_map["Accessories"].id,
            image_url="https://images.unsplash.com/photo-1511467687858-23d96c32e4ae?auto=format&fit=crop&w=800&q=80",
        ),
    ]
    db.add_all(products)
    db.commit()

    for product in products:
        db.add(Inventory(product_id=product.id, available=20, reserved=0))
    db.commit()


@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        seed_product_catalog(db)
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/products", response_model=List[ProductOut])
def list_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products


@app.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/auth/register", response_model=UserOut)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        name=payload.name,
        email=payload.email.lower(),
        password_hash=f"hashed::{payload.password}",
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/auth/login")
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or user.password_hash != f"hashed::{payload.password}":
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "user_id": user.id, "name": user.name}


@app.get("/cart")
def get_cart(user_id: int = Query(...), db: Session = Depends(get_db)):
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        return {"user_id": user_id, "items": [], "subtotal": 0}

    items = []
    subtotal = Decimal("0.00")
    for item in cart.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            line_total = product.price * item.quantity
            subtotal += line_total
            items.append(
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "product_name": product.name,
                    "product_price": product.price,
                    "quantity": item.quantity,
                }
            )
    return {"user_id": user_id, "items": items, "subtotal": subtotal}


@app.post("/cart/items")
def add_cart_item(payload: CartItemCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    cart = db.query(Cart).filter(Cart.user_id == payload.user_id).first()
    if not cart:
        cart = Cart(user_id=payload.user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing = db.query(CartItem).filter(CartItem.cart_id == cart.id, CartItem.product_id == payload.product_id).first()
    if existing:
        existing.quantity += payload.quantity
    else:
        db.add(CartItem(cart_id=cart.id, product_id=payload.product_id, quantity=payload.quantity))

    db.commit()
    return {"message": "Item added to cart", "user_id": user.id}


@app.delete("/cart/items/{product_id}")
def remove_cart_item(product_id: int, user_id: int = Query(...), db: Session = Depends(get_db)):
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    item = db.query(CartItem).filter(CartItem.cart_id == cart.id, CartItem.product_id == product_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"message": "Item removed"}


@app.get("/orders")
def list_orders(user_id: int = Query(...), db: Session = Depends(get_db)):
    orders = db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).all()
    response = []
    for order in orders:
        items = []
        for order_item in order.items:
            product = db.query(Product).filter(Product.id == order_item.product_id).first()
            items.append(
                {
                    "product_id": order_item.product_id,
                    "product_name": product.name if product else "Unknown product",
                    "quantity": order_item.quantity,
                    "unit_price": order_item.unit_price,
                }
            )
        response.append(
            {
                "id": order.id,
                "user_id": order.user_id,
                "status": order.status,
                "total_amount": order.total_amount,
                "items": items,
                "payments": [{"amount": p.amount, "status": p.status} for p in order.payments],
            }
        )
    return response


@app.post("/orders/checkout", response_model=OrderOut)
def checkout(payload: CheckoutRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not payload.items:
        raise HTTPException(status_code=400, detail="Order cannot be empty")

    cart = db.query(Cart).filter(Cart.user_id == payload.user_id).first()
    if cart:
        cart_items = cart.items
    else:
        cart_items = []

    chosen_items = payload.items
    if cart and not payload.items:
        chosen_items = [{"product_id": item.product_id, "quantity": item.quantity} for item in cart.items]

    total = Decimal("0.00")
    order_items = []
    for record in chosen_items:
        product = db.query(Product).filter(Product.id == record.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {record.product_id} not found")

        inventory = db.query(Inventory).filter(Inventory.product_id == record.product_id).first()
        if inventory and inventory.available < record.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}")

        if inventory:
            inventory.available -= record.quantity
            inventory.reserved += record.quantity

        total += product.price * record.quantity
        order_items.append(
            OrderItem(
                product_id=product.id,
                quantity=record.quantity,
                unit_price=product.price,
            )
        )

    order = Order(
        user_id=payload.user_id,
        status="paid",
        total_amount=total,
        idempotency_key=payload.idempotency_key,
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    for item in order_items:
        item.order_id = order.id
        db.add(item)
    db.commit()

    payment = Payment(order_id=order.id, method="simulated", amount=total, status="approved")
    db.add(payment)
    db.commit()

    if cart:
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        db.commit()

    db.add(Address(
        user_id=payload.user_id,
        street=payload.shipping_address.street,
        city=payload.shipping_address.city,
        state=payload.shipping_address.state,
        postal_code=payload.shipping_address.postal_code,
        country=payload.shipping_address.country,
    ))
    db.commit()

    return OrderOut(
        id=order.id,
        user_id=order.user_id,
        status=order.status,
        total_amount=order.total_amount,
        items=[
            {
                "product_id": item.product_id,
                "product_name": db.query(Product).filter(Product.id == item.product_id).one().name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
            }
            for item in order.items
        ],
        payments=[{"amount": payment.amount, "status": payment.status}],
    )


@app.get("/admin/dashboard", response_model=DashboardSummary)
def admin_dashboard(db: Session = Depends(get_db)):
    products_count = db.query(Product).count()
    orders_count = db.query(Order).count()
    revenue = db.query(func.coalesce(func.sum(Order.total_amount), 0)).scalar() or Decimal("0.00")
    low_inventory = db.query(Inventory).filter(Inventory.available < 5).count()
    return DashboardSummary(
        products=products_count,
        orders=orders_count,
        revenue=revenue,
        low_inventory=low_inventory,
    )


@app.get("/")
def root():
    return {"message": "ShopSphere API is running"}
