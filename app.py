import dash
from dash import html, dcc, Output, Input, dash_table
from dash.exceptions import PreventUpdate
import pandas as pd
import dash.dependencies as dd
from db_data_tweets import tweets_database
import time

# ------------------ Funciones --------------------

def reemplazar_comas_comentarios(comentario):
    comentario = comentario.strip('[]')
    dentro_de_comillas = False
    resultado = []

    for caracter in comentario:
        if caracter == "'":
            dentro_de_comillas = not dentro_de_comillas
        elif caracter == ',' and not dentro_de_comillas:
            resultado.append(';')
        else:
            resultado.append(caracter)
    
    return ''.join(resultado)

def eliminar_corchetes(usuario):
    usuario = usuario.strip('[]')
    return usuario

def format_comments(comments):
    comments_list = comments.split('<br>')
    comments_formatted = html.Ol([html.Li(comment) for comment in comments_list])
    return comments_formatted


# --------- Main ------------------

# Crear una instancia del analizador de sentimientos
#analyzer = SentimentAnalyzer(lang="es")

app = dash.Dash(__name__, suppress_callback_exceptions=True)

interval_time = 15 * 60 * 1000


# Cargar datos desde el archivo CSV y agregar una columna de ID automáticamente
df = tweets_database()

# Formatear la columna "link_tweet" como enlace "Ver publicación"
for index, row in df.iterrows():
    df.at[index, 'link_tweet'] = f"[Ver publicación]({row['link_tweet']})"


opciones_usuario = [{'label': usuario, 'value': usuario} for usuario in df['user_tweet'].unique()]

# ------------------------------- Dash ------------------------------------------------------- 

# Estilo para los Dropdowns
dropdown_style = {
    'width': '80%',
    'borderRadius': '10px',
    'color': '#000000',
}



app.layout = html.Div([
    html.H1("DashBoard Twitter Scraper",style={"textAlign": "center", "color": "black" }),
    html.H2("Pool",style={'padding': '10px'}),
    html.Div( id='tabla-users-general', style={'padding': '20px'} ),
    dcc.Dropdown(
        id='dropdown-usuario',
        options=opciones_usuario,
        value=None,
        placeholder="Selecciona un usuario",
        style=dropdown_style
    ),
    dcc.Loading(
        id="loading",
        type="default",
        fullscreen=True,
        children=[
            html.Div(id='tabla-general-container', style={'padding': '20px','width':'auto'}),
            html.Div(
                dcc.Dropdown(
                    id='dropdown-tweet-id',
                    options=[],
                    value=None,
                    placeholder="Selecciona un ID de tweet",
                ), style={'width': '65%', 'borderRadius': '10px', 'color': '#000000'}
            ),
            html.Div(id='tabla-tweet-general-container', style={'padding': '20px'}),
            html.Div(id='tabla-comentarios-container', style={'padding': '20px'}),
        ]
    ),
     dcc.Interval(
                    id='interval-component',
                    interval=interval_time,  # Intervalo de actualización
                    n_intervals=0
                ),
], style={
    'background': 'linear-gradient(to bottom, #C2E0A1, #86B75C) fixed',
    'height': '180vh',
    'overflow': 'auto'
})


