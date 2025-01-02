import os, re
from model import Bill
from pathlib import Path
import pandas as pd
from tqdm import tqdm
from pdfminer.high_level import extract_text



def check_if_valid_path(text: str) -> bool:
    """
    :param text: user input to check if path
    :return: A boolean
    """
    if os.path.isdir(text):
        return True
    else:
        return False

def get_identifier(extracted_text: str, regx: str) -> str:
    """
    :param extracted_text: Text extracted from PDF file
    :param regx: regx pattern
    :return: A string that matches regex pattern.
    """
    match = re.search(regx, extracted_text)

    try:
        identifier = match.group(1)
    except IndexError:
        identifier = match.group()
    except AttributeError:
        identifier = ""

    return identifier

def get_values(extracted_text: str, **kwargs) -> Bill:
    """
    :param extracted_text: Text extracted from PDF file
    :return: bill details as type Bill(Data Class)
    """

    bill: Bill = Bill(
        invoice_no = get_identifier(extracted_text, kwargs['invoice_no']) + "`",
        service_address = get_identifier(extracted_text, kwargs['service_address']).replace("SERVICE ADDRESS: ",""),
        date_= get_identifier(extracted_text, kwargs['date_']).replace("BY: ","").strip(),
        read_type = get_identifier(extracted_text, kwargs['read_type']),
        billing_period = get_identifier(extracted_text, kwargs['billing_period']).replace("Days","").strip(),
        energy_used = get_identifier(extracted_text, kwargs['energy_used']) + "`",
        total_charges = get_identifier(extracted_text, kwargs['total_charges']).replace("Total: ",""),
    )
    return bill

def get_bills(directory: Path, regex_patterns: dict) -> list[Bill]:
    """
    :param directory: Folder containing invoices
    :param regex_patterns: dictionary containing all regex patterns
    :return: A list of invoice details
    """
    bills: list = []
    for file in tqdm(os.listdir(directory)):
        if file.endswith(".pdf"):
            extracted_text: str = extract_text(Path(directory) / file)
            bill: Bill = get_values(extracted_text, **regex_patterns)
            bills.append(bill)
    return bills

def main(directory: Path, regex_patterns: dict) -> pd.DataFrame:
    """
    :param directory: Folder containing bills
    :param regex_patterns: dictionary containing all regex patterns
    :return: Pandas dataframe of electricity bills
    """
    bills: list[Bill] = get_bills(directory, regex_patterns)
    data = [bill.model_dump() for bill in bills]
    df = pd.DataFrame(data)
    df["date_"] = pd.to_datetime(df["date_"], format="%d-%b-%Y")
    return df


if __name__ == "__main__":

    # Regex Patterns
    reg_patterns_old_format: dict = {
                    "invoice_no": r"\d{10,}",  # Invoice no for bill
                    "service_address": r"Service Name \/ Address:\n(?:.*\n)?(.*)",  # service address for jps account
                    "date_": r"\b\d{2}-[A-Z]{3}-\d{4}\b",  # Bill read date
                    "read_type": r"Actual\b|Estimated",  # read type of bill actual vs estimated
                    "billing_period": r"No\. of Days\s+(\d+)",  # Number of days
                    "energy_used": r"TOTAL AMOUNT DUE\s+(\d{2,}\.\d+)",  # kwh consumption
                    "total_charges": r"Current\s+Charges\s+\$([\d,]+\.\d{2})",  # total amount charged
                    }

    reg_patterns_new_format: dict ={
                    "invoice_no": r"\d{10,}",  # Invoice no for bill
                    "service_address": r"SERVICE ADDRESS: .{10,}",  # service address for jps account
                    "date_": r"BY:\s+\d{2}-[A-Za-z]{3}-\d{4}",  # Bill read date
                    "read_type": r"Actual\b|Estimated",  # read type of bill actual vs estimated
                    "billing_period": r"(\d+)\s+Days",  # Number of days
                    "energy_used": r"ENERGY[\s\S]*?\n(?:.*\n){8}(\d{2,3}\.\d{2})", # kwh consumption
                    "total_charges": "Total:.{10,}", # total amount charged
                    }

    valid_path: bool = False
    path: Path = Path()
    bill_type: str = ""

    # Check if valid path
    while not valid_path:
        ques_path: str = input("Please enter path to folder with bills: \n")
        ques_bill_type: str = input("Please enter bill type. Type 'old' or 'new': \n")

        if check_if_valid_path(ques_path):
            path = Path(ques_path)
            bill_type = ques_bill_type.lower()
            valid_path = True

    regEx_patterns: dict = reg_patterns_old_format if bill_type=="old" else reg_patterns_new_format
    bills_batch = main(path, regEx_patterns)
    #bills_batch.to_csv(os.getcwd() + "_bills.csv", index=False)