# actualizador
> Este modulo actualiza las clases de trafico desde un servidor externo

## Funcionamiento
Consulta el numero de version de la ultima actualizacion disponible, 
si es distinto al que tiene guardado, solicita todas las clases de
trafico en formato JSON, parsea los objetos y guarda los cambios
en la base de datos

## Instalacion
TODO

## Configuracion
TODO

## Logging
Los logs se guardan mediante el demonio syslog de Unix (Journalctl
en los Linux modernos)
