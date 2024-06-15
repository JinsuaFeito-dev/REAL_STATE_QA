from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker
from langchain_community.llms import LlamaCpp
from llama_cpp import Llama

from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from pathlib import Path
import gradio as gr
import logging
import json

IMPORTANT_TABLES = ['home_data_extraction.home_processed_extraction',
                    "home_data_extraction.barrio_provincia"]
# Set up SQLAlchemy
DB_HOST = '192.168.1.94'
DB_PORT = '3306'
DB_PASS = 'm6o-7+3o'
DB_USER = 'jorge'
DB_SCHEMA = "home_data_extraction"



def find_second_occurrence(main_str, sub_str):
    first_occurrence = main_str.find(sub_str)
 
    if first_occurrence != -1:
        second_occurrence = main_str.find(sub_str, first_occurrence + 1)
        return second_occurrence if second_occurrence != -1 else -1
    else:
        print("Specified substring not found.")
        return -1
    
def connect_to_database(host: str, port: str, user: str, pasw: str, schema: str):

    engine = create_engine(url=f"mysql+pymysql://{user}:{pasw}@{host}:{port}"
                           )
    metadata = MetaData(schema=schema)
    metadata.reflect(bind=engine)

    Session = sessionmaker(bind=engine)
    return Session(), metadata


def init_llama(kwargs: dict):
    llm = Llama(**kwargs)
    return llm


def get_tables_context(metadata: MetaData, selected_tables: list = []):
    tables_lst = []
    table_names = metadata.tables.keys()
    if not selected_tables:
        selected_tables = table_names
    for table_name in table_names:
        if table_name in selected_tables:
            tables_lst.append({"nombre":table_name,"columnas":[]})
        else:
            continue
        # Get columns for each table
        table = metadata.tables[table_name]
        column_list = []
        for column in table.columns:
            column_list.append(f"{column.name} ({str(column.type)})")
        tables_lst[-1].update({"columnas":column_list})
    tables_str =  ""
    for index,table in enumerate(tables_lst):
        tables_str += f"Tabla {index}:\n"
        for key in table:
            tables_str+=f"{key}:"
            if isinstance(table[key],list):
                for item in table[key]:
                    tables_str+=f"{item}\n"
            if isinstance(table[key],str):
                tables_str+=f"{table[key]}\n"
    return tables_str


def natural_language_to_sql(database_ctx, natural_language_query):
    # Use the language model to convert natural language query to SQL
    # prompt_template = f'''

    #     Esquema Base de Datos: {database_ctx}
    #     Eres un experto de SQL, responde con una query de SQL entre simbolos de dolar $$ siguiendo el formato de los ejemplos y utilizando el esquema de la base de datos.
    #     Ejemplo:
    #     Pregunta: Recuperar todas las columnas de las viviendas que tienen ascensor y cuestan menos de 300,000 euros.
    #     Respuesta:         
    #     $$SELECT * FROM home_data_extraction.home_processed_extraction WHERE ascensor = 1 AND precio < 300000$$
    #     Ahora basandote en el ejemplo, responde a la siguiente pregunta con una unica query de SQL:      
    #     Pregunta: {natural_language_query}
    #     '''

    response = lang_model.create_chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": f"Eres un experto en SQL. Responde con una query de SQL utilizando el esquema de la base de datos."
                },
                {
                    "role": "user",
                    "content": f"Usando el esquema: {database_ctx}.\nRecupera todas las columnas de las viviendas que tienen ascensor y cuestan menos de 300,000 euros."
                },
                {
                    "role": "assistant",
                    "content": "SELECT * FROM home_data_extraction.home_processed_extraction WHERE ascensor = 1 AND precio < 300000"
                },
                                {
                    "role": "user",
                    "content": f"Usando el esquema: {database_ctx}.\n¿Cuántas viviendas hay en la ciudad de Madrid?"
                },
                {
                    "role": "assistant",
                    "content": "SELECT COUNT(*) AS total_viviendas FROM home_data_extraction.home_processed_extraction WHERE provincia = 'Madrid'"
                },
                                {
                    "role": "user",
                    "content": f"Usando el esquema: {database_ctx}.\n¿Cuál es el precio promedio de las viviendas con ascensor en la ciudad de Barcelona?"
                },
                {
                    "role": "assistant",
                    "content": "SELECT AVG(precio) AS precio_promedio FROM home_data_extraction.home_processed_extraction WHERE provincia = 'Barcelona' AND ascensor = 1"
                },
                {
                    "role": "user",
                    "content": f"Usando el esquema: {database_ctx}.\n{natural_language_query}"
                },
            ],
            response_format={
                "type": "json_object",
                "schema": {
                    "type": "object",
                    "properties": {"sql_query": {"type": "string"}},
                    "required": ["sql_query"],
                },
            },
            temperature=0.2,
        )
    try:
        resposnse_json = json.loads(response["choices"][0]["message"]["content"].replace("\n"," "))
    except:
        resposnse_json = {"sql_query": "Error"},
    return resposnse_json["sql_query"]

