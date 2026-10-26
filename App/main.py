
from contextlib import asynccontextmanager
from datetime import date
import sqlite3

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, ConfigDict, EmailStr, Field

DATABASE = "students.db"


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                dob TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT,
                course TEXT
            )
        """)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Student Management API",
    description="EWB internship CRUD project",
    version="1.0.0",
    lifespan=lifespan,
)


class StudentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    dob: date
    email: EmailStr
    phone: str | None = Field(default=None, max_length=20)
    course: str | None = Field(default=None, max_length=100)


class StudentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=100)
    dob: date | None = None
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=20)
    course: str | None = Field(default=None, max_length=100)


def find_student(student_id: int):
    with get_connection() as conn:
        student = conn.execute(
            "SELECT * FROM students WHERE id = ?",
            (student_id,),
        ).fetchone()

    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    return dict(student)


@app.post("/students", status_code=201)
def create_student(student: StudentCreate):
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO students
                   (name, dob, email, phone, course)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    student.name.strip(),
                    student.dob.isoformat(),
                    str(student.email),
                    student.phone,
                    student.course,
                ),
            )
            student_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="A student with this email already exists",
        )

    return find_student(student_id)


@app.get("/students")
def list_students(
    name: str | None = None,
    born_after: date | None = None,
    limit: int = Query(default=100, ge=1, le=500),
):
    sql = "SELECT * FROM students WHERE 1=1"
    params = []

    if name:
        sql += " AND name LIKE ?"
        params.append(f"%{name}%")

    if born_after:
        sql += " AND dob > ?"
        params.append(born_after.isoformat())

    sql += " ORDER BY id LIMIT ?"
    params.append(limit)

    with get_connection() as conn:
        rows = conn.execute(sql, params).fetchall()

    return [dict(row) for row in rows]


@app.get("/students/{student_id}")
def get_student(student_id: int):
    return find_student(student_id)


@app.put("/students/{student_id}")
def update_student(student_id: int, student: StudentUpdate):
    existing = find_student(student_id)
    updates = student.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one field to update",
        )

    for key, value in updates.items():
        if value is None:
            raise HTTPException(
                status_code=422,
                detail=f"{key} cannot be null",
            )
        if isinstance(value, date):
            updates[key] = value.isoformat()
        if key == "name":
            updates[key] = value.strip()

    allowed = {"name", "dob", "email", "phone", "course"}
    if not set(updates).issubset(allowed):
        raise HTTPException(status_code=400, detail="Invalid fields")

    assignments = ", ".join(f"{key} = ?" for key in updates)
    values = list(updates.values()) + [student_id]

    try:
        with get_connection() as conn:
            conn.execute(
                f"UPDATE students SET {assignments} WHERE id = ?",
                values,
            )
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="A student with this email already exists",
        )

    return find_student(student_id)


@app.patch("/students/{student_id}")
def patch_student(student_id: int, student: StudentUpdate):
    return update_student(student_id, student)


@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    find_student(student_id)

    with get_connection() as conn:
        conn.execute(
            "DELETE FROM students WHERE id = ?",
            (student_id,),
        )

    return {"message": "Student deleted successfully",
            "student_id": student_id}


@app.get("/")
def home():
    return {"message": "Student Management API is running"}
