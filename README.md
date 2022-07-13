![Python application](https://github.com/FelixTheC/lucidchart2sqlalchemy/workflows/Python%20application/badge.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

# Lucidchart2SqlAlchemy
- when creating UML charts in Lucidchart I needed to create these objects "twice" with
this package you're being able to generate python-files including SqlAlchemy-Models

![uml_diagrams](CamperVanPricing.png)
- will generate models like this
```python
class BaseRate(BaseModel):
    __tablename__ = "base_rate"

    model_code: str = sa.Column(sa.String)
    booking_period_id: str = sa.Column(sa.String, sa.ForeignKey("booking_period.id"))
    rate: float = sa.Column(sa.Float)
    monthly_rate: bool = sa.Column(sa.Boolean)
```