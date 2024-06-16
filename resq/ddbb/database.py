from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker
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
    database_ctx : dict, optional
        Context dict for the database, by default "".

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

    database_ctx: dict = {}

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
        try:
            if self.Session is None or self.metadata is None:
                raise Exception("Database has not connected properly")

            return self.execute_sql_query(sql_query)

        except Exception as e:
            logger.error(f"Error executing SQL query: {e}")
            return [], []

    def create_tables_context(self) -> str:
        """
        Generates a context string for tables in the metadata.

        Returns
        -------
        str
            Context string for the tables in the database metadata.
        """
        try:
            if self.tables is None:
                self.tables = self.metadata.tables.keys()

            tables_lst = []

            for table_name in self.metadata.tables.keys():
                if table_name in self.tables:
                    table = self.metadata.tables[table_name]
                    columns = [
                        f"{column.name} ({str(column.type)})"
                        for column in table.columns
                    ]
                    tables_lst.append({"nombre": table_name, "columnas": columns})

            tables_ctx = ""

            for index, table in enumerate(tables_lst):
                tables_ctx += f"Tabla {index}:\n"
                for key, value in table.items():
                    tables_ctx += f"{key}:"
                    if isinstance(value, list):
                        for item in value:
                            tables_ctx += f"{item}\n"
                    elif isinstance(value, str):
                        tables_ctx += f"{value}\n"
            if "user" in self.database_ctx:
                self.database_ctx["user"] += tables_ctx
            else:
                self.database_ctx["user"] = tables_ctx
            logger.info("Tables context generated successfully")

        except Exception as e:
            logger.error(f"Error generating tables context: {e}")

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
            logger.info(f"Connected correctly to: {self}")

            # Reflect metadata from the database
            self.metadata = MetaData()
            self.metadata.reflect(bind=engine)

            # Create sessionmaker bound to the engine
            self.Session = sessionmaker(bind=engine)

        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
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
            logger.error(f"Error executing SQL query: {e}")
            return [], []

    def generate_province_district_hood_relation(self):
        """
        Generates a relation between provinces, districts, and neighborhood names.

        Queries the database to fetch unique province, district, and neighborhood names
        and organizes them into a nested structure to create context prompts.

        Returns:
            str: The last generated context prompt.
        """
        try:
            # Query to fetch distinct provinces, districts, and neighborhood names, ordered.
            query = """SELECT DISTINCT PROVINCIA, NOMDIS, NOMBRE \
            FROM home_data_extraction.barrio_provincia \
            ORDER BY PROVINCIA, NOMDIS, NOMBRE;"""

            # Execute the query and fetch results
            result = self.Session().execute(text(query))

            # Populate the dictionary with query results
            results = result.fetchall()
            provincias = set(item[0] for item in results)
            distritos = set(item[1] for item in results)

            # Variable to store the last generated context prompt
            neighborhood_ctx = ""

            # Add province information
            neighborhood_ctx += f"Los valores posibles de la columna provincia son : {', '.join(provincias)}\n"
            # Add district information
            neighborhood_ctx += f" Los valores posibles de la columna distrito son : {', '.join(distritos)}\n"

            if "user" in self.database_ctx:
                self.database_ctx["user"] += neighborhood_ctx
            else:
                self.database_ctx["user"] = neighborhood_ctx

            logger.info(
                "Province, district, and neighborhood relation generated successfully"
            )

        except Exception as e:
            logger.error(
                f"Error generating province, district, and neighborhood relation: {e}"
            )

    def get_database_ctx(self):
        """
        Retrieves and stores the database context.

        This method combines multiple context generation functions to compile
        a comprehensive database context.
        """
        try:
            self.create_tables_context()
            self.generate_province_district_hood_relation()
            logger.info("Database context retrieved successfully")

        except Exception as e:
            logger.error(f"Error retrieving database context: {e}")
