SERVER = 'localhost' 
#SERVER = '192.168.100.10'
DATABASE = 'PuntoVenta'

STRING_DE_CONEXION = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"Trusted_Connection=yes;"
    #f"Trusted_Connection=No;"
)