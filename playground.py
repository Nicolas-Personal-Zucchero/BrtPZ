"""Interactive manual testing playground for BrtPZ.

Allows quick end-to-end testing of shipment creation, label generation,
and cancellation with real credentials.

Usage:
1. Ensure your '.env' contains your BRT credentials:
   cp template.env .env
   # Edit .env with your BRT_USER_ID, BRT_PASSWORD, etc.

2. Run:
   python3 playground.py
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path

from brt_pz import BrtPZ, CreateData, LabelParameters


def load_env_file(filepath: str | Path = ".env") -> None:
    """Load key=val pairs from a .env file into os.environ."""
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

    if not user_id or user_id == "your_user_id_here" or not password:
        print("[!] BRT credentials not configured!")
        print("    Please copy 'template.env' to '.env' and set your real credentials.")
        return

    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    logger = logging.getLogger("playground")

    client = BrtPZ(
        user_id=user_id,
        password=password,
        customer_code=customer_code,
        departure_depot=departure_depot,
        logger=logger,
    )
    print(f"[+] BrtPZ initialized successfully. Target URL: {client.base_url}")
    print(
        f"[+] Account: user_id={client.user_id}, "
        f"customer_code={client.customer_code}, depot={client.departure_depot}"
    )

    # Unique reference based on current epoch seconds (modulo 10^7)
    sample_ref = int(time.time()) % 10000000
    alpha_ref = f"TEST-{sample_ref}"

    # =============================================================
    # 1. CREATE SHIPMENT
    # =============================================================
    print("\n" + "=" * 60)
    print("STEP 1: CREATING SHIPMENT")
    print("=" * 60)

    shipment_payload: CreateData = {
        "departureDepot": client.departure_depot or 102,
        "senderCustomerCode": client.customer_code or 1020100,
        "deliveryFreightTypeCode": "DAP",
        "consigneeCompanyName": "Spedizione di prova BrtRestApi",
        "consigneeAddress": "Via Enrico Mattei 54",
        "consigneeZIPCode": "40138",
        "consigneeCity": "BOLOGNA",
        "consigneeProvinceAbbreviation": "BO",
        "consigneeCountryAbbreviationISOAlpha2": "IT",
        "consigneeContactName": "MARIO ROSSI",
        "consigneeTelephone": "051456778",
        "consigneeEMail": "test@example.com",
        "consigneeMobilePhoneNumber": "3351234567",
        "isAlertRequired": "0",
        "numberOfParcels": 1,
        "weightKG": 1.5,
        "numericSenderReference": sample_ref,
        "alphanumericSenderReference": alpha_ref,
    }

    label_params: LabelParameters = {
        "outputType": "PDF",
        "offsetX": "0",
        "offsetY": "0",
        "isBorderRequired": "0",
        "isLogoRequired": "0",
        "isBarcodeControlRowRequired": "0",
    }

    print(f"[*] Sending create_shipment request (Reference: {sample_ref} / {alpha_ref})...")
    create_result = client.create_shipment(
        shipment_payload,
        is_label_required="1",
        label_parameters=label_params,
    )

    if not create_result:
        print("[-] Failed to receive a response from BRT API.")
        return

    pretty_print("CREATE SHIPMENT RESPONSE", create_result)

    create_resp = create_result.get("createResponse", {})
    exec_msg = create_resp.get("executionMessage", {})
    code = exec_msg.get("code")

    print(f"\n[i] Execution Code: {code}")
    print(f"[i] Execution Message: {exec_msg.get('codeDesc')} - {exec_msg.get('message')}")

    # =============================================================
    # 2. SAVE GENERATED LABEL (IF PRESENT)
    # =============================================================
    labels_container = create_resp.get("labels", {})
    label_list = labels_container.get("label", [])
    if label_list:
        print("\n" + "=" * 60)
        print("STEP 2: SAVING LABEL")
        print("=" * 60)
        first_label = label_list[0]
        out_path = Path("labels") / f"label_{sample_ref}.pdf"
        saved = client.save_label(first_label, out_path)
        print(f"[+] Label saved successfully to: {saved.resolve()}")
    else:
        print("\n[!] No labels returned in response.")

    # =============================================================
    # 3. SHIPMENT DELETION (OPTIONAL)
    # =============================================================
    print("\n" + "=" * 60)
    print("STEP 3: DELETE SHIPMENT (OPTIONAL)")
    print("=" * 60)
    print("Note: According to BRT documentation, cancellation should ideally")
    print("be sent at least 5 minutes after creation and before depot takeover.")

    choice = input("\nDo you want to test delete_shipment now? [y/N]: ").strip().lower()
    if choice in ("y", "yes"):
        print(f"[*] Sending delete_shipment for numericSenderReference={sample_ref}...")
        del_result = client.delete_shipment(
            numeric_sender_reference=sample_ref,
            alphanumeric_sender_reference=alpha_ref,
        )
        if del_result:
            pretty_print("DELETE SHIPMENT RESPONSE", del_result)
        else:
            print("[-] Delete request failed.")
    else:
        print(f"[*] Skipping delete. Reference {sample_ref} remains created.")


if __name__ == "__main__":
    main()
