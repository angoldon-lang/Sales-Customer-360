#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Customer Intelligence Monitor - Setup Script${NC}\n"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python 3 is not installed. Please install Python 3.11+ first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python 3 is installed${NC}\n"

# Step 1: Create virtual environment
echo -e "${BLUE}📦 Creating Python virtual environment...${NC}"
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Failed to create virtual environment${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Virtual environment created${NC}\n"

# Step 2: Install dependencies
echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Failed to install dependencies${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Dependencies installed${NC}\n"

# Step 3: Setup .env
echo -e "${BLUE}⚙️  Setting up .env configuration...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created (please edit with your settings)${NC}\n"
else
    echo -e "${GREEN}✓ .env file already exists${NC}\n"
fi

# Step 4: Initialize database
echo -e "${BLUE}🗄️  Initializing SQLite database...${NC}"
python -c "from app.database import init_db; init_db()"

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Failed to initialize database${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Database initialized${NC}\n"

# Step 5: Run tests
echo -e "${BLUE}🧪 Running tests...${NC}"
pytest tests/ -v

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed${NC}\n"
else
    echo -e "${YELLOW}⚠️  Some tests failed (non-critical)${NC}\n"
fi

cd ..

# Final Summary
echo -e "${GREEN}✅ Setup complete!${NC}\n"

echo -e "${BLUE}📋 To start the application:${NC}"
echo -e "   cd backend"
echo -e "   source venv/bin/activate"
echo -e "   uvicorn app.main:app --reload\n"

echo -e "${BLUE}📍 Access points:${NC}"
echo -e "   • API: ${YELLOW}http://localhost:8000${NC}"
echo -e "   • API Docs (Swagger): ${YELLOW}http://localhost:8000/docs${NC}"
echo -e "   • Database file: ${YELLOW}backend/customer_intelligence.db${NC}\n"

echo -e "${BLUE}📚 Documentation:${NC}"
echo -e "   • README.md - Project overview and features"
echo -e "   • ARCHITECTURE.md - System design and modules"
echo -e "   • QUICKSTART.md - Getting started guide\n"

echo -e "${BLUE}🧪 Run Tests:${NC}"
echo -e "   cd backend"
echo -e "   pytest tests/\n"

echo -e "${BLUE}📊 Import Sample Companies:${NC}"
echo -e "   1. Create companies.csv with format:"
echo -e "      company_name,vat_number,cluster"
echo -e "   2. POST to http://localhost:8000/api/import/companies/csv\n"
