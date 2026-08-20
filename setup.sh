#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Sales Customer 360 - Setup Script${NC}\n"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose are installed${NC}\n"

# Step 1: Start services
echo -e "${BLUE}📦 Starting Docker services...${NC}"
docker-compose up -d

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Failed to start Docker services${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker services started${NC}\n"

# Step 2: Wait for PostgreSQL
echo -e "${BLUE}⏳ Waiting for PostgreSQL to be ready...${NC}"
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U user > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PostgreSQL is ready${NC}\n"
        break
    fi
    sleep 1
done

# Step 3: Seed database
echo -e "${BLUE}🌱 Seeding database with sample data...${NC}"
docker-compose exec -T backend python seed.py

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Failed to seed database${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Database seeded successfully${NC}\n"

# Step 4: Install frontend dependencies
echo -e "${BLUE}📦 Installing frontend dependencies...${NC}"
docker-compose exec -T frontend npm install

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Failed to install frontend dependencies${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Frontend dependencies installed${NC}\n"

# Step 5: Summary
echo -e "${GREEN}✅ Setup complete!${NC}\n"

echo -e "${BLUE}📋 Access the application:${NC}"
echo -e "   • Frontend: ${YELLOW}http://localhost:3000${NC}"
echo -e "   • API: ${YELLOW}http://localhost:8000${NC}"
echo -e "   • API Docs: ${YELLOW}http://localhost:8000/docs${NC}"
echo -e "   • Database: ${YELLOW}postgres://user:password@localhost:5432/sales_customer_360${NC}\n"

echo -e "${BLUE}🔑 Test Users:${NC}"
echo -e "   • mario_rossi (Sales)"
echo -e "   • lucia_bianchi (Sales)"
echo -e "   • anna_marini (Sales Manager)"
echo -e "   • carlo_romano (BU Manager)"
echo -e "   • stefano_ferrara (Executive)"
echo -e "   • admin (Administrator)"
echo -e "   Password: ${YELLOW}password123${NC}\n"

echo -e "${BLUE}📚 Documentation:${NC}"
echo -e "   • QUICKSTART.md - Quick start guide"
echo -e "   • ARCHITECTURE.md - Full system design"
echo -e "   • README.md - Project overview\n"

echo -e "${BLUE}🛑 To stop services:${NC}"
echo -e "   docker-compose down\n"

echo -e "${BLUE}📊 To view logs:${NC}"
echo -e "   docker-compose logs -f <service>\n"
