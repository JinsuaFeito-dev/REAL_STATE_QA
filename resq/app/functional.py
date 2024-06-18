import pandas as pd
from loguru import logger
from pathlib import Path
import yaml
import sys
from typing import Any, Dict, List, Union

from resq.llm.model import llm_model
from resq.ddbb.database import MySQL_database


def authenticate(username, password):
    """
    Authenticate a user based on username and password.

    Parameters
    ----------
    username : str
        The username to authenticate.
    password : str
        The password associated with the username.

    Returns
    -------
    bool
        True if authentication succeeds (username exists and password matches), False otherwise.
    """
    login_config = Path(__file__).parent.parent.parent / "config/login.yaml"
    with open(login_config, "r") as f:
        try:
            login = yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file: {e}")
            raise

    if username in login["users"] and login["passwords"].get(username) == password:
        logger.info(f"User '{username}' authenticated successfully")
        return True
    else:
        logger.warning(f"Failed authentication attempt for user '{username}'")
        return False


def get_model_config(config_path: Path) -> Dict[str, Any]:
    """
    Load the model configuration from a YAML file.

    Parameters
    ----------
    config_path : Path
        Path to the YAML configuration file.

    Returns
    -------
    dict
        Dictionary containing the model configuration.

    Raises
    ------
    FileNotFoundError
        If the specified config_path does not exist.
    yaml.YAMLError
        If there is an error parsing the YAML file.
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        try:
            model_cfg = yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file: {e}")
            raise

    logger.info(f"Model configuration loaded successfully from {config_path}")
    return model_cfg


def get_ddbb_config(config_path: Path) -> Dict[str, Any]:
    """
    Load the database configuration from a YAML file.

    Parameters
    ----------
    config_path : Path
        Path to the YAML configuration file.

    Returns
    -------
    dict
        Dictionary containing the database configuration.

    Raises
    ------
    FileNotFoundError
        If the specified config_path does not exist.
    yaml.YAMLError
        If there is an error parsing the YAML file.
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        try:
            ddbb_cfg = yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file: {e}")
            raise

    logger.info(f"Database configuration loaded successfully from {config_path}")
    return ddbb_cfg

def process_chat(model, database, user_input):
    """
    Processes user input through a language model and database, then formats and returns the response.

    Parameters
    ----------
    llm_model : gr.State
        A language model function that processes the user input and generates a query.
    database : gr.State
        A database function that executes the generated query and returns the result and column names.
    user_input : str
        The input provided by the user.

    Returns
    -------
    tuple
        A tuple containing:
        - response: pd.DataFrame
            A DataFrame with the formatted results from the database query.
        - info: str
            A string combining the generated query and the shape of the response DataFrame.
    """
    try:
        # Initialize weights and connect to database if necessary
        if database is None:
            ddbb_config = get_ddbb_config(
                Path(__file__).parent.parent.parent / "config/mysql.yaml"
            )
            database = MySQL_database(**ddbb_config)
            database.connect_to_database()
            database.get_database_ctx()
            logger.info("Connected to database and obtained database context")

        if model is None:

            model_config = get_model_config(
                Path(__file__).parent.parent.parent / "models/cfg/config.yaml"
            )
            model = llm_model(**model_config)
            model._initialize_model()
            model.database_context = database.database_ctx
            logger.info("Initialized language model")

        # Generate the query using the language model
        query = model.infer(user_input)

        # Execute the query on the database and retrieve the results
        response = database.pandas_query(query)

        logger.info(f"Processed user input with query: {query}")
        return response, f"{query}", model, database

    except Exception as e:
        logger.error(f"Error processing user input: {e}")
        raise


def extract_log_data(logs_path):
    """
    Extracts log data from the specified log file.

    Args:
    - logs_path (str): Path to the directory containing log files.

    Returns:
    - str: Contents of the log file as a string.
    """
    try:
        log = read_logs(logs_path)
        logger.debug(f"Extracted log data from '{logs_path}' successfully")
        return log
    except Exception as e:
        logger.error(f"Error extracting log data: {e}")
        raise


def read_logs(logs_path):
    """
    Reads log data from the specified log file.

    Args:
    - logs_path (str): Path to the directory containing log files.

    Returns:
    - str: Contents of the log file as a string.
    """
    try:
        # Ensure any buffered output is flushed
        sys.stdout.flush()

        # Convert logs_path to a Path object for better manipulation
        logs_path = Path(logs_path)

        # Find the first .log file recursively within the logs_path directory
        log_file = next(logs_path.glob("**/*.log"))

        # Open and read the contents of the log file
        with open(log_file, "r") as f:
            return f.read()

    except Exception as e:
        logger.error(f"Error reading logs from '{logs_path}': {e}")
        raise
