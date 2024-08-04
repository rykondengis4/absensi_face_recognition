from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import subprocess
import mysql.connector

app = FastAPI()

camera_process = None

class AbsensiData(BaseModel):
    tanggal_absensi: str
    id_mahasiswa: int
    waktu_masuk: str



@app.post("/insert_absensi")
def insert_absensi(data: AbsensiData):
    db_connection = mysql.connector.connect(
        host="localhost",
        user="root",
        database="absensi_wajah"
    )
    mycursor = db_connection.cursor()

    try:
        sql_insert = """
        INSERT INTO t_absensi (tanggal_absensi, id_mahasiswa, waktu_masuk)
        VALUES (%s, %s, %s)
        """
        mycursor.execute(sql_insert, (data.tanggal_absensi, data.id_mahasiswa, data.waktu_masuk))
        db_connection.commit()
    except mysql.connector.Error as err:
        db_connection.rollback()
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        mycursor.close()
        db_connection.close()

    return {"message": "Insert successful"}

def get_mata_kuliah():
    db_connection = mysql.connector.connect(
        host="localhost",
        user="root",
        database="absensi_wajah"
    )

    mycursor = db_connection.cursor()

    mycursor.execute("SELECT mata_kuliah FROM t_mata_kuliah")
    result = mycursor.fetchall()

    db_connection.close()

    return [row[0] for row in result]

def get_dosen():
    db_connection = mysql.connector.connect(
        host="localhost",
        user="root",
        database="absensi_wajah"
    )

    mycursor = db_connection.cursor()

    mycursor.execute("SELECT nama_dosen FROM t_dosen")
    result = mycursor.fetchall()

    db_connection.close()

    return [row[0] for row in result]

def get_student_by_name(name):
    db_connection = mysql.connector.connect(
        host="localhost",
        user="root",
        database="absensi_wajah"
    )
    mycursor = db_connection.cursor()

    query = """
    SELECT m.id_mahasiswa, m.nim
    FROM t_mahasiswa m
    WHERE LOWER(m.nama) = LOWER(%s)
    """
    mycursor.execute(query, (name.lower(),))
    result = mycursor.fetchone()

    db_connection.close()

    return result

def get_nim_by_id(id_mahasiswa):
    db_connection = mysql.connector.connect(
        host="localhost",
        user="root",
        database="absensi_wajah"
    )
    mycursor = db_connection.cursor()

    query = "SELECT nim FROM t_mahasiswa WHERE id_mahasiswa = %s"
    mycursor.execute(query, (id_mahasiswa,))
    nim_result = mycursor.fetchone()

    db_connection.close()

    return nim_result

@app.get("/check_absensi")
def check_absensi(id_mahasiswa: int, tanggal_absensi: str):
    db_connection = mysql.connector.connect(
        host="localhost",
        user="root",
        database="absensi_wajah"
    )
    mycursor = db_connection.cursor()

    check_query = """
    SELECT COUNT(*)
    FROM t_absensi
    WHERE tanggal_absensi = %s AND id_mahasiswa = %s
    """
    mycursor.execute(check_query, (tanggal_absensi, id_mahasiswa))
    count_result = mycursor.fetchone()[0]

    db_connection.close()

    return {"count": count_result}

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/mata_kuliah")
async def get_mata_kuliah_endpoint():
    return {"mata_kuliah" : get_mata_kuliah()}

@app.get("/dosen")
async def get_dosen_endpoint():
    return {"dosen" : get_dosen()}

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
        return {"Kamera dihentikan"}
    else:
        raise HTTPException(status_code=400, detail="Kamera tidak sedang berjalan")

@app.get("/mahasiswa")
def get_mahasiswa_by_name(name: str = Query(...)):

    result = get_student_by_name(name)

    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Mahasiswa tidak ditemukan")

@app.get("/nim")
def get_nim_by_student_id(id: int = Query(...)):

    result = get_nim_by_id(id)

    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Data tidak ditemukan")