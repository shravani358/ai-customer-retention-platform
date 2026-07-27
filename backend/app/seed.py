from database import SessionLocal, engine, Base
import models

Base.metadata.create_all(bind=engine)

def seed():
    print("Seed function called...")  # add this line
    db = SessionLocal()
    if db.query(models.Customer).count() > 0:
        print("Already has customers, skipping.")  # add this line
        db.close()
        return


    customers = [
        models.Customer(name="TechNova Solutions", email="accounts@technova.com",
            tenure_months=3, monthly_charges=120.0, support_tickets=7, last_login_days=75),
        models.Customer(name="Apex Retail Group", email="billing@apexretail.com",
            tenure_months=5, monthly_charges=95.0, support_tickets=5, last_login_days=60),
        models.Customer(name="Sunrise Logistics", email="finance@sunriselog.com",
            tenure_months=2, monthly_charges=145.0, support_tickets=8, last_login_days=55),
        models.Customer(name="Meridian Healthcare", email="ops@meridianhc.com",
            tenure_months=14, monthly_charges=110.0, support_tickets=3, last_login_days=30),
        models.Customer(name="BlueSky Ventures", email="admin@blueskyvc.com",
            tenure_months=18, monthly_charges=75.0, support_tickets=2, last_login_days=25),
        models.Customer(name="Granite Financial", email="accounts@granitefinancial.com",
            tenure_months=24, monthly_charges=130.0, support_tickets=1, last_login_days=18),
        models.Customer(name="Evergreen Media", email="hello@evergreenmedia.com",
            tenure_months=36, monthly_charges=85.0, support_tickets=1, last_login_days=5),
        models.Customer(name="Pinnacle Engineering", email="finance@pinnacleeng.com",
            tenure_months=48, monthly_charges=150.0, support_tickets=0, last_login_days=3),
        models.Customer(name="Atlas Global Corp", email="billing@atlasglobal.com",
            tenure_months=60, monthly_charges=200.0, support_tickets=0, last_login_days=1),
        models.Customer(name="Horizon Pharma", email="accounts@horizonpharma.com",
            tenure_months=55, monthly_charges=175.0, support_tickets=0, last_login_days=2),
    ]
    db.add_all(customers)
    db.commit()
    db.close()
    print("Database seeded with 10 customers.")

if __name__ == "__main__":
    seed()