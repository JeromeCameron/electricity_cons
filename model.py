from pydantic import BaseModel

# Data model using pydantic
class Bill(BaseModel):
    invoice_no: str
    service_address: str
    date_: str
    read_type: str
    billing_period: str
    energy_used: str|None
    total_charges: str