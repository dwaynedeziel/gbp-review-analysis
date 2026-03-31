BUSINESS_TYPES = {
    "home_services": "Home Services (Plumbing, HVAC, Roofing, etc.)",
    "medical": "Medical / Dental / Veterinary",
    "senior_living": "Senior Living / Assisted Living",
    "legal": "Legal Services",
    "restaurant": "Restaurant / Food Service",
    "real_estate": "Real Estate",
    "automotive": "Auto Repair / Dealerships",
    "b2b": "B2B / Professional Services",
    "retail": "Retail / E-commerce",
    "education": "Education / Childcare",
    "default": "Other / General",
}

TERMINOLOGY_MAP = {
    "home_services": {
        "customers": "customers",
        "prospect": "homeowner",
        "review_ask_audience": "happiest customers",
    },
    "medical": {
        "customers": "patients",
        "prospect": "patient",
        "review_ask_audience": "happiest patients",
    },
    "senior_living": {
        "customers": "residents and families",
        "prospect": "family",
        "review_ask_audience": "residents and families",
    },
    "legal": {
        "customers": "clients",
        "prospect": "potential client",
        "review_ask_audience": "satisfied clients",
    },
    "restaurant": {
        "customers": "guests",
        "prospect": "diner",
        "review_ask_audience": "happiest guests",
    },
    "real_estate": {
        "customers": "clients",
        "prospect": "buyer",
        "review_ask_audience": "satisfied clients",
    },
    "automotive": {
        "customers": "customers",
        "prospect": "vehicle owner",
        "review_ask_audience": "happiest customers",
    },
    "b2b": {
        "customers": "clients",
        "prospect": "prospect",
        "review_ask_audience": "satisfied clients",
    },
    "retail": {
        "customers": "customers",
        "prospect": "shopper",
        "review_ask_audience": "happiest customers",
    },
    "education": {
        "customers": "parents and families",
        "prospect": "parent",
        "review_ask_audience": "families",
    },
    "default": {
        "customers": "customers",
        "prospect": "prospect",
        "review_ask_audience": "happiest customers",
    },
}

# Keywords used for auto-detection from business name
_DETECTION_KEYWORDS = {
    "home_services": [
        "plumbing", "plumber", "hvac", "heating", "cooling", "roofing", "roofer",
        "electrical", "electrician", "landscaping", "painting", "remodel",
        "construction", "handyman", "pest control", "cleaning", "restoration",
        "garage door", "fencing", "paving", "septic", "insulation",
    ],
    "medical": [
        "medical", "dental", "dentist", "doctor", "clinic", "hospital",
        "veterinary", "vet", "orthodont", "chiropractic", "chiropractor",
        "dermatolog", "pediatric", "urgent care", "pharmacy", "optom",
        "ophthalmol", "therapy", "therapist", "counseling", "mental health",
        "physical therapy", "wellness",
    ],
    "senior_living": [
        "senior living", "assisted living", "nursing home", "memory care",
        "retirement", "elder care", "senior care",
    ],
    "legal": [
        "law", "legal", "attorney", "lawyer", "firm", "litigation",
        "injury", "defense", "counsel",
    ],
    "restaurant": [
        "restaurant", "cafe", "coffee", "pizza", "grill", "bar", "pub",
        "bistro", "bakery", "diner", "sushi", "taco", "burger", "kitchen",
        "eatery", "catering", "food truck", "brewery",
    ],
    "real_estate": [
        "real estate", "realty", "realtor", "property", "mortgage", "homes",
        "brokerage",
    ],
    "automotive": [
        "auto", "automotive", "car", "vehicle", "mechanic", "tire",
        "collision", "body shop", "dealership", "motor", "transmission",
        "oil change",
    ],
    "retail": [
        "store", "shop", "boutique", "market", "outlet", "mall",
        "supply", "goods",
    ],
    "education": [
        "school", "academy", "learning", "tutoring", "daycare", "childcare",
        "preschool", "montessori", "education", "university", "college",
    ],
}


def get_terminology(business_type: str) -> dict:
    return TERMINOLOGY_MAP.get(business_type, TERMINOLOGY_MAP["default"]).copy()


def detect_business_type(name: str) -> str:
    name_lower = name.lower()
    for btype, keywords in _DETECTION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in name_lower:
                return btype
    return "default"
