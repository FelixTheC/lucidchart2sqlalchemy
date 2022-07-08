import sqlalchemy as sa

SQLALCHEMY_TYPES = {key.lower(): key for key in vars(vars(sa)["types"]).keys()
                    if not key.startswith("_") and not key.swapcase().islower()}

SQLALCHEMY_TYPES.update({
    "str": SQLALCHEMY_TYPES["string"],
    "bool": SQLALCHEMY_TYPES["boolean"],
    "int": SQLALCHEMY_TYPES["integer"],
})

COLUMN_NAMES = {
    "en": {
            "library": "Shape Library",
            "area_1": "Text Area 1",
            "area_2": "Text Area 2",
        },
    "de": {
            "library": "Formenbibliothek",
            "area_1": "Textbereich 1",
            "area_2": "Textbereich 2",
    }
}