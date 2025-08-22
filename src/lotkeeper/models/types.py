"""Generic re-usable models, types and dataclasses"""

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field


@dataclass
class PaginationFilter:
    """Simple class for querying with limit and offset"""

    limit: int
    offset: int


class PaginationInfo(BaseModel):
    model_config = {"json_schema_extra": {"description": "Pagination details for paginated resources"}}

    limit: int = Field(description="Number of items per page", ge=1, le=1000)
    offset: int = Field(description="Number of items to skip", ge=0)
    total: int = Field(description="Total number of items available", ge=0)
    current_page: int | None = Field(description="Current page number (1-based)", ge=1, default=None)
    total_pages: int | None = Field(description="Total number of pages", ge=1, default=None)
    has_next: bool | None = Field(description="Whether there's a next page", default=None)
    has_previous: bool | None = Field(description="Whether there's a previous page", default=None)
    next_offset: int | None = Field(description="Offset for next page", default=None)

    def model_post_init(self, __context: Any) -> None:
        """Calculate computed fields after model initialization"""
        if self.limit and self.total:
            self.total_pages = max(1, (self.total + self.limit - 1) // self.limit)

        if self.offset is not None and self.limit:
            self.current_page = (self.offset // self.limit) + 1

        if self.current_page is not None and self.total_pages is not None:
            self.has_next = self.current_page < self.total_pages
            self.has_previous = self.current_page > 1

        if self.has_next:
            self.next_offset = self.offset + self.limit


class PaginatedResponse[T](BaseModel):
    model_config = {
        "json_schema_extra": {"description": "A paginated response containing a list of items and pagination details"}
    }

    data: list[T] = Field(description="The data of the response")
    pagination: PaginationInfo = Field(description="The pagination information of the response")
