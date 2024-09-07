from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import subprocess
import mysql.connector
from mysql.connector import Error
from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI()

camera_process = None

class AbsensiData(BaseModel):
    id_mahasiswa: int
    tanggal_absensi: str
    waktu_masuk: str

class Mahasiswa(BaseModel):
    nim: str
    nama: str
    kelas: str
    semester: str

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            database="absensi_wajah"
        )
        return connection
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))

def execute_query(query, params=None, fetchone=False):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        if fetchone:
            result = cursor.fetchone()
        else:
            result = cursor.fetchall()
        connection.commit()
    except Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        connection.close()
    return result

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/absensi", response_model=List[dict])
def get_absensi():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT m.Nama AS nama, m.nim AS nim, m.Semester AS semester, a.tanggal_absensi, TIME_FORMAT(a.waktu_masuk, '%H:%i:%s') AS waktu_masuk
        FROM t_absensi a
        JOIN t_mahasiswa m ON a.id_mahasiswa = m.id_mahasiswa
    """
    cursor.execute(query)
    absensi_list = cursor.fetchall()
    cursor.close()
    connection.close()
    return absensi_list

# api.py
@app.get("/mahasiswa", response_model=List[dict])
def get_mahasiswa(semester: str):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM t_mahasiswa WHERE semester = %s"
    cursor.execute(query, (semester,))
    mahasiswa_list = cursor.fetchall()
    cursor.close()
    connection.close()
    return mahasiswa_list


@app.post("/mahasiswa")
def create_mahasiswa(mahasiswa: Mahasiswa):
    connection = get_db_connection()
    cursor = connection.cursor()
    query = """
    INSERT INTO t_mahasiswa (nim, nama, kelas, semester)
    VALUES (%s, %s, %s, %s)
    """
    values = (mahasiswa.nim, mahasiswa.nama, mahasiswa.kelas, mahasiswa.semester)
    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close()
    return {"message": "Mahasiswa added"}

@app.put("/mahasiswa/{id_mahasiswa}")
def update_mahasiswa(id_mahasiswa: int, mahasiswa: Mahasiswa):
    connection = get_db_connection()
    cursor = connection.cursor()
    query = """
    UPDATE t_mahasiswa
    SET nim = %s, nama = %s, kelas = %s, semester = %s
    WHERE id_mahasiswa = %s
    """
    values = (mahasiswa.nim, mahasiswa.nama, mahasiswa.kelas, mahasiswa.semester, id_mahasiswa)
    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close()
    return {"message": "Mahasiswa updated"}

@app.delete("/mahasiswa/{id_mahasiswa}")
def delete_mahasiswa(id_mahasiswa: int):
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "DELETE FROM t_mahasiswa WHERE id_mahasiswa = %s"
    cursor.execute(query, (id_mahasiswa,))
    connection.commit()
    cursor.close()
    connection.close()
    return {"message": "Mahasiswa deleted"}

@app.post("/insert_absensi")
def insert_absensi(data: AbsensiData):
    sql_insert = """
        INSERT INTO t_absensi (id_mahasiswa, tanggal_absensi, waktu_masuk)
        VALUES (%s, %s, %s)
        """
    try:
        execute_query(sql_insert, (data.id_mahasiswa, data.tanggal_absensi, data.waktu_masuk))
        return {"message": "Insert successful"}
    except:
        raise HTTPException(status_code=400, detail="Error melakukan absensi")

@app.get("/check_absensi")
def check_absensi(id_mahasiswa: int, tanggal_absensi: str):
    check_query = """
    SELECT COUNT(*)
    FROM t_absensi
    WHERE tanggal_absensi = %s AND id_mahasiswa = %s
    """
    count_result = execute_query(check_query, (tanggal_absensi, id_mahasiswa), fetchone=True)[0]
    return {"count": count_result}

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.post("/start")
def start_camera():
    global camera_process
    if camera_process is None or camera_process.poll() is not None:
        print("Memulai kamera...")
        camera_process = subprocess.Popen(['python', 'absen.py'])
        return {"message": "Kamera dimulai"}
    else:
        raise HTTPException(status_code=400, detail="Kamera sudah berjalan.")

@app.post("/stop")
def stop_camera():
    global camera_process

    if camera_process is not None and camera_process.poll() is None:
        print("Menghentikan kamera...")
        camera_process.terminate()
        camera_process.wait()
        camera_process = None
        return {"message": "Kamera dihentikan"}
    else:
        raise HTTPException(status_code=400, detail="Kamera tidak sedang berjalan")

@app.get("/nama_mahasiswa")
def get_mahasiswa_by_name(name: str = Query(...)):
    query = """
    SELECT m.id_mahasiswa, m.nim
    FROM t_mahasiswa m
    WHERE LOWER(m.nama) = LOWER(%s)
    """
    result = execute_query(query, (name.lower(),), fetchone=True)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Mahasiswa tidak ditemukan")

@app.get("/nim")
def get_nim_by_student_id(id: int = Query(...)):
    query = "SELECT nim FROM t_mahasiswa WHERE id_mahasiswa = %s"
    result = execute_query(query, (id,), fetchone=True)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Data tidak ditemukan")