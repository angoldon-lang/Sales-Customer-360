#!/bin/bash

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
while ! nc -z postgres 5432; do
  sleep 1
done

echo "✓ PostgreSQL is ready"

# Run seed script
echo "Seeding database..."
python seed.py

if [ $? -eq 0 ]; then
  echo "✓ Database seeded successfully"
else
  echo "✗ Database seeding failed"
  exit 1
fi
