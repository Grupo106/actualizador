[![GitHub tag](https://img.shields.io/github/tag/Grupo106/actualizador.svg?maxAge=2592000?style=plastic)](https://github.com/Grupo106/actualizador/releases)
[![Build Status](https://travis-ci.org/Grupo106/actualizador.svg?branch=master)](https://travis-ci.org/Grupo106/actualizador)
[![codecov](https://codecov.io/gh/Grupo106/actualizador/branch/master/graph/badge.svg)](https://codecov.io/gh/Grupo106/actualizador)
[![Code Climate](https://codeclimate.com/github/Grupo106/actualizador/badges/gpa.svg)](https://codeclimate.com/github/Grupo106/actualizador)

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
