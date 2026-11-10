"""Manual development playground for BrtPZ.

This script is not part of the distributed package and can be used
to test BRT API calls interactively during development.

Setup:
1. Create a '.env' file by copying 'template.env':
   cp template.env .env
2. Insert your BRT credentials in '.env'
3. Run:
   python playground.py
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from brt_pz import BrtPZ


def load_env_file(filepath: str | Path = ".env") -> None:
    """Load variables from a .env file into the system environment (no external dependencies)."""
    env_path = Path(filepath)
    if not env_path.is_file():
        return

    with env_path.open(encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, val = stripped.split("=", 1)
            key = key.strip()
            val = val.strip().strip("'\"")
            os.environ.setdefault(key, val)


def pretty_print(title: str, data: object) -> None:
    """Print formatted JSON output."""
    print(f"\n{'='*25} {title} {'='*25}")
    print(json.dumps(data, indent=2, default=str))


def main() -> None:
    load_env_file()

    user_id = os.getenv("BRT_USER_ID")
    password = os.getenv("BRT_PASSWORD")
    raw_customer_code = os.getenv("BRT_CUSTOMER_CODE")
    customer_code = int(raw_customer_code) if raw_customer_code else None
    raw_departure_depot = os.getenv("BRT_DEPARTURE_DEPOT")
    departure_depot = int(raw_departure_depot) if raw_departure_depot else None
    sandbox = os.getenv("BRT_SANDBOX", "true").lower() in ("true", "1", "yes")

    if not user_id or user_id == "your_user_id_here" or not password:
        print("[!] BRT credentials not configured!")
        print("    Copy 'template.env' to '.env' and set your credentials before running.")
        return

    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    logger = logging.getLogger("playground")

    client = BrtPZ(
        user_id=user_id,
        password=password,
        customer_code=customer_code,
        departure_depot=departure_depot,
        sandbox=sandbox,
        logger=logger,
    )
    print(f"[+] BrtPZ initialized successfully (Sandbox: {sandbox}, Base URL: {client.base_url}).")

    # =============================================================
    # 1. CREATE SHIPMENT (TEST CONSIGNMENT)
    # =============================================================
    # print("\n--- Testing Shipment Creation ---")
    # test_payload: CreateData = {
    #     "departureDepot": int(departure_depot or 102),
    #     "senderCustomerCode": int(customer_code or 1020100),
    #     "deliveryFreightTypeCode": "DAP",
    #     "consigneeCompanyName": "Spedizione di prova BrtRestApi",
    #     "consigneeAddress": "Via Enrico Mattei 54",
    #     "consigneeZIPCode": "40138",
    #     "consigneeCity": "BOLOGNA",
    #     "consigneeProvinceAbbreviation": "BO",
    #     "consigneeCountryAbbreviationISOAlpha2": "IT",
    #     "consigneeContactName": "MARIO ROSSI",
    #     "consigneeTelephone": "051456778",
    #     "consigneeEMail": "test@example.com",
    #     "consigneeMobilePhoneNumber": "3351234567",
    #     "isAlertRequired": "0",
    #     "pricingConditionCode": "002",
    #     "numberOfParcels": 1,
    #     "weightKG": 1.5,
    #     "volumeM3": 0.01,
    #     "numericSenderReference": 99001,
    #     "alphanumericSenderReference": "TEST-REF-01",
    # }
    # created_shipment = client.create_shipment(
    #     test_payload,
    #     is_label_required=True,
    #     label_parameters={
    #         "outputType": "PDF",
    #         "offsetX": 0,
    #         "offsetY": 0,
    #         "isBorderRequired": "0",
    #         "isLogoRequired": "0",
    #         "isBarcodeControlRowRequired": "0",
    #     },
    # )
    # pretty_print("Created Shipment", created_shipment)

    # =============================================================
    # 2. DELETE SHIPMENT
    # =============================================================
    # Note: BRT requires waiting at least 5 minutes after creation
    # before attempting deletion.
    # print("\n--- Testing Shipment Deletion ---")
    # delete_result = client.delete_shipment(
    #     numeric_sender_reference=99001,
    #     alphanumeric_sender_reference="TEST-REF-01",
    # )
    # pretty_print("Delete Result", delete_result)


if __name__ == "__main__":
    main()
