import logging
from pathlib import Path
from typing import Any, ClassVar, Self

from .schemas import (
    ActualSender,
    CreateData,
    CreateResult,
    DeleteResult,
    Label,
    LabelParameters,
    ReturnShipmentConsignee,
)

class BrtPZ:
    _BASE_URL: ClassVar[str]

    def __init__(
        self,
        user_id: str,
        password: str,
        customer_code: int | None = ...,
        departure_depot: int | None = ...,
        logger: logging.Logger | None = ...,
    ) -> None:
        """Initialize the BRT API Shipment client."""

    @property
    def user_id(self) -> str: ...
    @property
    def customer_code(self) -> int | None: ...
    @property
    def departure_depot(self) -> int | None: ...
    @property
    def base_url(self) -> str: ...

    def close(self) -> None:
        """Close the underlying requests Session and release connection pool resources."""

    def __enter__(self) -> Self: ...
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None: ...

    def create_shipment(
        self,
        shipment_data: CreateData,
        *,
        is_label_required: str = ...,
        label_parameters: LabelParameters | None = ...,
        actual_sender: ActualSender | None = ...,
        return_shipment_consignee: ReturnShipmentConsignee | None = ...,
    ) -> CreateResult | None:
        """Create a new consignment / shipment in BRT."""

    def delete_shipment(
        self,
        numeric_sender_reference: int,
        alphanumeric_sender_reference: str = ...,
        *,
        sender_customer_code: int | None = ...,
    ) -> DeleteResult | None:
        """Cancel an uncollected BRT shipment."""

    @staticmethod
    def get_label_bytes(label: Label | str, *, digital: bool = ...) -> bytes:
        """Decode Base64 label stream to raw bytes."""

    @classmethod
    def save_label(
        cls,
        label: Label | str,
        output_path: str | Path,
        *,
        digital: bool = ...,
    ) -> Path:
        """Decode and save a parcel label to a local file."""
