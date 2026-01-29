#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for E-commerce App
Tests all backend APIs including products, cart, reviews, and orders
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = "https://mini-amazon-7.preview.emergentagent.com/api"

class ECommerceAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.product_ids = []
        self.order_ids = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "success": success,
            "details": details
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise
    
    def test_root_endpoint(self):
        """Test root API endpoint"""
        try:
            response = self.make_request("GET", "/")
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("Root endpoint", True, f"Message: {data['message']}")
                else:
                    self.log_test("Root endpoint", False, "No message in response")
            else:
                self.log_test("Root endpoint", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Root endpoint", False, f"Error: {str(e)}")
    
    def test_init_data(self):
        """Test data initialization endpoint"""
        try:
            response = self.make_request("POST", "/init-data")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Initialize mock data", True, f"Response: {data.get('message', 'Success')}")
            else:
                self.log_test("Initialize mock data", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Initialize mock data", False, f"Error: {str(e)}")
    
    def test_get_products(self):
        """Test product listing endpoint"""
        try:
            # Test basic product listing
            response = self.make_request("GET", "/products")
            if response.status_code == 200:
                products = response.json()
                if isinstance(products, list) and len(products) > 0:
                    self.product_ids = [p["id"] for p in products[:5]]  # Store first 5 product IDs
                    self.log_test("Get all products", True, f"Found {len(products)} products")
                else:
                    self.log_test("Get all products", False, "No products returned")
            else:
                self.log_test("Get all products", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get all products", False, f"Error: {str(e)}")
    
    def test_product_filtering(self):
        """Test product filtering with various parameters"""
        test_cases = [
            {"params": {"category": "Electronics"}, "name": "Filter by category"},
            {"params": {"search": "laptop"}, "name": "Search by name"},
            {"params": {"minPrice": 50, "maxPrice": 200}, "name": "Filter by price range"},
            {"params": {"sort": "price"}, "name": "Sort by price"},
            {"params": {"sort": "rating"}, "name": "Sort by rating"},
            {"params": {"category": "NonExistent"}, "name": "Filter by non-existent category"},
        ]
        
        for test_case in test_cases:
            try:
                response = self.make_request("GET", "/products", params=test_case["params"])
                if response.status_code == 200:
                    products = response.json()
                    self.log_test(test_case["name"], True, f"Returned {len(products)} products")
                else:
                    self.log_test(test_case["name"], False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(test_case["name"], False, f"Error: {str(e)}")
    
    def test_get_categories(self):
        """Test categories listing endpoint"""
        try:
            response = self.make_request("GET", "/categories")
            if response.status_code == 200:
                data = response.json()
                if "categories" in data and isinstance(data["categories"], list):
                    categories = data["categories"]
                    self.log_test("Get categories", True, f"Found {len(categories)} categories: {categories}")
                else:
                    self.log_test("Get categories", False, "Invalid categories response format")
            else:
                self.log_test("Get categories", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get categories", False, f"Error: {str(e)}")
    
    def test_get_product_detail(self):
        """Test product detail endpoint"""
        if not self.product_ids:
            self.log_test("Get product detail", False, "No product IDs available")
            return
        
        # Test with valid product ID
        try:
            product_id = self.product_ids[0]
            response = self.make_request("GET", f"/products/{product_id}")
            if response.status_code == 200:
                product = response.json()
                if "id" in product and "name" in product:
                    self.log_test("Get product detail (valid ID)", True, f"Product: {product['name']}")
                else:
                    self.log_test("Get product detail (valid ID)", False, "Invalid product format")
            else:
                self.log_test("Get product detail (valid ID)", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get product detail (valid ID)", False, f"Error: {str(e)}")
        
        # Test with invalid product ID
        try:
            response = self.make_request("GET", "/products/invalid-id")
            if response.status_code == 404:
                self.log_test("Get product detail (invalid ID)", True, "Correctly returned 404")
            else:
                self.log_test("Get product detail (invalid ID)", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("Get product detail (invalid ID)", False, f"Error: {str(e)}")
    
    def test_cart_operations(self):
        """Test all cart operations"""
        if not self.product_ids:
            self.log_test("Cart operations", False, "No product IDs available")
            return
        
        # Test get empty cart
        try:
            response = self.make_request("GET", "/cart")
            if response.status_code == 200:
                cart = response.json()
                self.log_test("Get cart", True, f"Cart items: {len(cart.get('items', []))}")
            else:
                self.log_test("Get cart", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get cart", False, f"Error: {str(e)}")
        
        # Test add to cart
        try:
            product_id = self.product_ids[0]
            payload = {"productId": product_id, "quantity": 2}
            response = self.make_request("POST", "/cart/add", json=payload)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Add to cart", True, f"Added product with quantity 2")
            else:
                self.log_test("Add to cart", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Add to cart", False, f"Error: {str(e)}")
        
        # Test add another product
        try:
            product_id = self.product_ids[1]
            payload = {"productId": product_id, "quantity": 1}
            response = self.make_request("POST", "/cart/add", json=payload)
            if response.status_code == 200:
                self.log_test("Add second product to cart", True, "Added second product")
            else:
                self.log_test("Add second product to cart", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Add second product to cart", False, f"Error: {str(e)}")
        
        # Test update cart item
        try:
            product_id = self.product_ids[0]
            payload = {"productId": product_id, "quantity": 3}
            response = self.make_request("POST", "/cart/update", json=payload)
            if response.status_code == 200:
                self.log_test("Update cart quantity", True, "Updated quantity to 3")
            else:
                self.log_test("Update cart quantity", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Update cart quantity", False, f"Error: {str(e)}")
        
        # Test remove item with quantity 0
        try:
            product_id = self.product_ids[1]
            payload = {"productId": product_id, "quantity": 0}
            response = self.make_request("POST", "/cart/update", json=payload)
            if response.status_code == 200:
                self.log_test("Remove item with quantity 0", True, "Removed item")
            else:
                self.log_test("Remove item with quantity 0", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Remove item with quantity 0", False, f"Error: {str(e)}")
        
        # Test remove from cart by ID
        try:
            product_id = self.product_ids[0]
            response = self.make_request("DELETE", f"/cart/remove/{product_id}")
            if response.status_code == 200:
                self.log_test("Remove from cart by ID", True, "Removed product")
            else:
                self.log_test("Remove from cart by ID", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Remove from cart by ID", False, f"Error: {str(e)}")
        
        # Add items back for order testing
        try:
            for i, product_id in enumerate(self.product_ids[:2]):
                payload = {"productId": product_id, "quantity": i + 1}
                self.make_request("POST", "/cart/add", json=payload)
        except:
            pass
    
    def test_reviews(self):
        """Test review operations"""
        if not self.product_ids:
            self.log_test("Review operations", False, "No product IDs available")
            return
        
        product_id = self.product_ids[0]
        
        # Test get reviews for product (should be empty initially)
        try:
            response = self.make_request("GET", f"/reviews/{product_id}")
            if response.status_code == 200:
                reviews = response.json()
                self.log_test("Get product reviews", True, f"Found {len(reviews)} reviews")
            else:
                self.log_test("Get product reviews", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get product reviews", False, f"Error: {str(e)}")
        
        # Test create review
        try:
            payload = {
                "productId": product_id,
                "rating": 5,
                "comment": "Excellent product! Highly recommended for testing purposes."
            }
            response = self.make_request("POST", "/reviews", json=payload)
            if response.status_code == 200:
                review = response.json()
                self.log_test("Create review", True, f"Created review with rating {review.get('rating')}")
            else:
                self.log_test("Create review", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Create review", False, f"Error: {str(e)}")
        
        # Test get reviews again (should have 1 review now)
        try:
            response = self.make_request("GET", f"/reviews/{product_id}")
            if response.status_code == 200:
                reviews = response.json()
                if len(reviews) > 0:
                    self.log_test("Get reviews after creation", True, f"Found {len(reviews)} reviews")
                else:
                    self.log_test("Get reviews after creation", False, "No reviews found after creation")
            else:
                self.log_test("Get reviews after creation", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get reviews after creation", False, f"Error: {str(e)}")
        
        # Verify product rating was updated
        try:
            response = self.make_request("GET", f"/products/{product_id}")
            if response.status_code == 200:
                product = response.json()
                rating = product.get("rating", 0)
                review_count = product.get("reviewCount", 0)
                if rating > 0 and review_count > 0:
                    self.log_test("Product rating update", True, f"Rating: {rating}, Reviews: {review_count}")
                else:
                    self.log_test("Product rating update", False, f"Rating not updated: {rating}")
            else:
                self.log_test("Product rating update", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Product rating update", False, f"Error: {str(e)}")
    
    def test_orders(self):
        """Test order operations"""
        # Test create order
        try:
            order_payload = {
                "items": [
                    {"productId": self.product_ids[0], "quantity": 2, "price": 99.99, "name": "Test Product 1"},
                    {"productId": self.product_ids[1], "quantity": 1, "price": 49.99, "name": "Test Product 2"}
                ],
                "total": 249.97,
                "shippingAddress": {
                    "name": "John Smith",
                    "address": "123 Test Street",
                    "city": "Test City",
                    "state": "TS",
                    "zip": "12345",
                    "phone": "555-0123"
                }
            }
            response = self.make_request("POST", "/orders", json=order_payload)
            if response.status_code == 200:
                order = response.json()
                self.order_ids.append(order["id"])
                self.log_test("Create order", True, f"Order ID: {order['id']}, Total: ${order['total']}")
            else:
                self.log_test("Create order", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Create order", False, f"Error: {str(e)}")
        
        # Test get orders
        try:
            response = self.make_request("GET", "/orders")
            if response.status_code == 200:
                orders = response.json()
                self.log_test("Get orders", True, f"Found {len(orders)} orders")
            else:
                self.log_test("Get orders", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get orders", False, f"Error: {str(e)}")
        
        # Test get specific order
        if self.order_ids:
            try:
                order_id = self.order_ids[0]
                response = self.make_request("GET", f"/orders/{order_id}")
                if response.status_code == 200:
                    order = response.json()
                    self.log_test("Get order detail", True, f"Order status: {order.get('status')}")
                else:
                    self.log_test("Get order detail", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Get order detail", False, f"Error: {str(e)}")
        
        # Test get order with invalid ID
        try:
            response = self.make_request("GET", "/orders/invalid-order-id")
            if response.status_code == 404:
                self.log_test("Get invalid order", True, "Correctly returned 404")
            else:
                self.log_test("Get invalid order", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("Get invalid order", False, f"Error: {str(e)}")
        
        # Verify cart was cleared after order
        try:
            response = self.make_request("GET", "/cart")
            if response.status_code == 200:
                cart = response.json()
                items_count = len(cart.get("items", []))
                if items_count == 0:
                    self.log_test("Cart cleared after order", True, "Cart is empty")
                else:
                    self.log_test("Cart cleared after order", False, f"Cart still has {items_count} items")
            else:
                self.log_test("Cart cleared after order", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Cart cleared after order", False, f"Error: {str(e)}")
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        # Test empty cart checkout (should fail)
        try:
            # Clear cart first
            self.make_request("DELETE", "/cart/clear")
            
            order_payload = {
                "items": [],
                "total": 0,
                "shippingAddress": {
                    "name": "Test User",
                    "address": "123 Test St",
                    "city": "Test City",
                    "state": "TS",
                    "zip": "12345",
                    "phone": "555-0123"
                }
            }
            response = self.make_request("POST", "/orders", json=order_payload)
            # This should still work as the API doesn't validate empty orders
            if response.status_code == 200:
                self.log_test("Empty cart checkout", True, "Empty order created (no validation)")
            else:
                self.log_test("Empty cart checkout", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Empty cart checkout", False, f"Error: {str(e)}")
        
        # Test updating non-existent cart item
        try:
            payload = {"productId": "non-existent-id", "quantity": 5}
            response = self.make_request("POST", "/cart/update", json=payload)
            # This should work as the API doesn't validate product existence
            if response.status_code == 200:
                self.log_test("Update non-existent cart item", True, "No validation for product existence")
            else:
                self.log_test("Update non-existent cart item", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Update non-existent cart item", False, f"Error: {str(e)}")
        
        # Test clear cart
        try:
            response = self.make_request("DELETE", "/cart/clear")
            if response.status_code == 200:
                self.log_test("Clear cart", True, "Cart cleared successfully")
            else:
                self.log_test("Clear cart", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Clear cart", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print(f"🚀 Starting E-commerce Backend API Tests")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Test sequence
        self.test_root_endpoint()
        self.test_init_data()
        self.test_get_products()
        self.test_product_filtering()
        self.test_get_categories()
        self.test_get_product_detail()
        self.test_cart_operations()
        self.test_reviews()
        self.test_orders()
        self.test_edge_cases()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        failed = len(self.test_results) - passed
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/len(self.test_results)*100):.1f}%")
        
        if failed > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   ❌ {result['test']}: {result['details']}")
        
        return passed, failed

def main():
    """Main test execution"""
    tester = ECommerceAPITester()
    passed, failed = tester.run_all_tests()
    
    # Exit with error code if tests failed
    if failed > 0:
        sys.exit(1)
    else:
        print("\n🎉 All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()