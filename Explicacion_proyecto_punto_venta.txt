Explicación del proyecto Punto de Venta hecho por el equipo:
Dicho proyecto sabemos que se realizo casi en totalidad en Python Tkinter 
Tkinter es una herramienta que permite crear interfaces graficas frontend en Python

Tambien se trabajo con herramientas como por ejemplo pyodbc, pandas, random, datetime, matplotlib y reportlab

pyodbc: Permite conectar python con bases de datos (sqlserver, mysql...) para leer o escribir informacion directamente en ellas

pandas: Sirve para manejar y analizar datos de forma sencilla usando tablas como si fueran hojas de calculo

random: Se usa para generar valores aleatorios, por ejemplo numeros o selecciones al azar

datetime: Permite trabajar con fechas y horasm como calcular diferencias de tiempo o mostrar la fecha actual

matplotlib: Se utiliza para crear gráficos y visualizar datos (por ejemplo barras, lineas o tortas)

reportlab: Sirve para generar archivos PDF desde python, agregando texto, imagenes y graficos de manera automatica

Dicho proyecto como su nombre lo indica era crear un Punto de Venta donde le facilitaríamos al Vendedor el llevar y guardar todos los datos de sus ventas como ademas generar
tickets/presupuestos, teniendo diferentes funcionalidades extra que facilitan mucho mas el día a día del vendedor, como por ejemplo el poder comprobar por medio de un 
pdf, o imagenes diferentes estadisticas sobre los articulos vendidos ese mismo día. (Cabe aclarar que antes de ejecutar el programa, debemos estar conectados al servidor y a la base de datos)

Pasando más al codigo de dicho proyecto encontramos varias partes a exponer donde obviamente dividimos el Frontend del Backend, aunque la mayoría puede encontrarse 
fusionado en un codigo para que este ordenado segun lo que realiza.

Explicacion de Archivos del Proyecto:

Tenemos 10 archivos como tal de python que podemos explicar:

main.py: como archivo y ventana principal del sistema es el archivo que ejecutamos para que funcione el proyecto y en donde podemos encontrar muchas 
de las funcionalidades, en dicho arhcivo al ser el principal y el que ocupamos para ejecutar, encontramos las conexiones con los demas archivos por medio de la llamada
de los mismos con el import o from, ademas encontramos parte del Frontend donde esta mencionado en un comentario cada parte o agregado de la misma, tanto
la separacion entre el header y el body, como los botones y barras de busqueda, todo el Frontend no se encuentra en dicha pagina puesto que fue mucho mas comodo
para ciertas funciones especiales como agregar tickets, hacerlo todo en archivos diferentes para una mejor explicacion.

interfaz.py: Dicho archivo tiene la logica de cobrar y obviamente la interfaz y logica del boton venta

interfaz_tickets.py: Este archivo correspondiente al boton Generar tickets, contiene toda la logica que se ocupo para que podamos generar varios tickets con un tiempo limite
en dicho codigo debemos modificar ese tiempo de espera para generar un ticket

graficos.py: Este archivo proveniente de la seccionde graficos, se encarga de generar graficos con las diferentes estadísticas de las ventas, por ejemplo: 
Grafico de ventas por articulo , Grafico cantidad por articulo, Grafico ventas por dia

generar_pdf_tkinter.py: Este archivo tiene todo el codigo del boton Generar PDF, donde incorporo al proyecto la herramienta reportlab para crear pdf y añadir texto y demas
lo que hace es crear un pdf, y que evalua los datos de articulos para mostrarlos en el pdf, datos como Top 10 articulos mas vendidos o total recaudado segun el punto de venta que inicio sesion

funciones.py:  Este archivo contiene varias de las funcionalidades de los botones que aparecen en la pagina principal de venta por ejemplo: 
agregar_articulo, buscar_articulo, listar_articulos, editar_articulo, borrar_articulo, obtener_articulo, abrir / cerrar caja

ejecutar_primero.py: Este archivo se debe de ejecutar primero una vez iniciado y conectado al servidor para que cargue algunas tablas en la base de datos para poder 
hacer las pruebas de forma local

db.py: Este archivo sirve para llamar a la base de datos y así tratarlo en cualquier otra funcion o archivo

config.py: Este archivo configura toda la conexion con la base de datos sql server ademas de la conexion con el servidor y su IP

articulos_add.py: Este archivo agrega a la base de datos los articulos que aparecen en el archivo, dichos articulos al añadirlos a la base de datos tambien se muestran
en la seccion de inventario del punto de venta.