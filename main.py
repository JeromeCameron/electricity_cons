import pandas as pd


def main(bills_old, bills_new):
    # Join dataframes
    bills = pd.concat([bills_old, bills_new], ignore_index=True)

    # Correct data types
    bills["date_"] = pd.to_datetime(bills["date_"], format="%d-%m-%y")
    bills["total_charges"] = pd.to_numeric(bills["total_charges"].str.replace(',', '').str.replace("$",""), errors='coerce')
    bills["energy_used"] = bills['energy_used'].str.strip("`")
    bills["energy_used"] = pd.to_numeric(bills['energy_used'], errors='coerce')

    # Add additional columns
    bills["month"] = bills["date_"].dt.month
    bills["year"] = bills["date_"].dt.year
    # bills["cost_per_kwh"] = bills["total_charges"]/bills["energy_used"] # cost charged for each kilowatt of energy used.

    return bills


if __name__ == "__main__":

    old_bills: pd.DataFrame = pd.read_csv(r"data/csv_files/electricity_cons_old_bill_type.csv")
    new_bills: pd.DataFrame = pd.read_csv(r"data/csv_files/electricity_cons_new_bill_type.csv")

    df: pd.DataFrame = main(old_bills, new_bills)
    # print(df["total_charges"].head(20))
    # df.to_csv("jps_bills.csv", index=False)

    # What % of bills are estimated

    # Max kWh cons
    max_kwh_consumption: float = df["energy_used"].max()
    # Max charge
    max_charge: float = df["total_charges"].max()
    # Total spend with jps
    sum_charge: float = df["total_charges"].sum()
    # What I saved from gov discount
    sum_savings: float = df["discount"].sum()

    # Cons trend, am I using more electricity now
    # Cost trend, If im spending more is it becuase I am using more or has fuel prices gone up


