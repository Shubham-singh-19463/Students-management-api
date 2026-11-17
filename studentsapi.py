from fastapi import FastAPI, Path, Query, HTTPException, Body
from studentsapi_model import StudentResponse, updateStudents, CreateStudent
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

app = FastAPI()


@app.get("/")
def home():
    return {"Welcome to student api"}


# Is endpoint se jo bhi data return hoga, use StudentResponse model ke according process karna.
@app.get("/student/{id}", response_model=StudentResponse)
def find_student(id:int = Path(..., description="enter this to find student by id")):

    try:
        with engine.connect() as connection:
        
            result = connection.execute(
                text("SELECT * FROM STUDENTS where id = :student_id;"),
                {"student_id" : id}
            )
            student = result.mappings().first()
            

    
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Database error"
        )

    if student is None:
        raise HTTPException(status_code=404, detail="Student id not found")

    return student
    

# id auto increment from database
@app.post("/student", status_code=201)
def create_students(stud : CreateStudent):
    try:
        with engine.connect() as connection:
            
            result = connection.execute(
                    text("INSERT INTO students (name, age, course, marks) VALUES (:name, :age, :course, :marks) RETURNING id;"),
                    {
                     "name" : stud.name,
                     "age" : stud.age,
                     "course" : stud.course,
                     "marks" : stud.marks,
                     }
                )
            id = result.scalar_one()
            connection.commit()
                
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Id already exists"
        
        )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Database error"
        )

    return {"status" : f"{stud.name} is created", "id" : id}
 
    
@app.put("/student/{student_id}")
def update_students(student_update: updateStudents,student_id : int = Path(...)):

    data = student_update.model_dump(exclude_unset=True)

    try:
        with engine.connect() as connection:

            student = connection.execute(text("Select * from students where id = :student_id"), {"student_id" : student_id})
            student_detail = student.mappings().first()
            
            if not student_detail:
                raise HTTPException(status_code = 404, detail="id not found")


            for key,value in student_detail.items():
                if key == "id":
                    continue
                if key not in data.keys():
                    data[key] = value

            
            connection.execute(
                        text(" UPDATE students SET name = :name, age = :age, course = :course, marks = :marks WHERE id = :student_id;"),
                        {"student_id" : student_id,
                         "name" : data["name"],
                         "age" : data["age"],
                         "course" : data["course"],
                         "marks" : data["marks"]
                         }
                    )
            
            connection.commit()

    except HTTPException:
        raise

    except SQLAlchemyError:
        raise HTTPException(
        status_code=500,
        detail="Server error"
    )

    return {"message" : "Student updated!"}
    
    

@app.delete("/student/{id}")
def delete_student(id : int = Path(..., description="Enter your id to delete")):
    
    try:
        with engine.connect() as connection:
            
            result = connection.execute(
                    text("DELETE FROM students WHERE id = :student_id;"),
                    {"student_id" : id}
                )

            
            if result.rowcount == 0:
                raise HTTPException(status_code = 404, detail="Id not found")
            
            connection.commit()

                
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Server error"
        )
    return {"student is deleted"}


@app.get("/all_students")
def show_all_students():
    
    try:
        with engine.connect() as connection:
            result = connection.execute(text("Select * from students;"))
            all_student = result.mappings().fetchall()
    

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Server error"
        )
    
    all_student = [StudentResponse(**student).model_dump() for student in all_student]
        
    return all_student

@app.get("/filter_student")
def filter_student(
    course: str | None = Query(None),
    sort_by: str | None = Query(None),
    sort_order: str = Query("asc"),
    page: int = Query(1, ge=1),
    limit: int = Query(2, ge=1, le=100)
):
    sort_by_list = ["age", "marks", "id"]
    sort_order_list = ["asc", "desc"]

    sort_order = sort_order.lower()

    if sort_by is not None and sort_by not in sort_by_list:
        raise HTTPException(400, "Invalid sort column")

    if sort_order not in sort_order_list:
        raise HTTPException(400, "Invalid sort order")

    if sort_by is None:
        sort_by = "id"
        sort_order = "asc"

    query = "SELECT * FROM students"
    params = {
        "limit": limit,
        "offset": (page - 1) * limit
    }

    if course is not None:
        query += " WHERE LOWER(course) = LOWER(:course)"
        params["course"] = course

    query += f" ORDER BY {sort_by} {sort_order.upper()}"

    if sort_by != "id":
        query += ", id ASC"

    query += " LIMIT :limit OFFSET :offset"

    try:
        with engine.connect() as connection:
            result = connection.execute(text(query), params)
            all_student = result.mappings().fetchall()

    except SQLAlchemyError:
        raise HTTPException(500, "Server error")

    return [
        StudentResponse(**student).model_dump()
        for student in all_student
    ]