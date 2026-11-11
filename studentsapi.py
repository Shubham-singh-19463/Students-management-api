from fastapi import FastAPI, Path, Query, HTTPException, Body
from studentsapi_model import Student, updateStudents
import json

app = FastAPI()

def read_data():
    with open("students_data.json", "r") as f:
        return json.load(f)

def write_data(data):
    with open("students_data.json", "w") as f:
        json.dump(data, f, indent=4)

def read_counter():
    with open("counter.json", "r") as f:
        return json.load(f)

def write_counter(data):
    with open("counter.json", "w") as f:
        json.dump(data, f, indent=4)

@app.get("/")
def home():
    return {"Welcome to student api"}

@app.get("/students")
def show_all_students():
    data = read_data()
    return {
        "total_no_of_students" : len(data),
        "data" : data
    }

@app.get('/students')
def pagination(page: int = Query(..., description=("Enter page no")), limit: int = Query(..., description=("Enter limit no"))):
    data = read_data()
    start = (page - 1) * limit
    end = start + limit
    return data[start:end]


@app.get("/students/search")
def search_by(name: str = Query(..., description="search by name")):
    data = read_data()
    students_name = []
    for info in data:
        if info["name"] == name:
            students_name.append(info)
    return students_name


@app.get("/students/sort_by")
def sort_by():
    data = read_data()
    sorting = sorted(data, key=lambda x: x['marks'])
    return sorting


@app.get("/students/filter")
def filter_by(course: str | None = Query(None, description="search by course"),
              min_marks: int | None = Query(None, description="search by min marks")):
    
    data = read_data()
    filtered_data = []

    if course is not None:

        for info in data:
            if info["course"] == course:
                filtered_data.append(info)

    if min_marks is not None:
        tmp_data = []

        for info in filtered_data:
            if info["marks"] >= min_marks:
                tmp_data.append(info)
        
        filtered_data = tmp_data 

    return filtered_data




@app.get("/students/{id}")
def find_student(id:int = Path(..., description="enter this to find student by id")):
    data = read_data()

    for info in data:
        if info["id"] == id:
            return info
            
    raise HTTPException(status_code=404, detail="id not found")


@app.post("/create", status_code=201)
def create_students(stud : Student):
    data = read_data()

    counter_d = read_counter()
    counter_d["id"] += 1

    write_counter(counter_d)

    student_data = stud.model_dump()
    student_data["id"] = counter_d["id"]


    data.append(student_data)
    write_data(data)

    return {"message":"success"}


@app.put("/students/{student_id}")
def update_students(student_update: updateStudents,student_id : int = Path(...)):

    data = read_data()

    for index,info in enumerate(data):
        if info["id"] == student_id:
            exisiting_data = data[index]
            update_data = student_update.model_dump(exclude_unset=True)
            
            for key,value in update_data.items():
                exisiting_data[key] = value

            student_det = Student(**exisiting_data).model_dump()
            data[index] = student_det
            write_data(data)

            return {"message" : "success"}
    raise HTTPException(status_code=404, detail="Id not found")

@app.delete("/students/{id}")
def delete_student(id : int = Path(..., description="Enter your id to delete")):
    data = read_data()
    for index,info in enumerate(data):
        if info["id"] == id:
            data.pop(index)
            write_data(data)
            return {"message" :"success"}
    raise HTTPException(status_code=404, detail="Id not found")
