# app/models.py
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class TestOrderItem(BaseModel):
    """Represents a single diagnostic test item within the order."""
    test_name: Optional[str] = Field(None, description="Name or description of the diagnostic test.")
    price: Optional[str] = Field(None, description="Price or cost of the test as a string (may contain currency symbol or formatting).") # Keeping as string as in JSON

# New models for the required output format
class YesNoStatus(BaseModel):
    yes: bool
    no: bool
class ClinicalInformation(BaseModel):
    single_pregnancy: YesNoStatus
    twin_pregnancy_minor_complication: YesNoStatus
    ivf_pregnancy: YesNoStatus
    gestational_age_weeks: str
    ultrasound_date: str
    crown_rump_length_crl: str
    nuchal_translucency: str
    maternal_weight: str
    prenatal_screening_risk_nt: str


class TestOption(BaseModel):
    package_name: str
    is_selected: bool

class AdditionalSelectionNotes(BaseModel):
    torch_fetal_infection_risk_survey: bool
    carrier_18_common_recessive_hereditary_disease_genes_in_vietnamese_thalassemia_hypo_hyper_thyroidism_g6pd_deficiency_pompe_wilson_cf: bool
    no_support_package_selected: bool

class HereditaryCancerType(BaseModel):
    is_selected: bool
    description: Optional[str] = None

class HereditaryCancer(BaseModel):
    breast_cancer_bcare: HereditaryCancerType
    a15_hereditary_cancer_types_more_care: HereditaryCancerType = Field(..., alias="15_hereditary_cancer_types_more_care")
    a20_hereditary_cancer_types_vip_care: HereditaryCancerType = Field(..., alias="20_hereditary_cancer_types_vip_care")

class GeneMutationClinicalInformation(BaseModel):
    clinical_diagnosis: str
    disease_stage: str
    pathology_result: str
    tumor_location_size_differentiation: str
    time_of_detection: str
    treatment_received: str

class SpecimenType(BaseModel):
    biopsy_tissue_ffpe: bool
    blood_stl_ctdna: bool
    pleural_peritoneal_fluid: bool

class CancerTypeAndTestPanel(BaseModel):
    onco_81: HereditaryCancerType
    onco_500_plus: HereditaryCancerType
    lung_cancer: HereditaryCancerType
    ovarian_cancer: HereditaryCancerType
    colorectal_cancer: HereditaryCancerType
    prostate_cancer: HereditaryCancerType
    breast_cancer: HereditaryCancerType
    cervical_cancer: HereditaryCancerType
    gastric_cancer: HereditaryCancerType
    pancreatic_cancer: HereditaryCancerType
    thyroid_cancer: HereditaryCancerType
    gastrointestinal_stromal_tumor_gist: HereditaryCancerType

class SpecimenAndTestInformation(BaseModel):
    specimen_type: SpecimenType
    gpb_code: str
    sample_collection_date: str
    cancer_type_and_test_panel_please_tick_one: CancerTypeAndTestPanel

class GeneMutationTesting(BaseModel):
    clinical_information: GeneMutationClinicalInformation
    specimen_and_test_information: SpecimenAndTestInformation

class NonInvasivePrenatalTesting(BaseModel):
    clinical_information: ClinicalInformation
    test_options: List[TestOption]
    
class ProcessedDocumentData(BaseModel):
    full_name: str
    clinic: str
    date_of_birth: str
    doctor: str
    sample_collection_date: str
    sample_collection_time: str
    phone: str
    email: str
    test_code: str
    smoking: str
    address: str
    test_code: str = Field(..., alias="Test code")
    non_invasive_prenatal_testing: NonInvasivePrenatalTesting
    additional_selection_notes: AdditionalSelectionNotes
    hereditary_cancer: HereditaryCancer
    gene_mutation_testing: GeneMutationTesting

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
