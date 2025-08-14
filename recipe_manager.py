"""
Recipe Manager - Save and reuse scraping configurations
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import uuid

class RecipeManager:
    """
    Manage scraping recipes (saved configurations)
    """
    
    def __init__(self, storage_path: str = "recipes"):
        self.storage_path = storage_path
        if not os.path.exists(storage_path):
            os.makedirs(storage_path)
        self.recipes = self._load_all_recipes()
    
    def create_recipe(self, name: str, config: Dict) -> Dict:
        """
        Create a new scraping recipe
        
        Args:
            name: Recipe name
            config: Scraping configuration
                {
                    "url_pattern": "https://example.com/products/*",
                    "strategy": "auto",
                    "output_format": "json",
                    "selectors": {
                        "title": "h1.product-title",
                        "price": "span.price",
                        "description": "div.description"
                    },
                    "options": {
                        "use_proxy": true,
                        "wait_time": 5,
                        "screenshot": false
                    }
                }
        """
        recipe_id = str(uuid.uuid4())
        recipe = {
            "id": recipe_id,
            "name": name,
            "config": config,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "usage_count": 0,
            "last_used": None,
            "success_rate": 0,
            "tags": config.get("tags", [])
        }
        
        # Save to file
        filepath = os.path.join(self.storage_path, f"{recipe_id}.json")
        with open(filepath, 'w') as f:
            json.dump(recipe, f, indent=2)
        
        self.recipes[recipe_id] = recipe
        return recipe
    
    def get_recipe(self, recipe_id: str) -> Optional[Dict]:
        """Get recipe by ID"""
        return self.recipes.get(recipe_id)
    
    def get_recipe_by_name(self, name: str) -> Optional[Dict]:
        """Get recipe by name"""
        for recipe in self.recipes.values():
            if recipe["name"] == name:
                return recipe
        return None
    
    def list_recipes(self, tags: List[str] = None) -> List[Dict]:
        """List all recipes, optionally filtered by tags"""
        recipes = list(self.recipes.values())
        
        if tags:
            recipes = [
                r for r in recipes 
                if any(tag in r.get("tags", []) for tag in tags)
            ]
        
        return sorted(recipes, key=lambda x: x["created_at"], reverse=True)
    
    def update_recipe(self, recipe_id: str, updates: Dict) -> Optional[Dict]:
        """Update an existing recipe"""
        if recipe_id not in self.recipes:
            return None
        
        recipe = self.recipes[recipe_id]
        recipe["config"].update(updates.get("config", {}))
        recipe["name"] = updates.get("name", recipe["name"])
        recipe["tags"] = updates.get("tags", recipe["tags"])
        recipe["updated_at"] = datetime.now().isoformat()
        
        # Save to file
        filepath = os.path.join(self.storage_path, f"{recipe_id}.json")
        with open(filepath, 'w') as f:
            json.dump(recipe, f, indent=2)
        
        return recipe
    
    def delete_recipe(self, recipe_id: str) -> bool:
        """Delete a recipe"""
        if recipe_id not in self.recipes:
            return False
        
        # Delete file
        filepath = os.path.join(self.storage_path, f"{recipe_id}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
        
        del self.recipes[recipe_id]
        return True
    
    def execute_recipe(self, recipe_id: str, url: str = None) -> Dict:
        """
        Execute a recipe
        """
        recipe = self.get_recipe(recipe_id)
        if not recipe:
            return {"error": "Recipe not found"}
        
        config = recipe["config"].copy()
        
        # Override URL if provided
        if url:
            config["url"] = url
        
        # Update usage stats
        recipe["usage_count"] += 1
        recipe["last_used"] = datetime.now().isoformat()
        
        # Save updated stats
        filepath = os.path.join(self.storage_path, f"{recipe_id}.json")
        with open(filepath, 'w') as f:
            json.dump(recipe, f, indent=2)
        
        return config
    
    def _load_all_recipes(self) -> Dict:
        """Load all recipes from storage"""
        recipes = {}
        if not os.path.exists(self.storage_path):
            return recipes
        
        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                filepath = os.path.join(self.storage_path, filename)
                try:
                    with open(filepath, 'r') as f:
                        recipe = json.load(f)
                        recipes[recipe["id"]] = recipe
                except Exception as e:
                    print(f"Error loading recipe {filename}: {e}")
        
        return recipes
    
    def get_popular_recipes(self, limit: int = 10) -> List[Dict]:
        """Get most used recipes"""
        recipes = list(self.recipes.values())
        return sorted(recipes, key=lambda x: x["usage_count"], reverse=True)[:limit]
    
    def search_recipes(self, query: str) -> List[Dict]:
        """Search recipes by name or tags"""
        query = query.lower()
        results = []
        
        for recipe in self.recipes.values():
            if (query in recipe["name"].lower() or
                any(query in tag.lower() for tag in recipe.get("tags", []))):
                results.append(recipe)
        
        return results

# Predefined recipes for common use cases
DEFAULT_RECIPES = [
    {
        "name": "E-commerce Product Scraper",
        "config": {
            "strategy": "auto",
            "output_format": "structured",
            "selectors": {
                "title": ["h1", ".product-title", "[itemprop='name']"],
                "price": [".price", "[itemprop='price']", ".product-price"],
                "description": [".description", "[itemprop='description']"],
                "images": ["img.product-image", ".gallery img"],
                "availability": [".availability", "[itemprop='availability']"]
            },
            "options": {
                "use_proxy": True,
                "wait_time": 3,
                "extract_schema": True
            }
        },
        "tags": ["ecommerce", "products", "shopping"]
    },
    {
        "name": "News Article Scraper",
        "config": {
            "strategy": "auto",
            "output_format": "markdown",
            "selectors": {
                "title": ["h1", ".article-title", "[itemprop='headline']"],
                "author": [".author", "[itemprop='author']", ".by-line"],
                "date": ["time", "[itemprop='datePublished']", ".publish-date"],
                "content": ["article", ".article-content", "[itemprop='articleBody']"]
            },
            "options": {
                "use_proxy": True,
                "clean_text": True,
                "extract_links": True
            }
        },
        "tags": ["news", "articles", "media"]
    },
    {
        "name": "Social Media Profile Scraper",
        "config": {
            "strategy": "undetected",
            "output_format": "json",
            "selectors": {
                "username": [".username", ".profile-name"],
                "bio": [".bio", ".profile-description"],
                "followers": [".followers-count", "[data-followers]"],
                "posts": [".post-count", "[data-posts]"]
            },
            "options": {
                "use_proxy": True,
                "wait_time": 5,
                "scroll_to_load": True
            }
        },
        "tags": ["social", "profiles", "metrics"]
    },
    {
        "name": "Real Estate Listing Scraper",
        "config": {
            "strategy": "selenium",
            "output_format": "structured",
            "selectors": {
                "address": [".property-address", ".listing-address"],
                "price": [".listing-price", ".property-price"],
                "bedrooms": [".bed-count", "[data-bedrooms]"],
                "bathrooms": [".bath-count", "[data-bathrooms]"],
                "sqft": [".property-size", ".square-feet"],
                "description": [".property-description", ".listing-details"]
            },
            "options": {
                "use_proxy": True,
                "screenshot": True,
                "extract_images": True
            }
        },
        "tags": ["realestate", "property", "listings"]
    },
    {
        "name": "Job Listing Scraper",
        "config": {
            "strategy": "auto",
            "output_format": "structured",
            "selectors": {
                "title": [".job-title", "h1"],
                "company": [".company-name", ".employer"],
                "location": [".job-location", ".location"],
                "salary": [".salary", ".compensation"],
                "description": [".job-description", ".posting-description"],
                "requirements": [".requirements", ".qualifications"]
            },
            "options": {
                "use_proxy": True,
                "extract_apply_link": True
            }
        },
        "tags": ["jobs", "careers", "employment"]
    }
]

# Global instance
recipe_manager = RecipeManager()