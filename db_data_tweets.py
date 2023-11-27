import mysql.connector
import pandas as pd

def tweets_database():

    # Configura tu conexión a la base de datos MySQL
    conexion = mysql.connector.connect(
        host="laclicsa.online",
        user="Admin1",
        password="admin_123!",
        database="twitter_database"
    )

    # Crea un cursor para ejecutar consultas SQL
    cursor = conexion.cursor()

    # Ejecuta una consulta SQL para obtener el usuario a buscar
    consulta = "SELECT * FROM tweets_user;"
    cursor.execute(consulta)

    # Recupera el resultado de la consulta
    resultado = cursor.fetchall()

    # Obtiene los nombres de las columnas de la tabla
    columnas = [i[0] for i in cursor.description]

    # Crea un DataFrame de Pandas a partir de los resultados y las columnas
    df_tweets = pd.DataFrame(resultado, columns=columnas)

    # Cierra el cursor y la conexión
    cursor.close()
    conexion.close()

    return df_tweets
