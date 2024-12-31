from pdfminer.high_level import extract_text
from pydantic import BaseModel
import re
import os
from pathlib import Path
import pandas as pd
from tqdm import tqdm

# Data model using pydantic
class Bill(BaseModel):
    invoice_no: str
    service_address: str
    date_: str
    read_type: str
    billing_period: str
    energy_used: str
    total_charges: str


def check_if_valid_path(text: str) -> bool:
    """
    :param text: user input to check if path
    :return: A boolean
    """
    if os.path.isdir(text):
        return True
    else:
        return False

def get_identifier(extracted_text: str, regx: str) -> str | None:
    """
    :param extracted_text: Text extracted from PDF file
    :param regx: regx pattern
    :return: A string that matches regex pattern.
    """
    try:
        pattern = re.search(regx, extracted_text)
        identifier: str | None = pattern.group()
    except AttributeError:
        identifier = None
    return identifier


def get_values(extracted_text: str) -> Bill:
    """
    :param extracted_text: Text extracted from PDF file
    :return: Invoice details as type Invoice(Data Class)
    """
    # RegX Patterns
    invoice_no: str = r"\d{10,}"  # Invoice number
    service_address: str = r"SERVICE ADDRESS: .{10,}"  # service address for jps account
    date_: str = r"()" # Bill read date
    read_type: str = r"Actual\b|Estimated"  # read type of bill actual vs estimated
    billing_period: str = r"(\d+)\s+Days\)"
    energy_used: str = r"^\d+\.\d{2}$"  # kwh consumption
    total_charges: str ="Total:.{10,}"

    invoice: Bill = Bill(
        invoice_no = get_identifier(extracted_text, invoice_no),
        service_address = get_identifier(extracted_text, service_address).replace("SERVICE ADDRESS: ",""),
        date_= get_identifier(extracted_text, date_),
        read_type = get_identifier(extracted_text, read_type),
        billing_period = get_identifier(extracted_text, billing_period).replace("Days","").strip(),
        energy_used = get_identifier(extracted_text, energy_used),
        total_charges = get_identifier(extracted_text, total_charges).replace("Total: ",""),
    )
    return invoice

def get_invoices(directory: Path) -> list[Bill]:
    """
    :param directory: Folder containing invoices
    :return: A list of invoice details
    """
    bills: list = []
    for file in tqdm(os.listdir(directory)):
        if file.endswith(".pdf"):
            extracted_text: str = extract_text(Path(directory) / file)
            bill: Bill = get_values(extracted_text)
            bills.append(bill)
    return bills

def main(directory: Path) -> pd.DataFrame:
    """
    :param directory: Folder containing invoices
    :return: Pandas dataframe fo invoices
    """
    bills: list[Bill] = get_invoices(directory)
    data = [invoice.model_dump() for invoice in bills]
    df = pd.DataFrame(data)
    # df["date_"] = pd.to_datetime(df["date_"], format="%m/%d/%Y")
    return df



if __name__ == "__main__":

    valid_path: bool = False
    path: Path = Path()

    while not valid_path:
        user_input: str = input("Please enter path to folder with bills: \n")
        if check_if_valid_path(user_input):
            path = Path(user_input)
            valid_path = True

    bills_batch = main(path)
    # print(bills_batch)
    bills_batch.to_csv(path / "bills.csv", index=False)