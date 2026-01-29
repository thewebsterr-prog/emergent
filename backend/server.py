from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
from bson import ObjectId


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    price: float
    category: str
    image: str
    rating: float = 0.0
    reviewCount: int = 0
    stock: int = 100
    createdAt: datetime = Field(default_factory=datetime.utcnow)

class Review(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    productId: str
    userId: str = "mock-user"
    userName: str = "Guest User"
    rating: int
    comment: str
    createdAt: datetime = Field(default_factory=datetime.utcnow)

class ReviewCreate(BaseModel):
    productId: str
    rating: int
    comment: str

class CartItem(BaseModel):
    productId: str
    quantity: int

class Cart(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str = "mock-user"
    items: List[CartItem] = []
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

class AddToCartRequest(BaseModel):
    productId: str
    quantity: int = 1

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str = "mock-user"
    items: List[dict]
    total: float
    status: str = "pending"
    shippingAddress: dict
    createdAt: datetime = Field(default_factory=datetime.utcnow)

class OrderCreate(BaseModel):
    items: List[dict]
    total: float
    shippingAddress: dict


# Root endpoint
@api_router.get("/")
async def root():
    return {"message": "E-Commerce API"}


# Product endpoints
@api_router.get("/products", response_model=List[Product])
async def get_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    minPrice: Optional[float] = None,
    maxPrice: Optional[float] = None,
    sort: Optional[str] = "createdAt"
):
    query = {}
    if category:
        query["category"] = category
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
    if minPrice is not None or maxPrice is not None:
        query["price"] = {}
        if minPrice is not None:
            query["price"]["$gte"] = minPrice
        if maxPrice is not None:
            query["price"]["$lte"] = maxPrice
    
    sort_field = sort if sort in ["price", "rating", "createdAt"] else "createdAt"
    products = await db.products.find(query).sort(sort_field, -1).to_list(1000)
    return [Product(**{**product, "id": product.get("id", str(product.get("_id")))}) for product in products]


@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    product = await db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(**{**product, "id": product.get("id", str(product.get("_id")))})


@api_router.get("/categories")
async def get_categories():
    categories = await db.products.distinct("category")
    return {"categories": categories}


# Review endpoints
@api_router.get("/reviews/{product_id}", response_model=List[Review])
async def get_reviews(product_id: str):
    reviews = await db.reviews.find({"productId": product_id}).sort("createdAt", -1).to_list(1000)
    return [Review(**review) for review in reviews]


@api_router.post("/reviews", response_model=Review)
async def create_review(review: ReviewCreate):
    review_obj = Review(
        productId=review.productId,
        rating=review.rating,
        comment=review.comment,
        userName="Guest User"
    )
    await db.reviews.insert_one(review_obj.dict())
    
    # Update product rating
    reviews = await db.reviews.find({"productId": review.productId}).to_list(1000)
    avg_rating = sum(r["rating"] for r in reviews) / len(reviews)
    await db.products.update_one(
        {"id": review.productId},
        {"$set": {"rating": round(avg_rating, 1), "reviewCount": len(reviews)}}
    )
    
    return review_obj


# Cart endpoints
@api_router.get("/cart")
async def get_cart(userId: str = "mock-user"):
    cart = await db.carts.find_one({"userId": userId}, {"_id": 0})
    if not cart:
        cart = Cart(userId=userId).dict()
        await db.carts.insert_one(cart)
        cart = await db.carts.find_one({"userId": userId}, {"_id": 0})
    return cart


@api_router.post("/cart/add")
async def add_to_cart(request: AddToCartRequest, userId: str = "mock-user"):
    cart = await db.carts.find_one({"userId": userId})
    if not cart:
        cart = Cart(userId=userId).dict()
        await db.carts.insert_one(cart)
    
    items = cart.get("items", [])
    existing_item = next((item for item in items if item["productId"] == request.productId), None)
    
    if existing_item:
        existing_item["quantity"] += request.quantity
    else:
        items.append({"productId": request.productId, "quantity": request.quantity})
    
    await db.carts.update_one(
        {"userId": userId},
        {"$set": {"items": items, "updatedAt": datetime.utcnow()}}
    )
    
    return {"message": "Added to cart", "items": items}


@api_router.post("/cart/update")
async def update_cart_item(request: AddToCartRequest, userId: str = "mock-user"):
    cart = await db.carts.find_one({"userId": userId})
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    items = cart.get("items", [])
    existing_item = next((item for item in items if item["productId"] == request.productId), None)
    
    if existing_item:
        if request.quantity <= 0:
            items.remove(existing_item)
        else:
            existing_item["quantity"] = request.quantity
    
    await db.carts.update_one(
        {"userId": userId},
        {"$set": {"items": items, "updatedAt": datetime.utcnow()}}
    )
    
    return {"message": "Cart updated", "items": items}


@api_router.delete("/cart/remove/{product_id}")
async def remove_from_cart(product_id: str, userId: str = "mock-user"):
    cart = await db.carts.find_one({"userId": userId})
    if cart:
        items = [item for item in cart.get("items", []) if item["productId"] != product_id]
        await db.carts.update_one(
            {"userId": userId},
            {"$set": {"items": items, "updatedAt": datetime.utcnow()}}
        )
    return {"message": "Removed from cart"}


@api_router.delete("/cart/clear")
async def clear_cart(userId: str = "mock-user"):
    await db.carts.update_one(
        {"userId": userId},
        {"$set": {"items": [], "updatedAt": datetime.utcnow()}}
    )
    return {"message": "Cart cleared"}


# Order endpoints
@api_router.post("/orders", response_model=Order)
async def create_order(order: OrderCreate, userId: str = "mock-user"):
    order_obj = Order(
        userId=userId,
        items=order.items,
        total=order.total,
        shippingAddress=order.shippingAddress,
        status="confirmed"
    )
    await db.orders.insert_one(order_obj.dict())
    
    # Clear cart after order
    await db.carts.update_one(
        {"userId": userId},
        {"$set": {"items": [], "updatedAt": datetime.utcnow()}}
    )
    
    return order_obj


@api_router.get("/orders", response_model=List[Order])
async def get_orders(userId: str = "mock-user"):
    orders = await db.orders.find({"userId": userId}).sort("createdAt", -1).to_list(1000)
    return [Order(**order) for order in orders]


@api_router.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: str, userId: str = "mock-user"):
    order = await db.orders.find_one({"id": order_id, "userId": userId})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return Order(**order)


