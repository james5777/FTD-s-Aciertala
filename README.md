# FTD-s-Aciertala
El objetivo de esta automatizacion es definir desde los exportables del sportbook, cuales de los usuarios registrados son primeros depositos, teniendo en cuenta las variables

Funcionamiento de la automatizacion:

La base de datos se carga inicialmente y esta cargada con los datos hasta el dia anterior dependiendo si es un dia entre semana o si es el dia siguiente de un fin de semana. 

El archivo excel de los registros se puede cargar normalmente eliminando el archivo anterior y agregando el nuevo en la direccion: FTD-s-Aciertala/Archivos/Diario-ACPE.xlsm ese es el nombre que debe tener siempre el archivo excel "Diario-ACPE.xlsm", debe tener ya hecha la actualizacion en el excel de los datos del dia que se quiere extraer la informacion de los primeros depositos, este archivo excel se encuentra en el Onedrive/Compartido/Carpeta/Quota Media Area Digital/Digital Quota/General Quota/Reportes/Elaboracion_Diario/Diario_ACPE.xlsm (Debe ser la ultima version, con la ultima fecha, igualmente es importante revisar).

Para el archivo CSV de las transacciones, si se debe eliminar el archivo anterior. Y los registros que se van a subir en ese CSV, tienen que ser nuevos, es decir si la fecha de corte anterior era hasta el 29/07/2025, el CSV debe contener registros desde el 30/07/025 en adelante, ya que si se repiten los registros no se sobreescriben sino que se duplican, y esto genera alteraciones en la data real. tambien se debe tener cuidado en el sportbook ya que no es solamente poner la fecha, tambien se debe tener en cuenta de que hora a que hora esta exportando los registros, no solamente el dia, sino tambien la hora. el archivo CSV se debe alojar en la siguiente ruta: FTD-s-Aciertala/Archivos/transactions.csv , para conseguir este archivo diariamente se debe ir al sportbook, ir al submenu "Lista de transacciones", y modificar los siguientes imputs del formulario de filtro: 

Casa de apuestas:  Aciertala PE
Grupo causal: Deposit - Withdraw
Por pagina: 1000
Tipo: Depositar
Real/Test: Usuario verdadero

Para el filtro de fecha: si es el dia anterior se puede seleccionar "ayer", si es el fin de semana, o una seleccion de varios dias, se debe seleccionar el dia desde que se quiere empezar a filtrar, QUE EMPIECE EN LAS 00:00, y para el dia final del filtro se debe seleccionar el dia siguiente al que se quiere seleccionar y debe estar la hora en 00:00, por ejemplo si quiero ver todos los registros desde el 22 de septiembre hasta el 25 de septiembre, selecciono como fecha inicial 22/09/2025 00:00 y como fecha final 26/09/2025 00:00.

El codigo tiene un bloque comentable, el cual esta marcado, este bloque se comenta cuando ya se cargaron los datos del csv y el excel , y si se quiere modificar algo en la logica de ahi hacia abajo, al ejecutar se comenta esto, para que no dañe la base de datos.

El archivo resultante con los Registros y FTD de aciertala, al ejecutar se crea en la siguiente ruta: FTD-s-Aciertala/Reporte_Diario_Aciertala.xlsx
Y tiene como nombre: Reporte_Diario_Aciertala.xlsx








