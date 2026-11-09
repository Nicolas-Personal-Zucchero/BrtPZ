# BrtPZ

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-0.1.0-green.svg)](pyproject.toml)
[![Type Checked](https://img.shields.io/badge/types-py.typed-informational.svg)](brt_pz/py.typed)
[![BRT REST API](https://img.shields.io/badge/BRT_API-REST_v1-orange.svg)](https://api.brt.it/)

**BrtPZ** is a Python client library designed for clean, robust interaction with the BRT (Bartolini) REST API. Tailored for automated logistics workflows, it provides high-level abstractions for tracking, routing, BRT-fermopoint locations, shipment management, and label printing.

---

## Features

- **Connection Pooling & Performance**: Built on `requests.Session` with automatic HTTP Keep-Alive.
- **Resilient Rate-Limiting & Retries**: Built-in exponential backoff for transient errors (`429`, `500`, `502`, `503`, `504`).
- **Comprehensive BRT Services**:
  - Tracking (by parcel ID, shipment ID, customer reference)
  - Routing & Depot locator
  - BRT-Fermopoint / PUDO locator & details
  - Consignment creation & cancellation
  - Label generation (PDF / ZPL)
- **Strict Typing & Stubs**: PEP 561 compliance (`py.typed`) with `.pyi` stubs for IDE auto-completion.
- **Zero-Dependency Playground**: Interactive manual test runner with `.env` support.

---

## Installation

```bash
git clone https://github.com/personalzucchero/BrtPZ.git
cd BrtPZ
pip install -e .
```

---

## Quick Start

```python
import logging
from brt_pz import BrtPZ

logging.basicConfig(level=logging.INFO)

with BrtPZ(
    user_id="your_user_id",
    security_token="your_token",
    customer_code="1234567",
    departure_depot="050",
    sandbox=True,
) as client:
    # 1. Routing check
    routing = client.get_routing("40121", "IT", city="Bologna")
    print("Routing info:", routing)

    # 2. Tracking check
    tracking = client.get_tracking_by_parcel_id("0123456789")
    print("Tracking:", tracking)
```

---

## Project Architecture

```
BrtPZ/
├── brt_pz/
│   ├── __init__.py         # Package exports (BrtPZ)
│   ├── __init__.pyi        # Stubs for package exports
│   ├── brt.py              # Core client implementation
│   ├── brt.pyi             # Public interface stubs & docstrings
│   └── py.typed            # PEP 561 marker
├── playground.py           # Interactive development and testing script
├── pyproject.toml          # Packaging metadata & build system (setuptools)
├── template.env            # Environment configuration template
└── README.md               # Library documentation
```

---

## Author & License

- **Author**: Nicolas Amadori ([nicolas.amadori02@gmail.com](mailto:nicolas.amadori02@gmail.com))