'''@app.callback(
    Output('tabla-users-general', 'children'),
    Input('tabla-users-general', 'id')
)
def tabla_usuarios_general(id):
    if id is None:
        return []

    # Crear la tabla
    table = dash_table.DataTable(
        id='tabla',
        columns=[
            {'name': 'Usuario', 'id': 'user_tweet'},
            {'name': 'Enlace', 'id': 'link_tweet', 'presentation': 'markdown'},
            {'name': 'Likes', 'id': 'cantidad_likes'},
            {'name': 'Compartido', 'id': 'cantidad_repost'},
            {'name': 'Comentarios', 'id': 'cantidad_comments'},
            {'name': 'Comentarios Positivos', 'id': 'comments_positivos'},
            {'name': 'Comentarios Negativos', 'id': 'comments_negativos'},
            {'name': 'Comentarios Neutros', 'id': 'comments_neutros'},
            {'name': 'Fecha del tweet', 'id': 'fecha_tweet'}

        ],
        data=df.to_dict('records'),
        style_table={'width': '100%'},
        style_cell={'textAlign': 'left'},
        style_header={'backgroundColor': 'lightgrey'},
        style_data_conditional=[
            {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}
        ],
    )

    return [table]

'''
@app.callback(
    [Output('dropdown-tweet-id', 'options'),
     Output('dropdown-tweet-id', 'style'),
     Output('tabla-general-container', 'children'),
     Output('tabla-tweet-general-container', 'children'),
     Output('tabla-comentarios-container', 'children')],
    [Input('dropdown-usuario', 'value'),
     Input('dropdown-tweet-id', 'value')]
)
def actualizar_pagina(selected_user, selected_tweet_id):

    df_actualizado = tweets_database()

    df_actualizado['id_tweet_user'] = df_actualizado['id_tweet_user'].astype(int)

    # Formatear la columna "link_tweet" como enlace "Ver publicación"
    for index, row in df.iterrows():
        df_actualizado.at[index, 'link_tweet'] = f"[Ver publicación]({row['link_tweet']})"

    # Lógica para actualizar opciones del dropdown-tweet-id
    if selected_user is not None:
        filtered_df = df_actualizado[df_actualizado['user_tweet'] == selected_user]
        tweet_ids = filtered_df['id_tweet_user'].unique()
        options = [{'label': str(tweet_id), 'value': tweet_id} for tweet_id in tweet_ids]
    else:
        options = []

    # Lógica para actualizar estilo del dropdown-tweet-id
    dropdown_style = {'display': 'block'} if selected_user is not None else {'display': 'none'}


    # Lógica para actualizar la tabla general
    if selected_user is not None:
        general_table = dash_table.DataTable(
            id='tabla-general',
            columns=[
                {'name': 'ID', 'id': 'id_tweet_user'},
                {'name': 'Texto', 'id': 'text'},
                {'name': 'Enlace', 'id': 'link_tweet','presentation': 'markdown'},
                {'name': 'Likes', 'id': 'cantidad_likes'},
                {'name': 'Compartido', 'id': 'cantidad_repost'},
                {'name': 'Comentarios', 'id': 'cantidad_comments'},
                {'name': 'Comentarios Positivos', 'id': 'comments_positivos'},
                {'name': 'Comentarios Negativos', 'id': 'comments_negativos'},
                {'name': 'Comentarios Neutros', 'id': 'comments_neutros'},
                {'name': 'Fecha del tweet', 'id': 'fecha_tweet'} 
            ],
            data=filtered_df.drop(columns=['comments_post', 'comment_authors']).to_dict('records'),
            style_table={'width': '100%', 'margin': '10px auto'},
            style_cell={'padding': '10px', 'textAlign': 'left', 'whiteSpace': 'normal', 'color': 'black'},
            style_header={'backgroundColor': 'lightgrey'},
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}
            ],
        )
    else:
        general_table = []

    # Lógica para actualizar la tabla de comentarios
    if selected_tweet_id is not None:
        filtered_comments_df = df_actualizado[df_actualizado['id_tweet_user'] == selected_tweet_id][['comments_post', 'comment_authors','comments_sentimientos']]
        filtered_comments_general = df_actualizado[df_actualizado['id_tweet_user'] == selected_tweet_id][['cantidad_comments', 'comments_positivos','comments_negativos','comments_neutros']]
        comments_data = pd.DataFrame()
        comments_list = []
        authors_list = []
        sentiments_list = []
        
        list_tam = filtered_comments_df['comments_post'].tolist()
        #print(list_tam)

        if list_tam != ['[]']:

            for index, row in filtered_comments_df.iterrows():
                comments = reemplazar_comas_comentarios(row['comments_post']).split(';')
                authors = eliminar_corchetes(row['comment_authors']).split(',')
                sent = eliminar_corchetes(row['comments_sentimientos']).split(",")

                for comment, author,sent in zip(comments, authors,sent):
                #    sentiment = analyzer.predict(comment)
                #    sentiment = sentiment.output
                    comments_list.append(comment)
                    authors_list.append(author)
                    sentiments_list.append(sent)
                    
            
            comments_data['Comentario'] = comments_list
            comments_data['Autor'] = authors_list
            comments_data['Sentimiento'] = sentiments_list
            comments_data['Sentimiento'] = comments_data['Sentimiento'].str.strip("' ")

            comments_table = dash_table.DataTable(
                id='tabla-comentarios',
                columns=[
                    {'name': col, 'id': col} for col in comments_data.columns
                ],
                data=comments_data.to_dict('records'),
                style_table={'width': '70%', 'margin': '20px auto'},
                style_cell={'padding': '10px', 'textAlign': 'left', 'whiteSpace': 'normal', 'color': 'black'},
                style_header={'backgroundColor': 'lightgrey'},
                style_data_conditional=[
                    {
                        'if': {'column_id': 'Sentimiento', 'filter_query': '{Sentimiento} eq "POS"'},
                        'backgroundColor': '#4CAF50',
                        'color': 'white'
                    },
                    {
                        'if': {'column_id': 'Sentimiento', 'filter_query': '{Sentimiento} eq "NEU"'},
                        'backgroundColor': 'gray',
                        'color': 'black'
                    },
                    {
                        'if': {'column_id': 'Sentimiento', 'filter_query': '{Sentimiento} eq "NEG"'},
                        'backgroundColor': 'red',
                        'color': 'white'
                    },
                ],
            )


            tweet_general_table = dash_table.DataTable(
                id='tabla-tweet-general',
                columns=[
                    {'name': col, 'id': col} for col in filtered_comments_general.columns
                ],
                data=filtered_comments_general.to_dict('records'),
                style_table={'width': '70%', 'margin': '20px auto'},
                style_cell={'padding': '10px', 'textAlign': 'left', 'whiteSpace': 'normal', 'color': 'black'},
                style_header={'backgroundColor': 'lightgrey'},
            )
        else:
            comments_table = []
            tweet_general_table =  html.Div("No hay comentarios", style={'font-size': '20px', 'color': 'red', 'text-align': 'center'})  # Inicializa la tabla tweet_general
    else:
        comments_table = []
        tweet_general_table = []

    return options, dropdown_style, [general_table] ,  [tweet_general_table] , [comments_table] 

