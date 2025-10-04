ENTORNO = 'local' 

CONFIG_LOCAL = {
    'server': 'localhost' , 
    #\SQLEXPRESS01 (para enzo) 
    'database': 'PuntoVenta'
}

CONFIG_INSTITUTO = {
    'server': '192.168.252.218', #cambien su ip
    'database': 'PuntoVenta',                      
    'user': 'homeUser',     
    #lucas cambia tus credenciales si haces en tu casa                 
    'password': 'Admin'
    #'password': 'admin'(para Lucas)                
}


CONNECTION_STRING = ""

if ENTORNO == 'local':
    # Crea el string para la conexión local (Autenticación de Windows)
    SERVER = CONFIG_LOCAL['server']
    DATABASE = CONFIG_LOCAL['database']
    CONNECTION_STRING = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"Trusted_Connection=yes;"
    )

elif ENTORNO == 'instituto':
    # Crea el string para la conexión del instituto (Autenticación de SQL Server)
    SERVER = CONFIG_INSTITUTO['server']
    DATABASE = CONFIG_INSTITUTO['database']
    UID = CONFIG_INSTITUTO['user']
    PWD = CONFIG_INSTITUTO['password']
    CONNECTION_STRING = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"UID={UID};"
        f"PWD={PWD};"
    )

