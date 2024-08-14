from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import subprocess
import mysql.connector
from mysql.connector import Error

app = FastAPI()

camera_process = None

class AbsensiData(BaseModel):
    id_mahasiswa: int
    tanggal_absensi: str
    waktu_masuk: str

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

@app.post("/insert_absensi")
def insert_absensi(data: AbsensiData):
    sql_insert = """
    INSERT INTO t_absensi (id_mahasiswa, tanggal_absensi, waktu_masuk)
    VALUES (%s, %s, %s)
    """
    execute_query(sql_insert, (data.id_mahasiswa, data.tanggal_absensi, data.waktu_masuk))
    return {"message": "Insert successful"}

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

@app.get("/mahasiswa")
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
