from app.models.tour_package import TourPackage

def filter_packages(db, city, budget):
    packages = db.query(TourPackage).filter(
        TourPackage.status == "active",
        TourPackage.price <= budget
    ).all()

    if city != "All":
        packages = [p for p in packages if p.city == city]

    return packages
