"""Module containing all data models which are shared between requests and responses"""

import pydantic

import models


class WaterUsages(models.BaseModel):
    """A model for the current water usages"""
    
    start: int = pydantic.Field(
        default=...,
        alias='startYear'
    )
    """
    Start Year

    The data contained in the ``usages`` list start in this year
    """
    
    end: int = pydantic.Field(
        default=...,
        alias='endYear'
    )
    """
    End Year

    The data contained in the ``usages`` list ends in this year
    """
    
    usages: list[float] = pydantic.Field(
        default=...,
        alias='usageAmounts'
    )
    """
    Water Usage Amounts

    Every entry in this list depicts the water usage of year between the ``start`` and ``end``
    attribute of this object. The list needs to be ordered by the corresponding years
    """
    
    @pydantic.root_validator
    def check_data_consistency(cls, values):
        """
        Check if the data is consistent between itself. Meaning for every year is a water usage
        amount in the list present and the values for start and end are not switched or equal
        """
        data_start = values.get('start')
        data_end = values.get('end')
        usage_values = values.get('usages')
        if data_start == data_end:
            raise ValueError('Unable to run successful forecast with one set of data')
        # Calculate the number of entries needed for a complete dataset
        needed_values = (data_end - data_start) + 1
        # Now check if the usage list has the same length
        if len(usage_values) != needed_values:
            raise ValueError(f'The usage values have {len(usage_values)} entries. Expected '
                             f'{needed_values} from start and end parameter')
        return values
