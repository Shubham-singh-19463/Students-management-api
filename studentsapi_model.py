from pydantic import BaseModel, Field, computed_field

class Student(BaseModel):
    id : int | None = Field(None)
    name : str = Field(..., max_length=100, min_length=2)
    age : int = Field(..., gt=0, lt=50)
    course : str = Field(...)
    marks : int = Field(..., ge=0, le=100)

    @computed_field
    @property
    def grade(self) -> str:
        if self.marks >= 90:
            return "A+"
        elif self.marks >= 80:
            return "A"
        elif self.marks >= 70:
            return "B+"
        elif self.marks >= 60:
            return "B"
        elif self.marks >= 50:
            return "C"
        else:
            return "F"

class updateStudents(BaseModel):
    name : str | None = Field(None, max_length=100, min_length=2)
    age : int | None = Field(None, gt=0, lt=50)
    course : str | None = Field(None)
    marks : int | None = Field(None, ge=0, le=100)