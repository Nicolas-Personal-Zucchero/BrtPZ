from __future__ import annotations

import base64
import logging
from pathlib import Path
from typing import Any, ClassVar

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from .schemas import (
    Account,
    ActualSender,
    CreateData,
    CreateResult,
    DeleteData,
    DeleteResult,
    Label,
    LabelParameters,
    ReturnShipmentConsignee,
)


class BrtPZ:
    """Python client library for BRT (Bartolini) REST API Shipments (v1)."""

    _PROD_BASE_URL: ClassVar[str] = "https://api.brt.it/rest/v1/shipments"

    def __init__(
        self,
        user_id: str,
        password: str,
        customer_code: int | None = None,
        departure_depot: int | None = None,
        base_url: str | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        """Initialize the BRT API Shipment client.

        :param user_id: BRT API User ID (userID).
        :param password: BRT API Password.
        :param customer_code: Default sender customer code (codice cliente mittente).
        :param departure_depot: Default departure depot (filiale di partenza, 3 digits).
        :param base_url: Explicit base URL override (defaults to 'https://api.brt.it/rest/v1/shipments').
        :param logger: Optional logger instance for recording API warnings and errors.
        """
        if not user_id:
            raise ValueError("'user_id' must be provided.")
        if not isinstance(user_id, str):
            raise TypeError(f"'user_id' must be a str, got {type(user_id).__name__}.")
        if not password:
            raise ValueError("'password' must be provided.")
        if not isinstance(password, str):
            raise TypeError(f"'password' must be a str, got {type(password).__name__}.")

        self._user_id: str = user_id
        self._password: str = password

        if customer_code is not None and not isinstance(customer_code, int):
            raise TypeError(f"'customer_code' must be an int, got {type(customer_code).__name__}.")
        self._customer_code: int | None = customer_code

        if departure_depot is not None and not isinstance(departure_depot, int):
            raise TypeError(f"'departure_depot' must be an int, got {type(departure_depot).__name__}.")
        self._departure_depot: int | None = departure_depot

        if base_url:
            url = base_url.rstrip("/")
            if not url.endswith("/shipments"):
                url = f"{url}/shipments"
            self._base_url = url
        else:
            self._base_url = self._PROD_BASE_URL

        self._logger: logging.Logger = logger if logger is not None else logging.getLogger("brt_pz")
        self._session: requests.Session = requests.Session()
        self._setup_session_retries()
        self._initialize_brt_headers()

    @property
    def user_id(self) -> str:
        """Return configured BRT user ID."""
        return self._user_id

    @property
    def customer_code(self) -> int | None:
        """Return default sender customer code."""
        return self._customer_code

    @property
    def departure_depot(self) -> int | None:
        """Return default departure depot code."""
        return self._departure_depot

    @property
    def base_url(self) -> str:
        """Return the active base URL."""
        return self._base_url

    def _setup_session_retries(self) -> None:
        """Configure automatic retry behavior with exponential backoff for transient HTTP errors."""
        retries = Retry(
            total=3,
            backoff_factor=1.0,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=None,
            raise_on_status=False,
            respect_retry_after_header=True,
        )
        adapter = HTTPAdapter(max_retries=retries)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

    def _initialize_brt_headers(self) -> None:
        """Configure default HTTP headers for BRT REST APIs.

        BRT API authentication is performed in the request body ('account' field);
        standard UTF-8 JSON headers are used at the transport layer.
        """
        self._headers: dict[str, str] = {
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
        }
        self._session.headers.update(self._headers)

    def close(self) -> None:
        """Close the underlying requests.Session and release connection pool resources."""
        self._session.close()

    def __enter__(self) -> BrtPZ:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def _build_account(self) -> Account:
        """Build the standard account authentication dictionary for request payloads."""
        return {
            "userID": self._user_id,
            "password": self._password,
        }

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
        expected_status: int | tuple[int, ...] = (200, 201),
        error_context: str = "an operation on BRT API",
    ) -> requests.Response | None:
        """Internal helper to execute HTTP requests with standardized headers and error logging."""
        url = endpoint if endpoint.startswith("http") else f"{self._PROD_BASE_URL}/{endpoint.lstrip('/')}"
        valid_statuses = (expected_status,) if isinstance(expected_status, int) else expected_status

        try:
            r = self._session.request(
                method=method.upper(),
                url=url,
                headers=self._headers,
                params=params,
                json=json,
            )
        except requests.RequestException as e:
            self._logger.error(f"Network error during {error_context}: {e}")
            return None

        if r.status_code not in valid_statuses:
            self._logger.error(
                f"HTTP {r.status_code} during {error_context}.\nResponse Body: {r.text}"
            )
            return None

        return r

    def _log_execution_message(self, response_data: dict[str, Any], operation_name: str) -> None:
        """Inspect and log executionMessage diagnostics from a BRT response."""
        exec_message = response_data.get("executionMessage", {})
        code = exec_message.get("code")
        severity = exec_message.get("severity", "INFO")
        code_desc = exec_message.get("codeDesc", "")
        message = exec_message.get("message", "")

        if code is not None:
            if code < 0:
                self._logger.error(
                    f"BRT {operation_name} failed [Code {code} / {severity}]: {code_desc} - {message}"
                )
            elif code > 0:
                self._logger.warning(
                    f"BRT {operation_name} succeeded with warning [Code {code} / {severity}]: {code_desc} - {message}"
                )
            else:
                self._logger.info(f"BRT {operation_name} succeeded: {code_desc}")

    # =========================================================================
    # 1. SHIPMENT CREATION (POST /shipment)
    # =========================================================================

    def create_shipment(
        self,
        shipment_data: CreateData,
        *,
        is_label_required: str = "0",
        label_parameters: LabelParameters | None = None,
        actual_sender: ActualSender | None = None,
        return_shipment_consignee: ReturnShipmentConsignee | None = None,
    ) -> CreateResult | None:
        """Create a new consignment / shipment in BRT (POST /rest/v1/shipments/shipment).

        Performs:
        1. Routing calculation
        2. Optional parcel label printing (PDF/ZPL Base64)
        3. Shipment creation in the BRT system (Disk B)

        :param shipment_data: Shipment data dictionary (fields of `createData`).
        :param is_label_required: Whether to request parcel labels ('1' or '0').
        :param label_parameters: Parameters for label generation (format, offset, borders).
        :param actual_sender: Real sender details (used for Shop to Shop B13 / Shop to Home B14).
        :param return_shipment_consignee: Return consignee details (used for B13 / B14).
        :return: Parsed `createResult` dictionary containing `createResponse`, or None on network/HTTP error.
        """
        payload: dict[str, Any] = {}

        if "createData" in shipment_data:
            payload = dict(shipment_data)
            create_data: dict[str, Any] = dict(payload.get("createData", {}))
        else:
            create_data = dict(shipment_data)

        # Inject default senderCustomerCode if not provided
        if self._customer_code is not None and "senderCustomerCode" not in create_data:
            create_data["senderCustomerCode"] = self._customer_code

        # Inject default departureDepot if not provided
        if self._departure_depot is not None and "departureDepot" not in create_data:
            create_data["departureDepot"] = self._departure_depot

        # Inject authentication account
        if "account" not in payload:
            payload["account"] = self._build_account()

        payload["createData"] = create_data

        # Determine label requirements ('1' or '0')
        req_label = "1" if (str(is_label_required).lower() in ("1", "true") or label_parameters is not None) else "0"
        if "isLabelRequired" not in payload:
            payload["isLabelRequired"] = req_label

        if label_parameters is not None and "labelParameters" not in payload:
            payload["labelParameters"] = label_parameters
        elif payload.get("isLabelRequired") == "1" and "labelParameters" not in payload:
            payload["labelParameters"] = {
                "outputType": "PDF",
                "offsetX": "0",
                "offsetY": "0",
                "isBorderRequired": "0",
                "isLogoRequired": "0",
                "isBarcodeControlRowRequired": "0",
            }

        if actual_sender is not None and "actualSender" not in payload:
            payload["actualSender"] = actual_sender

        if return_shipment_consignee is not None and "returnShipmentConsignee" not in payload:
            payload["returnShipmentConsignee"] = return_shipment_consignee

        endpoint = "/shipment"
        response = self._request(
            method="POST",
            endpoint=endpoint,
            json=payload,
            expected_status=(200, 201),
            error_context="shipment creation",
        )

        if response is None:
            return None

        try:
            result: dict[str, Any] = response.json()
        except ValueError as e:
            self._logger.error(f"Failed to parse JSON response during shipment creation: {e}")
            return None

        self._log_execution_message(result.get("createResponse", {}), "shipment creation")
        return result

    # =========================================================================
    # 2. SHIPMENT DELETION (PUT /delete)
    # =========================================================================

    def delete_shipment(
        self,
        numeric_sender_reference: int,
        alphanumeric_sender_reference: str = "",
        *,
        sender_customer_code: int | None = None,
    ) -> DeleteResult | None:
        """Cancel an uncollected BRT shipment (PUT /rest/v1/shipments/delete).

        Note: As specified by BRT, this service must be invoked at least 5 minutes
        after receiving the positive response from `create_shipment`.
        A shipment can be deleted as long as it has not yet been taken in charge by
        the BRT departure depot.

        :param numeric_sender_reference: Numeric sender reference (riferimento numerico mittente).
        :param alphanumeric_sender_reference: Alphanumeric sender reference (riferimento alfanumerico
            mittente, case-sensitive).
        :param sender_customer_code: Sender customer code (defaults to client's configured `customer_code`).
        :return: Parsed `deleteResult` dictionary containing `deleteResponse`, or None on network/HTTP error.
        """
        cust_code = sender_customer_code if sender_customer_code is not None else self._customer_code
        if cust_code is None:
            raise ValueError(
                "senderCustomerCode is mandatory for shipment deletion. "
                "Set it on client initialization or pass 'sender_customer_code'."
            )
        if not isinstance(cust_code, int):
            raise TypeError(f"'senderCustomerCode' must be an int, got {type(cust_code).__name__}.")

        if numeric_sender_reference is None:
            raise ValueError("numericSenderReference is mandatory for shipment deletion.")
        if not isinstance(numeric_sender_reference, int):
            raise TypeError(
                f"'numericSenderReference' must be an int, got {type(numeric_sender_reference).__name__}."
            )
        if not isinstance(alphanumeric_sender_reference, str):
            raise TypeError(
                f"'alphanumericSenderReference' must be a str, got {type(alphanumeric_sender_reference).__name__}."
            )

        payload: dict[str, Any] = {
            "account": self._build_account(),
            "deleteData": {
                "senderCustomerCode": cust_code,
                "numericSenderReference": numeric_sender_reference,
                "alphanumericSenderReference": alphanumeric_sender_reference,
            },
        }

        endpoint = "/delete"
        response = self._request(
            method="PUT",
            endpoint=endpoint,
            json=payload,
            expected_status=(200, 201),
            error_context="shipment deletion",
        )

        if response is None:
            return None

        try:
            result: dict[str, Any] = response.json()
        except ValueError as e:
            self._logger.error(f"Failed to parse JSON response during shipment deletion: {e}")
            return None

        self._log_execution_message(result.get("deleteResponse", {}), "shipment deletion")
        return result

    # =========================================================================
    # 3. LABEL UTILITIES
    # =========================================================================

    @staticmethod
    def get_label_bytes(label: Label | str, *, digital: bool = False) -> bytes:
        """Decode a Base64-encoded label stream into raw bytes.

        :param label: `Label` dictionary from `createResult`, or a raw Base64 string.
        :param digital: If True, decodes the `streamDigitalLabel` (PNG 2D code) instead of `stream`.
        :return: Decoded binary data (e.g. PDF bytes, ZPL string bytes, or PNG bytes).
        """
        if isinstance(label, dict):
            key = "streamDigitalLabel" if digital else "stream"
            stream_str = str(label.get(key, ""))
        else:
            stream_str = str(label)

        return base64.b64decode(stream_str)

    @classmethod
    def save_label(
        cls,
        label: Label | str,
        output_path: str | Path,
        *,
        digital: bool = False,
    ) -> Path:
        """Decode and save a parcel label to a local file.

        :param label: `Label` dictionary from `createResult`, or a raw Base64 string.
        :param output_path: Destination file path (e.g. 'label.pdf' or 'label.png').
        :param digital: If True, saves `streamDigitalLabel` (PNG QR code).
        :return: Path object of the saved file.
        """
        data = cls.get_label_bytes(label, digital=digital)
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path
