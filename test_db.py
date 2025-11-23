# test_db.py
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_manager.settings')
django.setup()

# Import your model
from app.models import Inventory  # Make sure 'app' is the name of your Django app

# Fetch and print all Inventory records
print("Fetching all Inventory records:")
for item in Inventory.objects.all():
    print(f"ID: {item.id}, Name: {item.name}, Quantity: {item.quantity}, Date: {item.date}, Description: {item.description}, Preview: {item.preview}")
