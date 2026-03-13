"""Seed the database with jewelry products, users, and preferences."""
from datetime import datetime, timedelta
from app.db.database import SessionLocal, engine
from app.db import Base
from app.models.models import User, Preference, Item, Session, Message
from app.auth import hash_password

PRODUCTS = [
    # Rings
    {"name": "Diamond Solitaire Ring", "category": "Rings", "subcategory": "Engagement", "price": 2499.00, "original_price": 2899.00, "description": "A breathtaking 1-carat round brilliant diamond set in 18K white gold. The timeless solitaire setting lets the diamond speak for itself.", "image_url": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=600", "rating": 4.9, "reviews_count": 284, "featured": 1, "attributes": {"style": "classic", "metal": "white gold", "stone": "diamond"}},
    {"name": "Rose Gold Infinity Band", "category": "Rings", "subcategory": "Wedding", "price": 899.00, "original_price": 899.00, "description": "Delicate infinity-twist band crafted in 14K rose gold with pavé-set diamonds. A symbol of eternal love.", "image_url": "https://images.unsplash.com/photo-1603561591411-07134e71a2a9?w=600", "rating": 4.7, "reviews_count": 156, "featured": 1, "attributes": {"style": "modern", "metal": "rose gold", "stone": "diamond"}},
    {"name": "Sapphire Halo Ring", "category": "Rings", "subcategory": "Cocktail", "price": 1899.00, "original_price": 2100.00, "description": "Oval blue sapphire surrounded by a halo of brilliant diamonds in platinum setting. Royally inspired elegance.", "image_url": "https://images.unsplash.com/photo-1598560917505-59a3ad559071?w=600", "rating": 4.8, "reviews_count": 198, "featured": 0, "attributes": {"style": "vintage", "metal": "platinum", "stone": "sapphire"}},
    {"name": "Platinum Eternity Ring", "category": "Rings", "subcategory": "Wedding", "price": 3200.00, "original_price": 3200.00, "description": "Full eternity band with 2.5ct total weight round diamonds channel-set in platinum. Unbroken circle of brilliance.", "image_url": "https://images.unsplash.com/photo-1611955167811-4711904bb9f8?w=600", "rating": 4.6, "reviews_count": 89, "featured": 0, "attributes": {"style": "classic", "metal": "platinum", "stone": "diamond"}},
    {"name": "Gold Signet Ring", "category": "Rings", "subcategory": "Statement", "price": 650.00, "original_price": 750.00, "description": "Bold 18K yellow gold signet ring with brushed finish. A modern take on a heritage classic, perfect for everyday wear.", "image_url": "https://images.unsplash.com/photo-1543294001-f7cd5d7fb516?w=600", "rating": 4.5, "reviews_count": 312, "featured": 0, "attributes": {"style": "statement", "metal": "yellow gold", "stone": "none"}},

    # Necklaces
    {"name": "Diamond Pendant Necklace", "category": "Necklaces", "subcategory": "Pendant", "price": 1299.00, "original_price": 1499.00, "description": "Brilliant round diamond pendant on a delicate 18K white gold chain. The perfect everyday luxury piece.", "image_url": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=600", "rating": 4.8, "reviews_count": 423, "featured": 1, "attributes": {"style": "delicate", "metal": "white gold", "stone": "diamond"}},
    {"name": "Pearl Strand Necklace", "category": "Necklaces", "subcategory": "Classic", "price": 1599.00, "original_price": 1599.00, "description": "Lustrous Akoya cultured pearl strand with 18K gold clasp. 7-7.5mm pearls hand-selected for matching luster.", "image_url": "https://images.unsplash.com/photo-1515562141589-67f0d54eb715?w=600", "rating": 4.9, "reviews_count": 267, "featured": 1, "attributes": {"style": "classic", "metal": "yellow gold", "stone": "pearl"}},
    {"name": "Gold Chain Choker", "category": "Necklaces", "subcategory": "Choker", "price": 749.00, "original_price": 749.00, "description": "Sleek Italian-made curb chain choker in 14K yellow gold. Adjustable length for versatile styling.", "image_url": "https://images.unsplash.com/photo-1611085583191-a3b181a88401?w=600", "rating": 4.5, "reviews_count": 178, "featured": 0, "attributes": {"style": "modern", "metal": "yellow gold", "stone": "none"}},
    {"name": "Emerald Drop Necklace", "category": "Necklaces", "subcategory": "Statement", "price": 2799.00, "original_price": 3100.00, "description": "Pear-shaped Colombian emerald with diamond accents on an 18K white gold chain. Show-stopping green fire.", "image_url": "https://images.unsplash.com/photo-1506630448388-4e683c67ddb0?w=600", "rating": 4.7, "reviews_count": 134, "featured": 0, "attributes": {"style": "statement", "metal": "white gold", "stone": "emerald"}},
    {"name": "Layered Gold Necklace", "category": "Necklaces", "subcategory": "Layered", "price": 499.00, "original_price": 599.00, "description": "Triple-layer 14K gold necklace set with satellite chain, bar pendant, and coin charm. Effortless modern elegance.", "image_url": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=600", "rating": 4.6, "reviews_count": 521, "featured": 0, "attributes": {"style": "modern", "metal": "yellow gold", "stone": "none"}},

    # Earrings
    {"name": "Diamond Stud Earrings", "category": "Earrings", "subcategory": "Studs", "price": 1799.00, "original_price": 1799.00, "description": "Classic round brilliant diamond studs totaling 1ct in 14K white gold 4-prong settings. The essential jewelry wardrobe piece.", "image_url": "https://images.unsplash.com/photo-1535632787350-4e68ef0ac584?w=600", "rating": 4.9, "reviews_count": 687, "featured": 1, "attributes": {"style": "classic", "metal": "white gold", "stone": "diamond"}},
    {"name": "Pearl Drop Earrings", "category": "Earrings", "subcategory": "Drop", "price": 599.00, "original_price": 699.00, "description": "South Sea pearl drops on 18K gold wire. Each pearl uniquely lustrous with a soft champagne overtone.", "image_url": "https://images.unsplash.com/photo-1588444837495-c6cfeb53f32d?w=600", "rating": 4.6, "reviews_count": 234, "featured": 0, "attributes": {"style": "delicate", "metal": "yellow gold", "stone": "pearl"}},
    {"name": "Gold Hoop Earrings", "category": "Earrings", "subcategory": "Hoops", "price": 450.00, "original_price": 450.00, "description": "Medium-size tubular hoops in polished 14K yellow gold. Lightweight with secure click-top closure.", "image_url": "https://images.unsplash.com/photo-1630019852942-f89202989a59?w=600", "rating": 4.7, "reviews_count": 445, "featured": 0, "attributes": {"style": "modern", "metal": "yellow gold", "stone": "none"}},
    {"name": "Ruby Chandelier Earrings", "category": "Earrings", "subcategory": "Chandelier", "price": 2299.00, "original_price": 2500.00, "description": "Cascading Burmese rubies and diamonds in 18K white gold. A dramatic statement for special evenings.", "image_url": "https://images.unsplash.com/photo-1617038260897-41a1f14a8ca0?w=600", "rating": 4.8, "reviews_count": 112, "featured": 1, "attributes": {"style": "statement", "metal": "white gold", "stone": "ruby"}},
    {"name": "Platinum Huggie Earrings", "category": "Earrings", "subcategory": "Huggie", "price": 899.00, "original_price": 899.00, "description": "Sleek platinum huggie hoops with a row of pavé diamonds. Sits close to the ear for modern minimalism.", "image_url": "https://images.unsplash.com/photo-1611652022419-a9419f74343d?w=600", "rating": 4.5, "reviews_count": 198, "featured": 0, "attributes": {"style": "modern", "metal": "platinum", "stone": "diamond"}},

    # Bracelets
    {"name": "Diamond Tennis Bracelet", "category": "Bracelets", "subcategory": "Tennis", "price": 4599.00, "original_price": 4599.00, "description": "5ct total weight round diamonds in 18K white gold tennis setting. Timeless elegance with secure box clasp.", "image_url": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=600", "rating": 4.9, "reviews_count": 312, "featured": 1, "attributes": {"style": "classic", "metal": "white gold", "stone": "diamond"}},
    {"name": "Gold Charm Bracelet", "category": "Bracelets", "subcategory": "Charm", "price": 799.00, "original_price": 899.00, "description": "14K yellow gold link bracelet with five interchangeable charms. Build your story one charm at a time.", "image_url": "https://images.unsplash.com/photo-1573408301185-9146fe634ad0?w=600", "rating": 4.6, "reviews_count": 267, "featured": 0, "attributes": {"style": "modern", "metal": "yellow gold", "stone": "mixed"}},
    {"name": "Rose Gold Cuff Bracelet", "category": "Bracelets", "subcategory": "Cuff", "price": 1199.00, "original_price": 1199.00, "description": "Wide hammered cuff in 14K rose gold. A bold sculptural piece that makes a statement on its own.", "image_url": "https://images.unsplash.com/photo-1602751584552-8ba73aad10e1?w=600", "rating": 4.4, "reviews_count": 156, "featured": 0, "attributes": {"style": "statement", "metal": "rose gold", "stone": "none"}},
    {"name": "Pearl & Gold Bracelet", "category": "Bracelets", "subcategory": "Beaded", "price": 699.00, "original_price": 799.00, "description": "Freshwater pearls alternating with 14K gold beads on silk cord. Elegance meets ease.", "image_url": "https://images.unsplash.com/photo-1611652022419-a9419f74343d?w=600", "rating": 4.7, "reviews_count": 189, "featured": 0, "attributes": {"style": "delicate", "metal": "yellow gold", "stone": "pearl"}},

    # Pendants
    {"name": "Heart Diamond Pendant", "category": "Pendants", "subcategory": "Heart", "price": 1099.00, "original_price": 1299.00, "description": "Heart-shaped diamond cluster pendant in 18K rose gold. A romantic gesture captured in precious metal.", "image_url": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=600", "rating": 4.8, "reviews_count": 345, "featured": 1, "attributes": {"style": "delicate", "metal": "rose gold", "stone": "diamond"}},
    {"name": "Evil Eye Gold Pendant", "category": "Pendants", "subcategory": "Symbolic", "price": 399.00, "original_price": 399.00, "description": "18K gold evil eye pendant with sapphire center and diamond surround. Protection meets luxury.", "image_url": "https://images.unsplash.com/photo-1611085583191-a3b181a88401?w=600", "rating": 4.5, "reviews_count": 234, "featured": 0, "attributes": {"style": "modern", "metal": "yellow gold", "stone": "sapphire"}},
    {"name": "Vintage Locket Pendant", "category": "Pendants", "subcategory": "Locket", "price": 549.00, "original_price": 649.00, "description": "Engraved oval locket in 14K gold with space for two photos. A treasured keepsake for generations.", "image_url": "https://images.unsplash.com/photo-1506630448388-4e683c67ddb0?w=600", "rating": 4.6, "reviews_count": 178, "featured": 0, "attributes": {"style": "vintage", "metal": "yellow gold", "stone": "none"}},
    {"name": "Sapphire Drop Pendant", "category": "Pendants", "subcategory": "Drop", "price": 1799.00, "original_price": 1799.00, "description": "Pear-cut sapphire suspended from a diamond bail in platinum. Deep blue intensity that captivates.", "image_url": "https://images.unsplash.com/photo-1515562141589-67f0d54eb715?w=600", "rating": 4.7, "reviews_count": 112, "featured": 0, "attributes": {"style": "classic", "metal": "platinum", "stone": "sapphire"}},

    # Watches
    # Bangles
    {"name": "Gold Kada Bangle Set", "category": "Bangles", "subcategory": "Traditional", "price": 2199.00, "original_price": 2199.00, "description": "Set of two ornate 22K gold kada bangles with intricate filigree work. Heritage craftsmanship for modern celebrations.", "image_url": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=600", "rating": 4.8, "reviews_count": 198, "featured": 1, "attributes": {"style": "classic", "metal": "yellow gold", "stone": "none"}},
    {"name": "Diamond Studded Bangle", "category": "Bangles", "subcategory": "Luxury", "price": 3999.00, "original_price": 4299.00, "description": "18K white gold bangle studded with 3ct total weight diamonds in a seamless channel setting.", "image_url": "https://images.unsplash.com/photo-1573408301185-9146fe634ad0?w=600", "rating": 4.7, "reviews_count": 145, "featured": 0, "attributes": {"style": "statement", "metal": "white gold", "stone": "diamond"}},
    {"name": "Enamel Art Bangle Set", "category": "Bangles", "subcategory": "Fashion", "price": 599.00, "original_price": 699.00, "description": "Set of three stackable bangles in gold-plated brass with hand-painted enamel art. Vibrant meets elegant.", "image_url": "https://images.unsplash.com/photo-1611652022419-a9419f74343d?w=600", "rating": 4.4, "reviews_count": 312, "featured": 0, "attributes": {"style": "modern", "metal": "gold plated", "stone": "none"}},
]


def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Item).count() > 0:
            return

        # Products
        for p in PRODUCTS:
            db.add(Item(**p))
        db.commit()

        # Admin user
        admin = User(
            name="Admin",
            email="admin@tanishq.com",
            password_hash=hash_password("Admin@123"),
            role="admin",
            segment="returning",
            email_verified=1,
            created_at=datetime.utcnow() - timedelta(days=60),
            last_seen=datetime.utcnow(),
        )
        db.add(admin)
        db.commit()

        # Sample users
        u1 = User(
            name="Priya Sharma",
            email="priya@tanishq.com",
            password_hash=hash_password("User@123"),
            role="user",
            segment="returning",
            email_verified=1,
            created_at=datetime.utcnow() - timedelta(days=30),
            last_seen=datetime.utcnow() - timedelta(days=1),
        )
        u2 = User(
            name="Rahul Mehta",
            email="rahul@tanishq.com",
            password_hash=hash_password("User@123"),
            role="user",
            segment="new",
            email_verified=1,
            created_at=datetime.utcnow() - timedelta(days=5),
            last_seen=datetime.utcnow() - timedelta(days=2),
        )
        db.add_all([u1, u2])
        db.commit()

        # Preferences
        p1 = Preference(user_id=u1.id, categories=["Rings", "Necklaces"], styles=["classic", "delicate"], past_likes=[1, 6, 11], past_dislikes=[])
        p2 = Preference(user_id=u2.id, categories=["Bangles", "Bracelets"], styles=["modern"], past_likes=[20, 17], past_dislikes=[])
        db.add_all([p1, p2])
        db.commit()

        # Sample sessions
        s1 = Session(id="sess_priya_001", user_id=u1.id, started_at=datetime.utcnow() - timedelta(days=1), path="preference", message_count=4)
        s2 = Session(id="sess_rahul_001", user_id=u2.id, started_at=datetime.utcnow() - timedelta(days=2), path="need_state", message_count=3)
        db.add_all([s1, s2])
        db.commit()

        # Sample messages
        msgs = [
            Message(session_id=s1.id, role="user", content="Looking for a necklace for my anniversary", timestamp=datetime.utcnow() - timedelta(days=1, hours=2)),
            Message(session_id=s1.id, role="assistant", content="Welcome back, Priya! Here are some exquisite necklace picks for your anniversary:", timestamp=datetime.utcnow() - timedelta(days=1, hours=2), item_ids_shown=[6, 7, 9]),
            Message(session_id=s1.id, role="user", content="I love the pearl strand", timestamp=datetime.utcnow() - timedelta(days=1, hours=1)),
            Message(session_id=s1.id, role="assistant", content="Excellent taste! The Pearl Strand Necklace is one of our most beloved pieces.", timestamp=datetime.utcnow() - timedelta(days=1, hours=1)),
        ]
        db.add_all(msgs)
        db.commit()

        print("✓ Database seeded with 30 jewelry products, admin + 2 users, preferences, and sample sessions.")
        print("  Admin: admin@tanishq.com / Admin@123")
        print("  User:  priya@tanishq.com / User@123")
        print("  User:  rahul@tanishq.com / User@123")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
