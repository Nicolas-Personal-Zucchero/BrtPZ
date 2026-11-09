import logging
from typing import Any, ClassVar

class BrtPZ:
    _PROD_BASE_URL: ClassVar[str]
    _TEST_BASE_URL: ClassVar[str]

    def __init__(
        self,
        user_id: str,
        security_token: str,
        customer_code: str | None = ...,
        departure_depot: str | None = ...,
        sandbox: bool = ...,
        base_url: str | None = ...,
        logger: logging.Logger | None = ...,
    ) -> None:
        """Initialize the BRT API client."""

    def close(self) -> None:
        """Close the underlying requests Session and release connection pool resources."""

    def __enter__(self) -> BrtPZ: ...
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None: ...

    # 1. Tracking
    def get_tracking_by_parcel_id(self, parcel_id: str) -> dict[str, Any] | None:
        """Retrieve tracking details by parcel ID."""

    def get_tracking_by_shipment_id(
        self,
        shipment_id: str,
        departure_depot: str | None = ...,
    ) -> dict[str, Any] | None:
        """Retrieve tracking details by BRT shipment ID."""

    def get_tracking_by_reference(
        self,
        reference: str,
        customer_code: str | None = ...,
        year: int | None = ...,
    ) -> dict[str, Any] | None:
        """Retrieve tracking details by customer reference."""

    # 2. Routing
    def get_routing(
        self,
        zip_code: str,
        country_code: str = ...,
        city: str | None = ...,
    ) -> dict[str, Any] | None:
        """Retrieve delivery routing info and serving depot."""

    # 3. PUDO
    def search_pudo(
        self,
        zip_code: str,
        country_code: str = ...,
        city: str | None = ...,
        address: str | None = ...,
        max_results: int = ...,
    ) -> list[dict[str, Any]] | None:
        """Search nearby BRT-fermopoint / PUDO locations."""

    def get_pudo_details(self, pudo_id: str) -> dict[str, Any] | None:
        """Retrieve detailed information and business hours for a specific BRT-fermopoint."""

    # 4. Shipments
    def create_shipment(self, shipment_data: dict[str, Any]) -> dict[str, Any] | None:
        """Create a new consignment / shipment in BRT."""

    def delete_shipment(
        self,
        shipment_id: str,
        departure_depot: str | None = ...,
    ) -> bool:
        """Cancel an uncollected BRT shipment."""

    def confirm_shipments(
        self,
        shipment_ids: list[str],
        departure_depot: str | None = ...,
    ) -> dict[str, Any] | None:
        """Confirm / close a daily manifest of shipments."""

    # 5. Labels
    def get_label(
        self,
        shipment_id: str,
        label_format: str = ...,
        departure_depot: str | None = ...,
    ) -> bytes | None:
        """Download a shipment label in the requested format (PDF or ZPL)."""
