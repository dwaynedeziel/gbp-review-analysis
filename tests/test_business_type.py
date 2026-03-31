from services.business_type import get_terminology, detect_business_type, BUSINESS_TYPES


def test_get_terminology_default():
    t = get_terminology("default")
    assert t["customers"] == "customers"
    assert t["prospect"] == "prospect"


def test_get_terminology_medical():
    t = get_terminology("medical")
    assert t["customers"] == "patients"
    assert t["prospect"] == "patient"


def test_get_terminology_restaurant():
    t = get_terminology("restaurant")
    assert t["customers"] == "guests"


def test_get_terminology_unknown_falls_back():
    t = get_terminology("nonexistent_type")
    assert t["customers"] == "customers"


def test_detect_plumbing():
    assert detect_business_type("Smith Plumbing & HVAC") == "home_services"


def test_detect_dental():
    assert detect_business_type("Bright Smile Dental Care") == "medical"


def test_detect_law_firm():
    assert detect_business_type("Johnson & Associates Law Firm") == "legal"


def test_detect_restaurant():
    assert detect_business_type("Mario's Pizza Restaurant") == "restaurant"


def test_detect_unknown():
    assert detect_business_type("XYZ Enterprises LLC") == "default"


def test_all_types_have_terminology():
    for btype in BUSINESS_TYPES:
        t = get_terminology(btype)
        assert "customers" in t
        assert "prospect" in t
        assert "review_ask_audience" in t