# Callback para recargar la página
@app.callback(Output('interval-component', 'disabled'),
              Output('dropdown-usuario', 'options'),
              Output('tabla-users-general', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_layout(n):
    
    if n is None:
        raise PreventUpdate
    
    # Imprime el tiempo actual para verificar
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"Recargando la página a las {current_time}")

    # Cargar datos desde el archivo CSV y agregar una columna de ID automáticamente
    df = tweets_database()

    # Formatear la columna "link_tweet" como enlace "Ver publicación"
    for index, row in df.iterrows():
        df.at[index, 'link_tweet'] = f"[Ver publicación]({row['link_tweet']})"

    opciones_usuario = [{'label': usuario, 'value': usuario} for usuario in df['user_tweet'].unique()]

    # Crear la tabla
    table = dash_table.DataTable(
        id='tabla',
        columns=[
            {'name': 'Usuario', 'id': 'user_tweet'},
            {'name': 'Enlace', 'id': 'link_tweet', 'presentation': 'markdown'},
            {'name': 'Likes', 'id': 'cantidad_likes'},
            {'name': 'Compartido', 'id': 'cantidad_repost'},
            {'name': 'Comentarios', 'id': 'cantidad_comments'},
            {'name': 'Comentarios Positivos', 'id': 'comments_positivos'},
            {'name': 'Comentarios Negativos', 'id': 'comments_negativos'},
            {'name': 'Comentarios Neutros', 'id': 'comments_neutros'},
            {'name': 'Fecha del tweet', 'id': 'fecha_tweet'}

        ],
        data=df.to_dict('records'),
        style_table={'width': '100%'},
        style_cell={'textAlign': 'left'},
        style_header={'backgroundColor': 'lightgrey'},
        style_data_conditional=[
            {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}
        ],
    )


    return False,opciones_usuario,[table]

    


# Callback para reiniciar el segundo Dropdown cuando se cambia el usuario
@app.callback(
        
    Output('dropdown-tweet-id', 'value'),
    [Input('dropdown-usuario', 'value')]
)
def reset_second_dropdown(selected_user):
    return None



if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
