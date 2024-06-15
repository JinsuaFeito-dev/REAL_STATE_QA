from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker
import logging
from pydantic import BaseModel, ConfigDict
from loguru import logger

class MySQL_database(BaseModel):
    """
    A model class for handling interactions with a MySQL database, including
    connection management, query execution, and context generation for tables.

    Attributes
    ----------
    Session : sessionmaker, optional
        SQLAlchemy sessionmaker object bound to a database engine, by default None.
    metadata : MetaData, optional
        SQLAlchemy MetaData object for reflecting database schema, by default None.
    host : str
        Database host address.
    port : str
        Port number to connect to the database.
    ddbb_schema : str
        Database schema name.
    tables : list
        List of table names to include in the context.
    user : str
        Username for database authentication.
    password : str
        Password for database authentication.
    database_ctx : str, optional
        Context string for the database, by default "".

    Methods
    -------
    __init__(**data)
        Initializes the MySQL database model with the provided configuration.
    __str__()
        Returns a string representation of the database configuration.
    query(sql_query)
        Executes a SQL query and returns the results.
    create_tables_context()
        Generates a context string for tables in the metadata.
    connect_to_database()
        Connects to the specified database and returns a session and metadata.
    execute_sql_query(session, sql_query)
        Executes a SQL query using the provided session and returns the results.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    Session: sessionmaker = None
    metadata: MetaData = None

    host: str
    port: str
    ddbb_schema: str
    tables: list

    user: str
    password: str

    database_ctx: str = ""

    def __init__(self, **data):
        """
        Initializes the MySQL database model with the provided configuration.

        Parameters
        ----------
        **data : dict
            Configuration data for the database.
        """
        super().__init__(**data)

    def __str__(self):
        """
        Returns a string representation of the database configuration.

        Returns
        -------
        str
            String representation of the database configuration.
        """
        return f"DatabaseConfig(host={self.host}, port={self.port}, schema={self.ddbb_schema}, tables={self.tables})"

    def query(self, sql_query: str) -> tuple:
        """
        Executes a SQL query and returns the results.

        Parameters
        ----------
        sql_query : str
            SQL query to execute.

        Returns
        -------
        tuple
            A tuple containing two elements:
            - A list of tuples representing the fetched rows from the query result.
            - A list of column names (keys) of the result set.

        Notes
        -----
        If the session or metadata is not properly initialized, an error is logged
        and None is returned.
        """
        if self.Session is None or self.metadata is None:
            logging.error("Database has not connected properly")
            return
        return self.execute_sql_query(sql_query)

    def create_tables_context(self) -> str:
        """
        Generates a context string for tables in the metadata.

        Returns
        -------
        str
            Context string for the tables in the database metadata.
        """
        if self.tables is None:
            self.tables = self.metadata.tables.keys()

        tables_lst = []

        for table_name in self.metadata.tables.keys():
            if table_name in self.tables:
                table = self.metadata.tables[table_name]
                columns = [
                    f"{column.name} ({str(column.type)})"
                    for column in table.ddbb_schema
                ]
                tables_lst.append({"nombre": table_name, "columnas": columns})

        self.database_ctx = ""

        for index, table in enumerate(tables_lst):
            self.database_ctx += f"Tabla {index}:\n"
            for key, value in table.items():
                self.database_ctx += f"{key}:"
                if isinstance(value, list):
                    for item in value:
                        self.database_ctx += f"{item}\n"
                elif isinstance(value, str):
                    self.database_ctx += f"{value}\n"

        return self.database_ctx

    def connect_to_database(self):
        """
        Connects to the specified database and returns a session and metadata.

        Raises
        ------
        Exception
            If there is an error during database connection or metadata reflection.
        """
        try:
            # Create engine and bind to the database
            engine = create_engine(
                f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.ddbb_schema}"
            )
            logger.info(f"Connected correctly to:\n {self}")

            # Reflect metadata from the database
            self.metadata = MetaData()
            self.metadata.reflect(bind=engine)

            # Create sessionmaker bound to the engine
            self.Session = sessionmaker(bind=engine)

        except Exception as e:
            logging.error(f"Error connecting to database: {e}")
            raise  # Re-raise the exception for higher-level handling

    def execute_sql_query(self, sql_query) -> tuple:
        """
        Executes a SQL query using the provided session and returns the results.

        Parameters
        ----------

        sql_query : str
            SQL query to execute.

        Returns
        -------
        tuple
            A tuple containing two elements:
            - A list of tuples representing the fetched rows from the query result.
            - A list of column names (keys) of the result set.

        Notes
        -----
        If an error occurs during execution, it is logged, and empty lists are returned.
        """
        try:
            result = self.Session().execute(text(sql_query))
            return result.fetchall(), result.keys()
        except Exception as e:
            logging.error(e)
            return [], []
