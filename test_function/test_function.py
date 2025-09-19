#!/usr/bin/env python3
"""
Test script for the Azure Function - Cosmos DB integration
"""

import requests
import json
import time
import sys

def test_health_endpoint():
    """Test the health check endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get('http://localhost:7071/api/health')
        print(f"Health check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Health check failed: {e}")
        return False

def test_add_items():
    """Test adding items from sample data"""
    print("\nTesting add_item endpoint...")
    
    # Load sample data
    try:
        with open('sample_data.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("sample_data.json not found!")
        return False
    
    success_count = 0
    total_items = len(data['sample_items'])
    
    for i, item in enumerate(data['sample_items'], 1):
        print(f"\nTesting item {i}/{total_items}: {item['name']}")
        try:
            response = requests.post(
                'http://localhost:7071/api/add_item',
                json=item,
                timeout=10
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Success: {result['message']}")
                success_count += 1
            elif response.status_code == 409:
                print(f"⚠️  Item already exists: {item['id']}")
                success_count += 1  # Count as success for testing purposes
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        
        # Small delay between requests
        time.sleep(0.5)
    
    print(f"\nResults: {success_count}/{total_items} items processed successfully")
    return success_count == total_items

def test_error_handling():
    """Test error handling with invalid data"""
    print("\nTesting error handling...")
    
    # Test missing required field
    invalid_item = {"name": "Test without ID"}
    try:
        response = requests.post(
            'http://localhost:7071/api/add_item',
            json=invalid_item,
            timeout=10
        )
        if response.status_code == 400:
            print("✅ Error handling works: Missing ID field properly rejected")
        else:
            print(f"❌ Expected 400 error, got {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    # Test empty body
    try:
        response = requests.post(
            'http://localhost:7071/api/add_item',
            json={},
            timeout=10
        )
        if response.status_code == 400:
            print("✅ Error handling works: Empty body properly rejected")
        else:
            print(f"❌ Expected 400 error, got {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

def main():
    """Main test function"""
    print("Azure Function - Cosmos DB Test Script")
    print("=" * 50)
    
    # Test health endpoint first
    if not test_health_endpoint():
        print("\n❌ Health check failed. Make sure the function is running with 'func start'")
        sys.exit(1)
    
    # Test adding items
    if not test_add_items():
        print("\n⚠️  Some items failed to add. Check the function logs for details.")
    
    # Test error handling
    test_error_handling()
    
    print("\n🎉 Testing completed!")
    print("\nTo view the data in Cosmos DB:")
    print("- If using emulator: https://localhost:8081/_explorer/index.html")
    print("- If using Azure: Check your Cosmos DB account in Azure portal")

if __name__ == "__main__":
    main()