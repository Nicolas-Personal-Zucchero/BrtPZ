# BrtPZ

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-0.1.0-green.svg)](pyproject.toml)
[![Type Checked](https://img.shields.io/badge/types-py.typed-informational.svg)](brt_pz/py.typed)
[![BRT REST API](https://img.shields.io/badge/BRT_API-REST_v1_Shipments-orange.svg)](https://api.brt.it/)

**BrtPZ** is a Python client library for the official **BRT (Bartolini) REST API Shipment service (v1)**. Designed according to the technical specifications of BRT SpA, it provides typed schemas and robust HTTP operations for shipment creation and cancellation.

---

## Features

- **Official BRT Shipment API Integration**:
  - `create_shipment`: Disk B shipment generation (`POST /rest/v1/shipments/shipment`), routing calculation, and optional parcel label printing (PDF/ZPL Base64).
  - `delete_shipment`: Shipment cancellation (`PUT /rest/v1/shipments/delete`) before management by the BRT departure depot.
  - `get_label_bytes` & `save_label`: Label decoding and file export utilities for PDF, ZPL, and 2D digital QR codes.
- **Dedicated JSON Schemas & Typings**: Full PEP 589 `TypedDict` definitions in [`brt_pz/schemas.py`](brt_pz/schemas.py) matching BRT Disk B specifications (`CreateData`, `LabelParameters`, `ActualSender`, `ReturnShipmentConsignee`, `Parcel`, `AdrData`, `DeleteData`, `CreateResult`, `DeleteResult`, `ExecutionMessage`, etc.).
- **Automatic Account Injection**: Injects the BRT API `account` object (`userID`, `password`) into request bodies automatically.
- **Default Depot & Customer Code Inheritance**: Configurable default `departureDepot` and `senderCustomerCode` auto-injected if omitted.
- **Connection Pooling & Resiliency**: Built on `requests.Session` with HTTP Keep-Alive and exponential backoff retries on transient errors (`429`, `500`, `502`, `503`, `504`).
- **Strict Typing & IDE Autocomplete**: PEP 561 compliance (`py.typed`) and `.pyi` stubs.

---

## Installation

```bash
git clone https://github.com/Nicolas-Personal-Zucchero/BrtPZ.git
cd BrtPZ
pip install -e .
```

---

## Quick Start

### 1. Initialize Client

```python
from brt_pz import BrtPZ, CreateData

client = BrtPZ(
    user_id="your_user_id",
    password="your_password",
    customer_code=1020100,      # Default senderCustomerCode
    departure_depot=102,        # Default departureDepot
)
```

### 2. Create a Shipment

```python
shipment_data: CreateData = {
    "deliveryFreightTypeCode": "DAP",
    "consigneeCompanyName": "Mario Rossi",
    "consigneeAddress": "Via dell'Indipendenza 1",
    "consigneeZIPCode": "40121",
    "consigneeCity": "Bologna",
    "consigneeProvinceAbbreviation": "BO",
    "consigneeCountryAbbreviationISOAlpha2": "IT",
    "consigneeContactName": "Mario Rossi",
    "consigneeTelephone": "051123456",
    "consigneeEMail": "mario.rossi@example.com",
    "numberOfParcels": 1,
    "weightKG": 2.5,
    "numericSenderReference": 99001,
    "alphanumericSenderReference": "ORDER-2026-01",
}

# Create shipment and generate a PDF label
result = client.create_shipment(
    shipment_data,
    is_label_required="1",
    label_parameters={"outputType": "PDF"},
)

if result:
    exec_msg = result["createResponse"]["executionMessage"]
    print(f"Status Code: {exec_msg['code']} ({exec_msg['codeDesc']})")
```

### 3. Delete a Shipment

> [!NOTE]
> According to BRT documentation, cancellation must be requested at least 5 minutes after receiving the positive response from `create_shipment`, and before the shipment is processed by the BRT depot.

```python
delete_result = client.delete_shipment(
    numeric_sender_reference=99001,
    alphanumeric_sender_reference="ORDER-2026-01",
)

if delete_result:
    exec_msg = delete_result["deleteResponse"]["executionMessage"]
    print(f"Delete Code: {exec_msg['code']} ({exec_msg['codeDesc']})")
```

---

## Project Structure

```
BrtPZ/
├── brt_pz/
│   ├── __init__.py         # Package exports (BrtPZ and schema types)
│   ├── __init__.pyi        # Stub definitions for package exports
│   ├── brt.py              # BrtPZ client implementation (Create & Delete)
│   ├── brt.pyi             # Interface typing stubs & docstrings
│   ├── schemas.py          # Dedicated BRT REST API JSON schemas and TypedDicts
│   └── py.typed            # PEP 561 typing marker
├── tests/
│   └── test_brt.py         # Comprehensive unit tests
├── playground.py           # Interactive test runner with .env support
├── pyproject.toml          # Packaging metadata & setuptools config
├── template.env            # Environment configuration template
└── README.md               # Library documentation
```

---

## Author & License

- **Author**: Nicolas Amadori ([nicolas.amadori02@gmail.com](mailto:nicolas.amadori02@gmail.com))
