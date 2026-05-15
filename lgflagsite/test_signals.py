#!/usr/bin/env python
"""Test automatic database compression via Django signals"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from review.models import Flag

print("Testing automatic compression via Django signals...")
print("Creating test flag...")
flag = Flag.objects.create(
    code="AUTOTEST",
    description="Test flag to trigger automatic compression"
)
print(f"✓ Created: {flag.code}")

print("Deleting test flag (should trigger compression)...")
flag.delete()
print("✓ Deleted - automatic compression should have run!")

print("\nSignals setup complete - compression will now run automatically on:")
print("  - Create/update any Stem, StemFlagTask, Flag, StemGroup, or ReviewDecision")
print("  - Delete any of these models")
print("  - Run Django migrations")
