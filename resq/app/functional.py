import pandas as pd
from loguru import logger
from pathlib import Path
import yaml
import sys
from typing import Any, Dict, List, Union

# Dummy user data (replace with database)
users = {"RESQ": "RESQ"}


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
            raise yaml.YAMLError(f"Error parsing YAML file: {e}")
    # Check if the username exists in the users dictionary and if the provided password matches
    if username in login["users"] and login["passwords"][users] == password:
        return True  # Authentication successful
    return False  # Authentication failed


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
            raise yaml.YAMLError(f"Error parsing YAML file: {e}")

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
            raise yaml.YAMLError(f"Error parsing YAML file: {e}")

    logger.info(f"Database configuration loaded successfully from {config_path}")
    return ddbb_cfg


def format_response(
    result: List[tuple], columns: Union[List[str], None] = None
) -> pd.DataFrame:
    """
    Format a result set into a pandas DataFrame.

    Parameters
    ----------
    result : List[tuple]
        List of tuples representing the rows of the result set.
    columns : Union[List[str], None], optional
        List of column names. If None, columns will be inferred from the result data.

    Returns
    -------
    pd.DataFrame
        Pandas DataFrame containing the formatted data.

    Notes
    -----
    Assumes each tuple in result corresponds to a row in the DataFrame.
    """
    # Create a DataFrame from the result with specified columns
    df = pd.DataFrame(data=result, columns=columns)
    return df


def process_chat(llm_model, database, user_input):
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
    # ==================================================================
    # Initialize weights and connect to database
    if llm_model.llm == None:
        llm_model._initialize_model()
    if database.Session == None:
        database.connect_to_database()
        database.create_tables_context()

    # Generate the query using the language model
    query = llm_model.infer(user_input)

    # Execute the query on the database and retrieve the results
    result, columns = database.query(query)

    # TODO: Implement a second query attempt if the first one fails

    # Format the response into a DataFrame
    response = format_response(result, columns)

    # Return the response DataFrame and additional info string
    return response, f"{query}"


def extract_log_data(
    logs_path,
):

    log = read_logs(logs_path)

    return log


def read_logs(
    logs_path,
):
    """
    Extracts log data from the specified log file.

    Args:
    - logs_path (str): Path to the directory containing log files.

    Returns:
    - str: Contents of the log file as a string.
    """
    # Ensure any buffered output is flushed
    sys.stdout.flush()

    # Convert logs_path to a Path object for better manipulation
    logs_path = Path(logs_path)

    # Find the first .log file recursively within the logs_path directory
    log_file = next(logs_path.glob("**/*.log"))

    # Open and read the contents of the log file
    with open(log_file, "r") as f:
        return f.read()
