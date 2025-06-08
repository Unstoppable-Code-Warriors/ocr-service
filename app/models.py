# app/models.py
from typing import List, Optional
from pydantic import BaseModel, Field

class TestOrderItem(BaseModel):
    """Represents a single diagnostic test item within the order."""
    test_name: Optional[str] = Field(None, description="Name or description of the diagnostic test.")
    price: Optional[str] = Field(None, description="Price or cost of the test as a string (may contain currency symbol or formatting).") # Keeping as string as in JSON

class Data(BaseModel):
    """Represents the main data payload containing details of a diagnostic order."""
    test_orders: Optional[List[TestOrderItem]] = Field(
        None,
        description="List of ordered diagnostic tests with details."
    )
    hospital: Optional[str] = Field(
        None,
        description="The name of the hospital."
    )
    order_sheet: Optional[str] = Field(
        None,
        description="The type of the order form (e.g., 'Biochemistry-Immunology Test')."
    )
    clinic: Optional[str] = Field(
        None,
        description="The name or code of the clinic room."
    )
    medical_record_id: Optional[str] = Field(
        None,
        description="The patient's medical record code."
    )
    order_id: Optional[str] = Field(
        None,
        description="The unique identifier for this specific order."
    )
    full_name: Optional[str] = Field(
        None,
        description="The full name of the patient."
    )
    address: Optional[str] = Field(
        None,
        description="The patient's address."
    )
    gender: Optional[str] = Field(
        None,
        description="Patient's gender information as a raw string (e.g., 'Nam')."
    )
    age: Optional[int] = Field(
        None,
        description="The patient's age."
    )
    patient_type: Optional[str] = Field(
        None,
        description="The category or type of the patient (e.g., paying, insurance)."
    )
    diagnosis: Optional[str] = Field(
        None,
        description="The patient's diagnosis."
    )
    exam_date: Optional[str] = Field(
        None,
        description="The date of the examination." # Could potentially be parsed as a date
    )
    ordering_doctor: Optional[str] = Field(
        None,
        description="The name or identifier of the ordering doctor." # Note: Sample data sometimes contains a date instead of a name/ID.
    )
    sample_time: Optional[str] = Field(
        None,
        description="The time the sample was collected."
    )
    print_time: Optional[str] = Field(
        None,
        description="The time the order form was printed." # Could potentially be parsed as a datetime
    )
    technician: Optional[str] = Field(
        None,
        description="The name or identifier of the technician who collected the sample."
    )
