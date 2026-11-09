from __future__ import annotations

import logging
from typing import Any, ClassVar

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


class BrtPZ:
    """Python client library for BRT (Bartolini) REST APIs."""

    _PROD_BASE_URL: ClassVar[str] = "https://api.brt.it/rest/v1"
    _TEST_BASE_URL: ClassVar[str] = "https://api-test.brt.it/rest/v1"

    def __init__(
        self,
        user_id: str,
        security_token: str,
        customer_code: str | None = None,
        departure_depot: str | None = None,
        sandbox: bool = False,
        base_url: str | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        """Initialize the BRT API client.

        :param user_id: BRT API User ID.
        :param security_token: BRT Security Token or API Key.
        :param customer_code: Default BRT customer code (codice cliente).
        :param departure_depot: Default departure depot (filiale di partenza).
        :param sandbox: If True, uses the BRT test environment endpoint.
        :param base_url: Explicit base URL override (optional).
        :param logger: Optional logger instance for recording API warnings and errors.
        """
        self._user_id = user_id
        self._security_token = security_token
        self._customer_code = customer_code
        self._departure_depot = departure_depot
        self._sandbox = sandbox

        if base_url:
            self._base_url = base_url.rstrip("/")
        else:
            self._base_url = self._TEST_BASE_URL if sandbox else self._PROD_BASE_URL

        self._session: requests.Session = requests.Session()
        self._setup_session_retries()
        self._initialize_brt_headers()
        self._logger: logging.Logger = logger if logger is not None else logging.getLogger("brt_pz")

    def _setup_session_retries(self) -> None:
        """Configure automatic retry behavior with exponential backoff for rate limits and transient errors."""
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
        """Configure authentication and default headers for BRT REST APIs."""
        self._headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "userID": self._user_id,
            "securityToken": self._security_token,
        }
        self._session.headers.update(self._headers)

    def close(self) -> None:
        """Close the underlying requests.Session and release connection pool resources."""
        self._session.close()

    def __enter__(self) -> BrtPZ:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
        expected_status: int | tuple[int, ...] = 200,
        error_context: str = "an operation on BRT API",
    ) -> requests.Response | None:
        """Internal helper to execute HTTP requests with standardized headers and error reporting."""
        url = endpoint if endpoint.startswith("http") else f"{self._base_url}/{endpoint.lstrip('/')}"
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
            self._logger.error(f"Error {r.status_code} during {error_context}.\nResponse Body: {r.text}")
            return None

        return r

    # =========================================================================
    # 1. TRACKING
    # =========================================================================

    def get_tracking_by_parcel_id(self, parcel_id: str) -> dict[str, Any] | None:
        """Retrieve tracking details by BRT parcel ID / package code (collo/segnacollo)."""
        endpoint = f"/tracking/parcelId/{parcel_id}"
        r = self._request("GET", endpoint, error_context="tracking retrieval by parcel ID")
        return r.json() if r is not None else None

    def get_tracking_by_shipment_id(
        self,
        shipment_id: str,
        departure_depot: str | None = None,
    ) -> dict[str, Any] | None:
        """Retrieve tracking details by BRT shipment ID (numero spedizione)."""
        depot = departure_depot or self._departure_depot
        params: dict[str, Any] = {}
        if depot:
            params["departureDepot"] = depot

        endpoint = f"/tracking/shipmentId/{shipment_id}"
        r = self._request("GET", endpoint, params=params, error_context="tracking retrieval by shipment ID")
        return r.json() if r is not None else None

    def get_tracking_by_reference(
        self,
        reference: str,
        customer_code: str | None = None,
        year: int | None = None,
    ) -> dict[str, Any] | None:
        """Retrieve tracking details by customer reference (riferimento cliente)."""
        customer = customer_code or self._customer_code
        params: dict[str, Any] = {"customerReference": reference}
        if customer:
            params["customerCode"] = customer
        if year:
            params["year"] = year

        endpoint = "/tracking/reference"
        r = self._request("GET", endpoint, params=params, error_context="tracking retrieval by customer reference")
        return r.json() if r is not None else None

    # =========================================================================
    # 2. ROUTING & DEPOT FINDER
    # =========================================================================

    def get_routing(
        self,
        zip_code: str,
        country_code: str = "IT",
        city: str | None = None,
    ) -> dict[str, Any] | None:
        """Retrieve delivery routing info and serving depot for a destination postal code."""
        params: dict[str, Any] = {
            "zipCode": zip_code,
            "countryCode": country_code,
        }
        if city:
            params["city"] = city

        endpoint = "/routing"
        r = self._request("GET", endpoint, params=params, error_context="routing inquiry")
        return r.json() if r is not None else None

    # =========================================================================
    # 3. BRT-FERMOPOINT / PUDO (PICK-UP & DROP-OFF POINTS)
    # =========================================================================

    def search_pudo(
        self,
        zip_code: str,
        country_code: str = "IT",
        city: str | None = None,
        address: str | None = None,
        max_results: int = 10,
    ) -> list[dict[str, Any]] | None:
        """Search nearby BRT-fermopoint / PUDO pickup locations."""
        payload: dict[str, Any] = {
            "zipCode": zip_code,
            "countryCode": country_code,
            "maxResults": max_results,
        }
        if city:
            payload["city"] = city
        if address:
            payload["address"] = address

        endpoint = "/pudo/search"
        r = self._request(
            "POST",
            endpoint,
            json=payload,
            expected_status=(200, 201),
            error_context="PUDO search",
        )
        return r.json() if r is not None else None

    def get_pudo_details(self, pudo_id: str) -> dict[str, Any] | None:
        """Retrieve detailed information and business hours for a specific BRT-fermopoint."""
        endpoint = f"/pudo/{pudo_id}"
        r = self._request("GET", endpoint, error_context="PUDO details retrieval")
        return r.json() if r is not None else None

    # =========================================================================
    # 4. SHIPMENTS / CONSIGNMENTS
    # =========================================================================

    def create_shipment(self, shipment_data: dict[str, Any]) -> dict[str, Any] | None:
        """Create a new consignment / shipment in BRT.

        :param shipment_data: Complete shipment payload according to BRT specification.
        :return: Created shipment response including barcode, shipment ID, and label data.
        """
        # Inject defaults if missing
        if self._customer_code and "customerCode" not in shipment_data:
            shipment_data["customerCode"] = self._customer_code
        if self._departure_depot and "departureDepot" not in shipment_data:
            shipment_data["departureDepot"] = self._departure_depot

        endpoint = "/shipments/shipment"
        r = self._request(
            "POST",
            endpoint,
            json=shipment_data,
            expected_status=(200, 201),
            error_context="shipment creation",
        )
        return r.json() if r is not None else None

    def delete_shipment(
        self,
        shipment_id: str,
        departure_depot: str | None = None,
    ) -> bool:
        """Cancel an uncollected BRT shipment.

        :param shipment_id: BRT shipment number.
        :param departure_depot: Departure depot code.
        :return: True if successfully deleted, False otherwise.
        """
        depot = departure_depot or self._departure_depot
        params: dict[str, Any] = {}
        if depot:
            params["departureDepot"] = depot

        endpoint = f"/shipments/shipment/{shipment_id}"
        r = self._request(
            "DELETE",
            endpoint,
            params=params,
            expected_status=(200, 204),
            error_context="shipment deletion",
        )
        return r is not None

    def confirm_shipments(
        self,
        shipment_ids: list[str],
        departure_depot: str | None = None,
    ) -> dict[str, Any] | None:
        """Confirm / close a daily manifest of shipments (chiusura giornaliera borderò)."""
        depot = departure_depot or self._departure_depot
        payload: dict[str, Any] = {
            "shipmentIds": shipment_ids,
        }
        if depot:
            payload["departureDepot"] = depot

        endpoint = "/shipments/confirm"
        r = self._request(
            "POST",
            endpoint,
            json=payload,
            expected_status=(200, 201),
            error_context="shipment confirmation",
        )
        return r.json() if r is not None else None

    # =========================================================================
    # 5. LABELS
    # =========================================================================

    def get_label(
        self,
        shipment_id: str,
        label_format: str = "PDF",
        departure_depot: str | None = None,
    ) -> bytes | None:
        """Download a shipment label in the requested format (PDF or ZPL).

        :param shipment_id: BRT shipment number or parcel ID.
        :param label_format: Format string ('PDF', 'ZPL', 'EPL').
        :param departure_depot: Departure depot code.
        :return: Raw binary content of the label file, or None on error.
        """
        depot = departure_depot or self._departure_depot
        params: dict[str, Any] = {"format": label_format.upper()}
        if depot:
            params["departureDepot"] = depot

        endpoint = f"/labels/shipment/{shipment_id}"
        r = self._request("GET", endpoint, params=params, error_context="label retrieval")
        return r.content if r is not None else None
