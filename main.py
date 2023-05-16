import pandas as pd
import ast

from fastapi import FastAPI
from modelo import recomendar # importamos la funcion para recomendar

# importamos los datos
df = pd.read_csv('./data/latest.csv')
vocab = pd.read_csv('./data/latest_vocab.csv')

# llenamos los espacios vacios con []
df.overview_keywords = df.overview_keywords.fillna('[]')

# convertimos string de listas a listas
columnas_lista = ['belongs_to_collection', 'genres', 'production_companies',
                  'production_countries', 'spoken_languages', 'production_countries_iso',
                  'spoken_languages_iso', 'overview_keywords']

for c in columnas_lista:
    df[c] = df[c].apply(ast.literal_eval)


# FUNCIONES EXTRAS
def has_this(to_find, value):
    if isinstance(value, list):
        for item in value:
            if item == to_find:
                return True
    return to_find == value


def get_index(df, diccionario):
    '''
    df es el dataframe
    diccionario tiene la siguiente forma: {columna: valor_to_find, columna2: valor2, etc...}
    por ejemplo: {production_countries: united states of america}
    '''

    index = True
    for c, to_find in diccionario.items():
        index = index & df[c].apply(lambda v: has_this(to_find, v))
    return index


# ======================================================================================================================
# ======================================================================================================================

# API ENDPOINTS
app = FastAPI()

@app.get('/')
def index():
    return {}

@app.get('/peliculas_mes/{mes}')
def peliculas_mes(mes: str):
    '''Se ingresa el mes y la funcion retorna la cantidad de peliculas que se estrenaron ese mes historicamente'''
    cantidad = get_index(df, dict(release_month=mes)).sum()

    cantidad = int(cantidad)
    return dict(mes=mes, cantidad=cantidad)

@app.get('/peliculas_dia/{dia}')
def peliculas_dia(dia: str):
    '''Se ingresa el dia y la funcion retorna la cantidad de peliculas que se estrenaron ese dia historicamente'''
    cantidad = get_index(df, dict(release_day=dia)).sum()

    cantidad = int(cantidad)
    return dict(dia=dia, cantidad=cantidad)

@app.get('/franquicia/{franquicia}')
def franquicia(franquicia: str):
    '''Se ingresa la franquicia, retornando la cantidad de peliculas, ganancia total y promedio'''
    indice = get_index(df, dict(belongs_to_collection=franquicia))
    ganancia_total = (df[indice].revenue - df[indice].budget).sum()
    ganancia_promedio = (df[indice].revenue - df[indice].budget).mean()
    cantidad = indice.sum()

    ganancia_total, ganancia_promedio = [float(x) for x in [ganancia_total, ganancia_promedio]]
    cantidad = int(cantidad)
    return dict(franquicia=franquicia, cantidad=cantidad, ganancia_total=ganancia_total, ganancia_promedio=ganancia_promedio)

@app.get('/peliculas_pais/{pais}')
def peliculas_pais(pais: str):
    '''Ingresas el pais, retornando la cantidad de peliculas producidas en el mismo'''
    cantidad = get_index(df, dict(production_countries=pais)).sum()

    cantidad = int(cantidad)
    return dict(pais=pais, cantidad=cantidad)

@app.get('/productoras/{productora}')
def productoras(productora: str):
    '''Ingresas la productora, retornando la ganancia total y la cantidad de peliculas que produjeron'''
    indice = get_index(df, dict(production_companies=productora))
    ganancia_total = (df[indice].revenue - df[indice].budget).sum()
    cantidad = indice.sum()

    ganancia_total = float(ganancia_total)
    cantidad = int(cantidad)
    return dict(productora=productora, ganancia_total=ganancia_total, cantidad=cantidad)

@app.get('/retorno/{pelicula}')
def retorno(pelicula: str):
    '''Ingresas la pelicula, retornando la inversion, la ganancia, el retorno y el año en el que se lanzo'''
    index =  df[df.title == pelicula].index[0]
    budget = df.loc[index, 'budget']
    revenue = df.loc[index, 'revenue']
    ganancia = revenue - budget
    retorno = df.loc[index, 'return']
    year = df.loc[index, 'release_year']

    budget, ganancia, retorno = [round(float(x), 2) for x in [budget, ganancia, retorno]]
    year = int(year)
    return dict(pelicula=pelicula, inversion=budget, ganancia=ganancia, retorno=retorno, anio=year)

@app.get('/recomendacion/{pelicula}')
def recomendacion(pelicula: str):
    '''Ingresas un nombre de pelicula y te recomienda las similares en una lista de 5 valores'''
    recomendaciones = recomendar(pelicula, df, vocab)

    recomendaciones = list(recomendaciones)
    return dict(pelicula=pelicula, recomendaciones=recomendaciones)