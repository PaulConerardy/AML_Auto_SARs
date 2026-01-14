import pandas as pd
import numpy as np
import os

def generate_mock_data():
    data_dir = "c:/Users/paulc/Documents/Projets/AML SARs/data"
    os.makedirs(data_dir, exist_ok=True)

    # 1. Transactions
    tx_data = {
        "transaction_id": [f"TX{i:05d}" for i in range(100)],
        "customer_id": ["C001", "C001", "C002", "C003", "C001"] * 20,
        "amount": np.random.uniform(100, 15000, 100),
        "currency": ["USD"] * 100,
        "date": pd.date_range(start="2025-11-01", periods=100),
        "description": ["Wire Transfer", "Cash Deposit", "ATM Withdrawal", "Online Purchase", "Zelle"] * 20,
        "counterparty": ["Acme Corp", "Unknown", "Local ATM", "Amazon", "Friend"] * 20
    }
    df_tx = pd.DataFrame(tx_data)
    df_tx.to_csv(os.path.join(data_dir, "transactions.csv"), index=False)

    # 2. KYC Profiles
    kyc_data = {
        "customer_id": ["C001", "C002", "C003"],
        "full_name": ["John Doe", "Jane Smith", "Bob Johnson"],
        "occupation": ["Software Engineer", "Art Dealer", "Consultant"],
        "risk_score": ["Low", "High", "Medium"],
        "address": ["123 Main St, NY", "456 Art Ave, Miami", "789 Biz Rd, Chicago"],
        "onboarding_date": ["2020-01-15", "2021-05-20", "2019-11-10"]
    }
    df_kyc = pd.DataFrame(kyc_data)
    df_kyc.to_csv(os.path.join(data_dir, "kyc_profiles.csv"), index=False)

    # 3. Adverse Media (Mocking as text files)
    media_content = """
    REPORT: Allegations of art fraud involving Jane Smith.
    Local news reports suggest that Jane Smith, owner of Miami Art Gallery, 
    has been linked to a series of questionable high-value transactions 
    involving offshore accounts.
    Date: 2025-12-15
    """
    with open(os.path.join(data_dir, "adverse_media_c002.txt"), "w") as f:
        f.write(media_content)

    print(f"Mock data generated in {data_dir}")

if __name__ == "__main__":
    generate_mock_data()
