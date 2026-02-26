## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()

from crewai.tools import tool
from crewai_tools import SerperDevTool
from langchain_community.document_loaders import PyPDFLoader

## Creating search tool
search_tool = SerperDevTool()

## Creating custom pdf reader tool using @tool decorator
@tool("Financial Document Reader")
def read_financial_document(file_path: str = "data/sample.pdf") -> str:
    """Tool to read and extract text content from a PDF financial document.

    Args:
        file_path (str, optional): Path to the PDF file. Defaults to 'data/sample.pdf'.

    Returns:
        str: Extracted text content from the financial document.
    """
    if not os.path.exists(file_path):
        return f"Error: File not found at path '{file_path}'. Please provide a valid file path."

    try:
        loader = PyPDFLoader(file_path=file_path)
        docs = loader.load()

        full_report = ""
        for page in docs:
            content = page.page_content

            # Clean and format the financial document data
            # Remove excessive blank lines while preserving structure
            while "\n\n\n" in content:
                content = content.replace("\n\n\n", "\n\n")

            full_report += content + "\n"

        if not full_report.strip():
            return "Warning: The document appears to be empty or could not be parsed."

        return full_report.strip()

    except Exception as e:
        return f"Error reading PDF file: {str(e)}"


## Creating Investment Analysis Tool
@tool("Investment Data Processor")
def process_investment_data(financial_data: str) -> str:
    """Process and clean financial document data for investment analysis.

    Args:
        financial_data (str): Raw financial document text to process.

    Returns:
        str: Cleaned and formatted financial data ready for analysis.
    """
    if not financial_data or not financial_data.strip():
        return "Error: No financial data provided for processing."

    processed_data = financial_data.strip()

    # Normalize whitespace — remove excessive spaces
    while "  " in processed_data:
        processed_data = processed_data.replace("  ", " ")

    return processed_data


## Creating Risk Assessment Tool
@tool("Risk Data Extractor")
def extract_risk_data(financial_data: str) -> str:
    """Extract and organize risk-related data from financial documents.

    Args:
        financial_data (str): Financial document text to extract risk data from.

    Returns:
        str: Organized risk-related data points.
    """
    if not financial_data or not financial_data.strip():
        return "Error: No financial data provided for risk extraction."

    return financial_data.strip()