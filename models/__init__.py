import pydantic


class BaseModel(pydantic.BaseModel):
    
    class Config:
        
        allow_population_by_field_name = True
