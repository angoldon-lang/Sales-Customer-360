"""
Seed script to populate database with sample data.
Run: python seed.py
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal, Base
from app.models import (
    User, Role, Permission,
    ProductCategory, ProductVendor, Product,
    ServiceCategory, Service, ServiceLevel,
    Customer, CustomerContact, CustomerAccount,
    Contract,
    ConversionRule,
)
from app.routers.auth import get_password_hash


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")


def seed_roles_and_permissions(db: Session):
    """Create roles and permissions."""
    roles_data = [
        ("sales", "Sales Representative"),
        ("sales_manager", "Sales Manager"),
        ("bu_manager", "Business Unit Manager"),
        ("direzione", "Executive Direction"),
        ("admin", "Administrator"),
        ("data_steward", "Data Steward"),
    ]

    for role_name, role_desc in roles_data:
        existing = db.query(Role).filter(Role.name == role_name).first()
        if not existing:
            role = Role(name=role_name, description=role_desc)
            db.add(role)

    db.commit()
    print("✓ Roles created")


def seed_users(db: Session):
    """Create sample users."""
    users_data = [
        ("mario_rossi", "mario.rossi@adconsulting.it", "Mario Rossi", "sales", "Security", "Milan Team"),
        ("lucia_bianchi", "lucia.bianchi@adconsulting.it", "Lucia Bianchi", "sales", "Cloud", "Rome Team"),
        ("giuseppe_verdi", "giuseppe.verdi@adconsulting.it", "Giuseppe Verdi", "sales", "Infrastructure", "Milan Team"),
        ("anna_marini", "anna.marini@adconsulting.it", "Anna Marini", "sales_manager", "Security", "Milan Team"),
        ("carlo_romano", "carlo.romano@adconsulting.it", "Carlo Romano", "bu_manager", "Security", None),
        ("francesca_longo", "francesca.longo@adconsulting.it", "Francesca Longo", "bu_manager", "Cloud", None),
        ("stefano_ferrara", "stefano.ferrara@adconsulting.it", "Stefano Ferrara", "direzione", None, None),
        ("admin", "admin@adconsulting.it", "Admin User", "admin", None, None),
    ]

    for username, email, full_name, role_name, bu, team in users_data:
        existing = db.query(User).filter(User.username == username).first()
        if not existing:
            role = db.query(Role).filter(Role.name == role_name).first()
            user = User(
                username=username,
                email=email,
                full_name=full_name,
                hashed_password=get_password_hash("password123"),
                role_id=role.id if role else None,
                business_unit=bu,
                team=team,
                is_active=True,
                is_admin=(role_name == "admin")
            )
            db.add(user)

    db.commit()
    print("✓ Users created (password: password123)")


def seed_product_categories_and_vendors(db: Session):
    """Create product categories and vendors."""
    categories = [
        ("Security", "Security products and services"),
        ("Cloud", "Cloud infrastructure and services"),
        ("Infrastructure", "Infrastructure management"),
        ("Collaboration", "Collaboration and productivity tools"),
        ("Database", "Database and data management"),
    ]

    for name, description in categories:
        existing = db.query(ProductCategory).filter(ProductCategory.name == name).first()
        if not existing:
            cat = ProductCategory(name=name, description=description)
            db.add(cat)

    vendors = [
        ("Fortinet", "https://www.fortinet.com"),
        ("Palo Alto Networks", "https://www.paloaltonetworks.com"),
        ("Microsoft", "https://www.microsoft.com"),
        ("Veeam", "https://www.veeam.com"),
        ("SolarWinds", "https://www.solarwinds.com"),
        ("VMware", "https://www.vmware.com"),
        ("Nutanix", "https://www.nutanix.com"),
        ("Redgate", "https://www.redgate.com"),
    ]

    for name, website in vendors:
        existing = db.query(ProductVendor).filter(ProductVendor.name == name).first()
        if not existing:
            vendor = ProductVendor(name=name, website=website)
            db.add(vendor)

    db.commit()
    print("✓ Product categories and vendors created")


def seed_products(db: Session):
    """Create sample products."""
    products_data = [
        ("Fortinet FortiGate 500E", "Security", "Fortinet", "FortiGate-500E", "firewall", "subscription", 15000, 40),
        ("Palo Alto PA-5220", "Security", "Palo Alto Networks", "PA-5220", "firewall", "subscription", 28000, 45),
        ("Microsoft 365 E5", "Collaboration", "Microsoft", "M365-E5", "cloud_saas", "subscription", 8500, 35),
        ("Veeam Backup Standard", "Infrastructure", "Veeam", "Veeam-Backup-Std", "backup", "subscription", 5000, 50),
        ("SolarWinds Orion Platform", "Infrastructure", "SolarWinds", "SolarWinds-Orion", "monitoring", "subscription", 12000, 40),
        ("VMware vSphere Enterprise", "Infrastructure", "VMware", "vSphere-Ent", "virtualization", "perpetual", 35000, 35),
        ("Nutanix Enterprise Cloud", "Infrastructure", "Nutanix", "Nutanix-EC", "hyperconverged", "subscription", 45000, 40),
        ("Redgate SQL Toolbelt", "Database", "Redgate", "SQL-Toolbelt", "database_tools", "perpetual", 3000, 60),
    ]

    for name, category_name, vendor_name, sku, product_type, license_type, price, margin in products_data:
        existing = db.query(Product).filter(Product.sku == sku).first()
        if not existing:
            category = db.query(ProductCategory).filter(ProductCategory.name == category_name).first()
            vendor = db.query(ProductVendor).filter(ProductVendor.name == vendor_name).first()

            product = Product(
                name=name,
                sku=sku,
                category_id=category.id if category else None,
                vendor_id=vendor.id if vendor else None,
                product_type=product_type,
                license_type=license_type,
                list_price=price,
                margin_expectation=margin,
                is_active=1,
            )
            db.add(product)

    db.commit()
    print("✓ Products created")


def seed_services(db: Session):
    """Create sample services."""
    service_categories = [
        ("Security Services", "Security managed services"),
        ("Infrastructure Services", "Infrastructure management"),
        ("Backup Services", "Data backup and recovery"),
        ("Monitoring Services", "Monitoring and alerting"),
    ]

    for name, description in service_categories:
        existing = db.query(ServiceCategory).filter(ServiceCategory.name == name).first()
        if not existing:
            cat = ServiceCategory(name=name, description=description)
            db.add(cat)

    db.commit()

    services_data = [
        ("Managed Firewall", "Security Services", "Security", "Fortinet, Palo Alto, Cisco ASA", "managed", "monthly", 3000, 2000, 4000, 40),
        ("Managed Modern Workplace", "Security Services", "Cloud", "Microsoft 365, Office 365", "managed", "monthly", 2500, 1500, 3500, 35),
        ("Backup Managed Service", "Backup Services", "Infrastructure", "Veeam, Commvault, NetBackup", "managed", "monthly", 2000, 1000, 3000, 50),
        ("Monitoring as a Service", "Monitoring Services", "Infrastructure", "SolarWinds, DataDog, New Relic", "managed", "monthly", 1500, 800, 2500, 40),
        ("Infrastructure Managed Service", "Infrastructure Services", "Infrastructure", "VMware, Nutanix, Hyper-V", "managed", "monthly", 4000, 2500, 6000, 35),
        ("DBA as a Service", "Infrastructure Services", "Infrastructure", "Redgate, Oracle, SQL Server", "consulting", "monthly", 3500, 2000, 5000, 45),
    ]

    for name, category_name, bu, description, service_type, billing, price, price_min, price_max, margin in services_data:
        existing = db.query(Service).filter(Service.name == name).first()
        if not existing:
            category = db.query(ServiceCategory).filter(ServiceCategory.name == category_name).first()

            service = Service(
                name=name,
                description=description,
                category_id=category.id if category else None,
                business_unit=bu,
                service_type=service_type,
                billing_type=billing,
                indicative_price=price,
                price_range_min=price_min,
                price_range_max=price_max,
                margin_expectation=margin,
                is_active=True,
                is_recommended=True,
            )
            db.add(service)

    db.commit()
    print("✓ Services created")


def seed_customers(db: Session):
    """Create sample customers."""
    customers_data = [
        ("Acme Corporation", "Acme Corp SpA", "IT01234567890", "Technology", "Mid-Market", "Italy", "Milano", 2500),
        ("Tech Solutions Ltd", "Tech Solutions Ltd", "GB98765432100", "Technology", "Mid-Market", "UK", "London", 1800),
        ("Global Industries", "Global Ind. GmbH", "DE12345678901", "Manufacturing", "Enterprise", "Germany", "Berlin", 5000),
        ("Prime Consulting", "Prime Consulting SPA", "IT11111111111", "Consulting", "Mid-Market", "Italy", "Roma", 2200),
        ("Digital Ventures", "Digital Ventures Inc", "US98765432109", "Startup", "Mid-Market", "USA", "San Francisco", 800),
    ]

    for name, legal_name, vat, industry, sector, country, city, employees in customers_data:
        existing = db.query(Customer).filter(Customer.vat_number == vat).first()
        if not existing:
            customer = Customer(
                name=name,
                legal_name=legal_name,
                vat_number=vat,
                industry=industry,
                sector=sector,
                country=country,
                city=city,
                employee_count=employees,
                status="active",
                data_quality_score=85,
            )
            db.add(customer)

    db.commit()
    print("✓ Customers created")


def seed_customer_accounts(db: Session):
    """Create customer accounts."""
    customers = db.query(Customer).all()
    sales_users = db.query(User).filter(User.role.has(Role.name.in_(["sales", "sales_manager"]))).all()

    if customers and sales_users:
        for idx, customer in enumerate(customers):
            account_owner = sales_users[idx % len(sales_users)]

            account = CustomerAccount(
                customer_id=customer.id,
                name=f"{customer.name} - Main Account",
                account_owner_id=account_owner.id,
                business_unit=account_owner.business_unit or "General",
                team=account_owner.team,
                annual_value=50000 + (idx * 10000),
                pipeline_value=20000 + (idx * 5000),
                renewal_date=datetime.utcnow() + timedelta(days=180 + idx * 30),
            )
            db.add(account)

        db.commit()
        print("✓ Customer accounts created")


def seed_contracts(db: Session):
    """Create sample contracts."""
    customers = db.query(Customer).all()
    products = db.query(Product).all()

    if customers and products:
        contract_data = [
            (0, 0, 15000, "2023-06-15", "2026-06-15"),
            (1, 2, 8500, "2023-09-20", "2025-09-20"),
            (2, 1, 28000, "2023-03-15", "2026-03-15"),
            (3, 3, 5000, "2022-11-10", "2024-11-10"),
            (4, 4, 12000, "2023-01-30", "2026-01-30"),
        ]

        for customer_idx, product_idx, value, start_date_str, end_date_str in contract_data:
            if customer_idx < len(customers) and product_idx < len(products):
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

                contract = Contract(
                    customer_id=customers[customer_idx].id,
                    product_id=products[product_idx].id,
                    contract_number=f"CT-{2023 + customer_idx}-{1000 + customer_idx}",
                    start_date=start_date,
                    end_date=end_date,
                    renewal_date=end_date,
                    annual_value=value,
                    payment_frequency="annual",
                    status="active",
                    is_auto_renewal=True,
                )
                db.add(contract)

        db.commit()
        print("✓ Contracts created")


def seed_conversion_rules(db: Session):
    """Create conversion rules."""
    products = {p.sku: p for p in db.query(Product).all()}
    services = {s.name: s for s in db.query(Service).all()}

    rules_data = [
        ("Firewall to Managed Service", "Propose Managed Firewall for Fortinet/Palo Alto",
         "FortiGate-500E", "Managed Firewall", 36, True, "high"),
        ("Cloud Suite to Managed Workplace", "Propose Managed Modern Workplace for Microsoft 365",
         "M365-E5", "Managed Modern Workplace", 24, True, "high"),
        ("Backup to Managed Service", "Propose Backup Managed Service",
         "Veeam-Backup-Std", "Backup Managed Service", 36, True, "medium"),
        ("Monitoring to Service", "Propose Monitoring as a Service",
         "SolarWinds-Orion", "Monitoring as a Service", 24, True, "medium"),
    ]

    for name, description, trigger_sku, service_name, months, requires_no_service, priority in rules_data:
        existing = db.query(ConversionRule).filter(ConversionRule.name == name).first()
        if not existing and trigger_sku in products and service_name in services:
            rule = ConversionRule(
                name=name,
                description=description,
                trigger_product_id=products[trigger_sku].id,
                recommended_service_id=services[service_name].id,
                months_lookback=months,
                requires_no_service=requires_no_service,
                priority=priority,
                is_active=True,
            )
            db.add(rule)

    db.commit()
    print("✓ Conversion rules created")


def main():
    """Run all seed functions."""
    print("\n🌱 Starting database seeding...\n")

    create_tables()
    db = SessionLocal()

    try:
        seed_roles_and_permissions(db)
        seed_users(db)
        seed_product_categories_and_vendors(db)
        seed_products(db)
        seed_services(db)
        seed_customers(db)
        seed_customer_accounts(db)
        seed_contracts(db)
        seed_conversion_rules(db)

        print("\n✅ Database seeding completed!\n")
        print("📋 Test Users:")
        print("   - mario_rossi (Sales) - Security BU")
        print("   - lucia_bianchi (Sales) - Cloud BU")
        print("   - anna_marini (Sales Manager) - Security BU")
        print("   - carlo_romano (BU Manager) - Security")
        print("   - stefano_ferrara (Executive)")
        print("   - admin (Admin)")
        print("\n🔑 Default password: password123\n")

    finally:
        db.close()


if __name__ == "__main__":
    main()
