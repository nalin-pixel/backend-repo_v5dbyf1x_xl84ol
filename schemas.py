"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Customization settings schema for the site
class QuizQuestion(BaseModel):
    q: str
    a: List[str]
    correct: int = Field(0, ge=0)

class Settings(BaseModel):
    """
    Site customization options (single document)
    Collection name: "settings"
    """
    key: str = Field("singleton", description="Singleton key to identify unique doc")
    title: str = Field("Playful Mario‑vibe Game Hub", description="Hero title text")
    subtitle: str = Field("A vibrant landing page with a quiz and a roulette game.", description="Hero subtitle text")
    primaryColor: str = Field("#ef4444", description="Primary brand color (hex)")
    accentColor: str = Field("#f59e0b", description="Accent color (hex)")
    heroLogoUrl: Optional[str] = Field(None, description="URL for hero logo image")
    wheelBgUrl: Optional[str] = Field(None, description="URL for roulette background image")
    quizQuestions: Optional[List[QuizQuestion]] = None
