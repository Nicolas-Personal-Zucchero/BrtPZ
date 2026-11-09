"""Manual development playground for BrtPZ.

This script is not part of the distributed package and can be used
to test API calls interactively during development.

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
    security_token = os.getenv("BRT_SECURITY_TOKEN")
    customer_code = os.getenv("BRT_CUSTOMER_CODE")
    departure_depot = os.getenv("BRT_DEPARTURE_DEPOT")
    sandbox = os.getenv("BRT_SANDBOX", "true").lower() in ("true", "1", "yes")

    if not user_id or user_id == "your_user_id_here":
        print("[!] BRT credentials not configured!")
        print("    Copy 'template.env' to '.env' and set your credentials before running.")
        return

    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    logger = logging.getLogger("playground")

    client = BrtPZ(
        user_id=user_id,
        security_token=security_token,
        customer_code=customer_code,
        departure_depot=departure_depot,
        sandbox=sandbox,
        logger=logger,
    )
    print(f"[+] BrtPZ initialized successfully (Sandbox: {sandbox}).")

    # =============================================================
    # MANUAL TESTS: UNCOMMENT THE SECTION YOU WISH TO RUN
    # =============================================================

    # -------------------------------------------------------------
    # 1. ROUTING & DEPOT CHECK
    # -------------------------------------------------------------
    # print("\n--- Testing Routing (40121 Bologna) ---")
    # routing_info = client.get_routing(zip_code="40121", country_code="IT", city="Bologna")
    # pretty_print("Routing Info", routing_info)

    # -------------------------------------------------------------
    # 2. BRT-FERMOPOINT / PUDO SEARCH
    # -------------------------------------------------------------
    # print("\n--- Testing PUDO Search (40121 Bologna) ---")
    # pudo_points = client.search_pudo(zip_code="40121", country_code="IT", max_results=5)
    # pretty_print("PUDO Locations", pudo_points)

    # -------------------------------------------------------------
    # 3. TRACKING BY PARCEL ID
    # -------------------------------------------------------------
    # print("\n--- Testing Tracking by Parcel ID ---")
    # TEST_PARCEL_ID = "000000000000"
    # tracking_data = client.get_tracking_by_parcel_id(TEST_PARCEL_ID)
    # pretty_print("Parcel Tracking", tracking_data)

    # -------------------------------------------------------------
    # 4. TRACKING BY SHIPMENT ID
    # -------------------------------------------------------------
    # print("\n--- Testing Tracking by Shipment ID ---")
    # TEST_SHIPMENT_ID = "00000000"
    # shipment_tracking = client.get_tracking_by_shipment_id(TEST_SHIPMENT_ID)
    # pretty_print("Shipment Tracking", shipment_tracking)

    # -------------------------------------------------------------
    # 5. CREATE SHIPMENT (TEST CONSIGNMENT)
    # -------------------------------------------------------------
    # print("\n--- Testing Shipment Creation ---")
    # test_payload = {
    #     "recipient": {
    #         "name": "Mario Rossi",
    #         "address": "Via Indipendenza 1",
    #         "zipCode": "40121",
    #         "city": "Bologna",
    #         "countryCode": "IT",
    #         "contactPhone": "3331234567"
    #     },
    #     "parcels": [
    #         {"weightKg": 1.5, "lengthCm": 20, "widthCm": 15, "heightCm": 10}
    #     ],
    #     "customerReference": "ORDER-2026-TEST-01"
    # }
    # created_shipment = client.create_shipment(test_payload)
    # pretty_print("Created Shipment", created_shipment)

    # -------------------------------------------------------------
    # 6. DOWNLOAD LABEL (PDF)
    # -------------------------------------------------------------
    # print("\n--- Testing Label Retrieval ---")
    # label_pdf = client.get_label(shipment_id="TEST_ID", label_format="PDF")
    # if label_pdf:
    #     output_path = Path("test_label.pdf")
    #     output_path.write_bytes(label_pdf)
    #     print(f"[+] Label written to {output_path}")


if __name__ == "__main__":
    main()
