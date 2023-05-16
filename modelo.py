from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline, FeatureUnion

# from sklearn.preprocessing import StandardScaler
# from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import RobustScaler

# from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.metrics.pairwise import cosine_similarity  # euclidean_distances, manhattan_distances


# esta clase la usaremos al construir el pipeline del modelo.
class ColumnSelector(BaseEstimator, TransformerMixin):
    '''esta clase selecciona las columnas dadas de un dataframe'''

    def __init__(self, columns=None):
        self.columns = columns

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        if self.columns is not None:
            return X[self.columns]
        else:
            return X


def compute_similarity(df, vocab, numeric_col, target_movie, top_n=5):
    '''funcion que computal a matriz de similitud
       df es el dataframe con la columna "DOC"
       vocab es el dataset con los tokens
       numeric_col son las columnas numericas que utilizaremos en conjunto a las de texto para calcular similitud
       target_movie es la pelicula sobre la cual queremos recibir recomendaciones
       top_n es el numero de recomendaciones'''

    # Define la pipeline para texto
    text_pipeline = Pipeline([
        ('select', ColumnSelector('doc')),  # selecciona doc
        ('vect', TfidfVectorizer(vocabulary=vocab))
        # utiliza el metodo count_vectorizer para covertir texto a numeros segun su frecuencia
    ])

    # Define la pipeline para columnas numéricas
    numeric_pipeline = Pipeline([
        ('select', ColumnSelector(numeric_col)),  # selecciona las columnas numéricas
        ('mms', RobustScaler())  # estandarizamos
    ])

    # Une ambas pipelines
    feature_union = FeatureUnion([
        ('text', text_pipeline),
        ('numeric', numeric_pipeline)
    ])

    # Aplica la feature_union al dataframe
    features = feature_union.fit_transform(df)

    # Encuentra el índice de la película objetivo en el dataframe
    target_index = df[df['title'] == target_movie].index[0]

    # Obtiene la fila correspondiente a la película objetivo
    target_features = features[target_index]

    # Calcula la similitud solo para la película objetivo
    cosine_sim = cosine_similarity(target_features.reshape(1, -1), features)

    # Obtén los índices de las películas más similares
    similar_indices = cosine_sim.argsort()[0][::-1]

    # Obtén las películas recomendadas basadas en la similitud
    top_movies = similar_indices[1:top_n + 1]

    # Devuelve las películas recomendadas
    return df.loc[top_movies, 'title'].values


def recomendar(pelicula, df, vocab):
    numeric_column = ['popularity', 'runtime']
    return compute_similarity(df, vocab, numeric_column, pelicula)