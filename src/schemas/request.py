from pydantic import BaseModel, Field

class AnalysisRequest(BaseModel):
    # Validates that the year is an integer and within a realistic range
    target_year: int = Field(
        default=2019, 
        ge=1900, 
        le=2100, 
        description="The filter year for the database query"

    # TODO: # Add more fields here later (e.g., species_name, buffer_distance)
    )