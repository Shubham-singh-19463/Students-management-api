import os
from dotenv import load_dotenv

from sqlalchemy import create_engine, text

# from sqlalchemy.orm import sessionmaker, DeclarativeBase


# Read environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Database konsa hai aur kaise connection banana hai, ex:- connection manager
engine = create_engine(DATABASE_URL)

# connection banana engine se
# run = engine.connect()
# query database par ja ke data ko retrieve kar ke driver me store ho gya aur wha se result object mil gya.
# data = run.execute(text("SELECT * FROM STUDENTS;"))

# fetch connection pe pahle kar rhe hai taaki jo data driver me load nhi hua hai wo dubara se load ho ke python ke isi variable me aa jaye.
# all_data = data.all()

# ye wala connection close
# run.close()

# example 1: with context se sabhi student ko retrieve karna ka example
# with engine.connect() as connection:
#     result = connection.execute(text("SELECT * FROM STUDENTS;"))
#     all_student = result.mappings().fetchall() # mappings() -> convert rows to dictionary

# print(all_student)


with engine.connect() as connection:
    try:
        result = connection.execute(
            text("INSERT INTO students (id, name, age, course, marks) VALUES (13, 'june', 20, 'BCA', 65);")
        )

        # database me transaction ke andar query execute ho gya hai par changes nhi hua agar commit nhi kiya to wo database me change nhi hoga.
        connection.commit()
        print("done...")
    except Exception as e:
        connection.rollback() # transaction ko clean kar dega
        print(e)