def execute_sql_query(session: sessionmaker, sql_query: str):
    try:
        result = session.execute(text(sql_query))
        return result.fetchall(), result.keys()
    except Exception as e:
        logging.error(e)
        return [],[]


def process_user_input(database_ctx, input_text):
    # Convert natural language to SQL query
    answer_dict = natural_language_to_sql(database_ctx, input_text)
    # Execute SQL query
    return answer_dict


llama_config = {"model_path": str(Path.joinpath(Path(__file__).parent.parent, r"models/model/Code-Llama-3-8B-Q6_K.gguf").absolute()),
                # The number of layers to put on the GPU. The rest will be on the CPU. If you don't know how many layers there are, you can use -1 to move all to GPU.
                "n_gpu_layers": 27,
                "n_ctx": 3000,
                # Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.
                "n_batch": 3000,
                "callback_manager":  CallbackManager([StreamingStdOutCallbackHandler()]),
                "verbose":  True,  # Verbose is required to pass to the callback manager
                "chat_format":"chatml",
                }
DB_HOST = '192.168.1.94'
DB_PORT = '3306'
DB_PASS = 'm6o-7+3o'
DB_USER = 'jorge'

session, metadata = connect_to_database(
    DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_SCHEMA)
lang_model = init_llama(llama_config)

db_tables_ctx = get_tables_context(metadata, selected_tables=IMPORTANT_TABLES)


def format_response(result, columns):
    import pandas as pd
    df = pd.DataFrame(data=result, columns=columns)
    return df


def gradio_interface(user_input):
    answer = process_user_input(db_tables_ctx, user_input)
    result, columns = execute_sql_query(session, answer)
    #TODO second query when failed
    response = format_response(result, columns)
    return response,f"{answer} --- {response.shape}"


js_func = """
    function refresh() {
        const url = new URL(window.location);

        if (url.searchParams.get('__theme') !== 'dark') {
            url.searchParams.set('__theme', 'dark');
            window.location.href = url.href;
        }
    }
    """
# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO)
with gr.Blocks(js=js_func) as demo:
    gr.Markdown(
            '''
            <div style="text-align:center;">
                <span style="font-size:3em; font-weight:bold; color:rgb(93, 134, 180);">SQL Query Interface</span>
            </div>
            <div style="text-align:center;">
                <span style="font-size:1em; color:rgb(208, 215, 226);">Enter a natural language query to retrieve data from the database</span>
            </div>
            '''
    )
    gr.Image(str(Path.joinpath(Path(
        __file__).parent.parent, r"img/Real-Estate.jpg")),height=480,label="Your Image",show_download_button=False,show_label=False)
    query = gr.Textbox(lines=2, placeholder="Enter your query here...", label="Query")
    output_dataframe = gr.Dataframe(label="Query Results")
    output_text = gr.Textbox(lines=2, placeholder="Output text...", label="Text Output")

    submit_button = gr.Button("Submit")

    submit_button.click(fn = gradio_interface, inputs=query, outputs=[output_dataframe, output_text])
    
# Dummy user data (replace with database)
users = {"RESQ": "RESQ"}

def authenticate(username, password):
    if username in users and users[username] == password:
        return True
    return False

# Launch the Gradio app
if __name__ == "__main__":
    demo.launch(
        share = True
                # , auth=authenticate
                )

