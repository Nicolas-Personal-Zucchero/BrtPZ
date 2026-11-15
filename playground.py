"""Interactive manual testing playground for BrtPZ.

Allows quick testing of shipment creation, label generation, and cancellation
with real credentials, organized into 3 separate callable action functions.

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
from typing import Any

from brt_pz import (
    BrtPZ,
    CreateData,
    CreateResult,
    DeleteResult,
    LabelParameters,
    ParcelIDResult,
)


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


def get_client() -> BrtPZ | None:
    """Initialize BrtPZ client from .env configuration."""
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
        return None

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
    return client


# =============================================================================
# ACTION 1: CREATE SHIPMENT
# =============================================================================

def action_create_shipment(
    client: BrtPZ,
    numeric_ref: int | None = None,
    alphanumeric_ref: str | None = None,
    output_type: str = "ZPL",
) -> CreateResult | None:
    """Action 1: Send create_shipment request to BRT."""
    ref = numeric_ref if numeric_ref is not None else (int(time.time()) % 10000000)
    alpha = alphanumeric_ref if alphanumeric_ref is not None else f"TEST-{ref}"

    print("\n" + "=" * 60)
    print("ACTION 1: CREATE SHIPMENT")
    print("=" * 60)
    print(f"[*] Sending create_shipment (Reference: {ref} / {alpha}, Format: {output_type})...")

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
        "isCODMandatory": "0",
        "numberOfParcels": 1,
        "weightKG": 1.5,
        "numericSenderReference": ref,
        "alphanumericSenderReference": alpha,
    }

    label_params: LabelParameters = {
        "outputType": output_type,
        "offsetX": "0",
        "offsetY": "0",
        "isBorderRequired": "0",
        "isLogoRequired": "0",
        "isBarcodeControlRowRequired": "0",
    }

    create_result = client.create_shipment(
        shipment_payload,
        is_label_required="1",
        label_parameters=label_params,
    )

    if not create_result:
        print("[-] Failed to receive a response from BRT API.")
        return None

    pretty_print("CREATE SHIPMENT RESPONSE", create_result)

    create_resp = create_result.get("createResponse", {})
    exec_msg = create_resp.get("executionMessage", {})
    code = exec_msg.get("code")

    print(f"\n[i] Execution Code: {code}")
    print(f"[i] Execution Message: {exec_msg.get('codeDesc')} - {exec_msg.get('message')}")
    return create_result


# =============================================================================
# ACTION 2: SAVE LABEL
# =============================================================================

def action_save_label(
    client: BrtPZ,
    create_result: CreateResult | dict[str, Any] | None,
    numeric_ref: int | None = None,
    ext: str = "zpl",
) -> Path | None:
    """Action 2: Extract, decode, and save the label from a create_shipment result."""
    print("\n" + "=" * 60)
    print(f"ACTION 2: SAVE LABEL ({ext.upper()})")
    print("=" * 60)

    if not create_result:
        print("[-] No create_result provided.")
        return None

    create_resp = create_result.get("createResponse", {})
    labels_container = create_resp.get("labels", {})
    label_list = labels_container.get("label", [])

    if not label_list:
        print("[!] No labels returned in create_result.")
        return None

    first_label = label_list[0]
    filename = f"label_{numeric_ref}.{ext.lower()}" if numeric_ref else f"label.{ext.lower()}"
    out_path = Path("labels") / filename
    saved = client.save_label(first_label, out_path)
    print(f"[+] Label saved successfully to: {saved.resolve()}")

    if ext.lower() == "zpl":
        try:
            zpl_text = client.get_label_text(first_label)
            print("\n[i] ZPL Content Preview (first 10 lines):")
            for line in zpl_text.strip().splitlines()[:10]:
                print(f"    {line}")
        except Exception as e:
            print(f"[!] Could not decode ZPL text preview: {e}")

    return saved


# =============================================================================
# ACTION 3: DELETE SHIPMENT
# =============================================================================

def action_delete_shipment(
    client: BrtPZ,
    numeric_ref: int,
    alphanumeric_ref: str = "",
) -> DeleteResult | None:
    """Action 3: Send delete_shipment request to BRT."""
    print("\n" + "=" * 60)
    print("ACTION 3: DELETE SHIPMENT")
    print("=" * 60)
    print(f"[*] Sending delete_shipment for numericSenderReference={numeric_ref}...")

    del_result = client.delete_shipment(
        numeric_sender_reference=numeric_ref,
        alphanumeric_sender_reference=alphanumeric_ref,
    )

    if del_result:
        pretty_print("DELETE SHIPMENT RESPONSE", del_result)
        exec_msg = del_result.get("deleteResponse", {}).get("executionMessage", {})
        print(f"\n[i] Delete Execution Code: {exec_msg.get('code')}")
        print(f"[i] Delete Execution Message: {exec_msg.get('codeDesc')} - {exec_msg.get('message')}")
    else:
        print("[-] Delete request failed.")

    return del_result


# =============================================================================
# ACTION 4: TRACK PARCEL
# =============================================================================

def action_track_parcel(
    client: BrtPZ,
    parcel_id: str,
) -> ParcelIDResult | None:
    """Action 4: Query tracking information for a parcel ID (GET /tracking/parcelID/{parcelID})."""
    print("\n" + "=" * 60)
    print(f"ACTION 4: TRACK PARCEL ({parcel_id})")
    print("=" * 60)
    print(f"[*] Sending get_tracking_by_parcel_id for parcelID='{parcel_id}'...")

    track_result = client.get_tracking_by_parcel_id(parcel_id)
    if not track_result:
        print("[-] Failed to receive a tracking response from BRT API.")
        return None

    pretty_print("TRACKING RESPONSE", track_result)

    tt_resp = track_result.get("ttParcelIdResponse", {})
    exec_msg = tt_resp.get("executionMessage", {})
    code = exec_msg.get("code")
    print(f"\n[i] Tracking Execution Code: {code}")
    print(f"[i] Tracking Execution Message: {exec_msg.get('codeDesc')} - {exec_msg.get('message')}")

    bolla = tt_resp.get("bolla", {})
    dati_sped = bolla.get("dati_spedizione", {})
    if dati_sped:
        print(f"[+] Shipment ID: {dati_sped.get('spedizione_id')}")
        print(f"[+] Service: {dati_sped.get('servizio')} ({dati_sped.get('tipo_servizio')})")
        print(f"[+] Arrival Depot: {dati_sped.get('filiale_arrivo')} (code {dati_sped.get('cod_filiale_arrivo')})")
        stato_p1 = dati_sped.get("stato_sped_parte1") or dati_sped.get("descrizione_stato_sped_parte1")
        stato_p2 = dati_sped.get("stato_sped_parte2") or dati_sped.get("descrizione_stato_sped_parte2")
        if stato_p1 or stato_p2:
            print(f"[+] Status: {stato_p1} / {stato_p2}")

    events = tt_resp.get("lista_eventi", [])
    if events:
        active_events = [
            e.get("evento", {})
            for e in events
            if isinstance(e, dict) and (e.get("evento", {}).get("id") or e.get("evento", {}).get("descrizione"))
        ]
        if active_events:
            print(f"\n[+] Events ({len(active_events)} active):")
            for ev in active_events:
                print(f"    - {ev.get('data')} {ev.get('ora')} [{ev.get('id')}]: {ev.get('descrizione')} ({ev.get('filiale')})")

    return track_result


def main() -> None:
    client = get_client()
    if not client:
        return

    # Generated or shared parameters
    sample_ref = int(time.time()) % 10000000
    alpha_ref = f"TEST-{sample_ref}"

    # -------------------------------------------------------------
    # Action 1: Create Shipment
    # -------------------------------------------------------------
    create_result = action_create_shipment(
        client=client,
        numeric_ref=sample_ref,
        alphanumeric_ref=alpha_ref,
        output_type="ZPL",
    )

    # -------------------------------------------------------------
    # Action 2: Save Label (shares client, create_result, numeric_ref)
    # -------------------------------------------------------------
    if create_result:
        action_save_label(
            client=client,
            create_result=create_result,
            numeric_ref=sample_ref,
            ext="zpl",
        )

    # -------------------------------------------------------------
    # Action 3: Track Parcel
    # -------------------------------------------------------------
    # Extract parcelID (segnacollo) from create_result:
    parcel_id: str | None = None
    if create_result:
        create_resp = create_result.get("createResponse", {})
        labels = create_resp.get("labels", {}).get("label", [])
        if labels and labels[0].get("trackingByParcelID"):
            parcel_id = str(labels[0]["trackingByParcelID"])

    if parcel_id:
        action_track_parcel(
            client=client,
            parcel_id=parcel_id,
        )

    # -------------------------------------------------------------
    # Action 4: Delete Shipment (shares client, numeric_ref, alphanumeric_ref)
    # -------------------------------------------------------------
    # Note: BRT documentation advises waiting ~5 minutes after creation
    # before requesting cancellation. Uncomment when ready to test:
    # action_delete_shipment(
    #     client=client,
    #     numeric_ref=sample_ref,
    #     alphanumeric_ref=alpha_ref,
    # )


if __name__ == "__main__":
    main()