# Initialize mock data
@api_router.post("/init-data")
async def init_mock_data():
    # Check if data already exists
    existing_products = await db.products.count_documents({})
    if existing_products > 0:
        return {"message": "Data already initialized"}
    
    # Mock products with stock images
    products = [
        {
            "id": str(uuid.uuid4()),
            "name": "Premium Laptop",
            "description": "High-performance laptop with latest processor and stunning display. Perfect for work and entertainment.",
            "price": 1299.99,
            "category": "Electronics",
            "image": "https://images.unsplash.com/photo-1691073121676-1ab3a6d3d743",
            "rating": 4.5,
            "reviewCount": 0,
            "stock": 50,
            "createdAt": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Wireless Earbuds",
            "description": "Crystal clear sound with active noise cancellation. Long battery life and comfortable fit.",
            "price": 149.99,
            "category": "Electronics",
            "image": "https://images.unsplash.com/photo-1717996563514-e3519f9ef9f7",
            "rating": 4.3,
            "reviewCount": 0,
            "stock": 100,
            "createdAt": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Smart Watch",
            "description": "Track your fitness, receive notifications, and stay connected on the go.",
            "price": 299.99,
            "category": "Electronics",
            "image": "https://images.pexels.com/photos/10185544/pexels-photo-10185544.jpeg",
            "rating": 4.6,
            "reviewCount": 0,
            "stock": 75,
            "createdAt": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Designer T-Shirt",
            "description": "Premium quality cotton t-shirt with modern design. Comfortable and stylish.",
            "price": 39.99,
            "category": "Fashion",
            "image": "https://images.unsplash.com/photo-1532453288672-3a27e9be9efd",
            "rating": 4.4,
            "reviewCount": 0,
            "stock": 200,
            "createdAt": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Running Shoes",
            "description": "Lightweight and comfortable running shoes with excellent cushioning and support.",
            "price": 89.99,
            "category": "Fashion",
            "image": "https://images.unsplash.com/photo-1567401893414-76b7b1e5a7a5",
            "rating": 4.7,
            "reviewCount": 0,
            "stock": 150,
            "createdAt": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Casual Jacket",
            "description": "Stylish casual jacket perfect for any season. Durable and comfortable.",
            "price": 129.99,
            "category": "Fashion",
            "image": "https://images.unsplash.com/photo-1441984904996-e0b6ba687e04",
            "rating": 4.5,
            "reviewCount": 0,
            "stock": 80,
            "createdAt": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Modern Sofa",
            "description": "Comfortable and stylish sofa perfect for any living room. Premium upholstery.",
            "price": 899.99,
            "category": "Home",
            "image": "https://images.unsplash.com/photo-1616046229478-9901c5536a45",
            "rating": 4.8,
            "reviewCount": 0,
            "stock": 25,
            "createdAt": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Table Lamp",
            "description": "Elegant table lamp with adjustable brightness. Perfect for reading and ambiance.",
            "price": 49.99,
            "category": "Home",
            "image": "https://images.unsplash.com/photo-1618220179428-22790b461013",
            "rating": 4.2,
            "reviewCount": 0,
            "stock": 100,
            "createdAt": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Wall Art Set",
            "description": "Beautiful set of wall art to decorate your home. Modern and elegant design.",
            "price": 79.99,
            "category": "Home",
            "image": "https://images.unsplash.com/photo-1572048572872-2394404cf1f3",
            "rating": 4.4,
            "reviewCount": 0,
            "stock": 60,
            "createdAt": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Coffee Maker",
            "description": "Programmable coffee maker with thermal carafe. Brew perfect coffee every time.",
            "price": 79.99,
            "category": "Kitchen",
            "image": "https://images.pexels.com/photos/35348456/pexels-photo-35348456.jpeg",
            "rating": 4.5,
            "reviewCount": 0,
            "stock": 90,
            "createdAt": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Blender Pro",
            "description": "Powerful blender for smoothies, soups, and more. Multiple speed settings.",
            "price": 129.99,
            "category": "Kitchen",
            "image": "https://images.unsplash.com/photo-1586898633445-fc34716255b2",
            "rating": 4.6,
            "reviewCount": 0,
            "stock": 70,
            "createdAt": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Yoga Mat",
            "description": "Non-slip yoga mat with extra cushioning. Perfect for all types of workouts.",
            "price": 29.99,
            "category": "Sports",
            "image": "https://images.pexels.com/photos/3393705/pexels-photo-3393705.jpeg",
            "rating": 4.3,
            "reviewCount": 0,
            "stock": 120,
            "createdAt": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Dumbbell Set",
            "description": "Adjustable dumbbell set for home workouts. Multiple weight options.",
            "price": 199.99,
            "category": "Sports",
            "image": "https://images.unsplash.com/photo-1768987439370-bd60d3d0b28b",
            "rating": 4.7,
            "reviewCount": 0,
            "stock": 45,
            "createdAt": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Backpack",
            "description": "Spacious and durable backpack with laptop compartment. Perfect for travel and work.",
            "price": 59.99,
            "category": "Accessories",
            "image": "https://images.pexels.com/photos/7289716/pexels-photo-7289716.jpeg",
            "rating": 4.4,
            "reviewCount": 0,
            "stock": 110,
            "createdAt": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Sunglasses",
            "description": "Stylish sunglasses with UV protection. Classic design that never goes out of style.",
            "price": 89.99,
            "category": "Accessories",
            "image": "https://images.pexels.com/photos/7289741/pexels-photo-7289741.jpeg",
            "rating": 4.5,
            "reviewCount": 0,
            "stock": 95,
            "createdAt": datetime.utcnow()
        }
    ]
    
    await db.products.insert_many(products)
    return {"message": "Mock data initialized successfully", "products_count": len(products)}


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
