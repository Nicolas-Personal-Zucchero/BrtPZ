"""BRT REST API shipment JSON schemas and typing definitions.

Based on official BRT Rest API Shipment documentation (v1).
"""

from __future__ import annotations

from typing import TypedDict

# =============================================================================
# AUTHENTICATION
# =============================================================================

class Account(TypedDict):
    """Account information for BRT REST API authentication."""

    userID: str
    """User code provided by BRT for web service authentication."""

    password: str
    """User password."""


# =============================================================================
# MERCE PERICOLOSA (ADR) & PARCELS
# =============================================================================

class AdrData(TypedDict, total=False):
    """ADR dangerous goods details according to UN regulations."""

    UN_No: int
    """4-digit UN identification number assigned by UN Committee (min: 1, max: 9999). Mandatory for ADR."""

    packingGroup: str
    """Packing group: 'I' (high danger), 'II' (medium danger), 'III' (low danger). Mandatory for ADR."""

    classCode: str
    """ADR classification code (max length: 5). Mandatory for ADR."""

    netWeightGrams: int
    """Dangerous goods net weight in grams (min: 1, max: 30000). Mandatory for ADR."""


class Parcel(TypedDict, total=False):
    """Single package details with optional ADR dangerous goods data."""

    grossWeightGrams: int
    """Gross parcel weight in grams (min: 1, max: 30000). Mandatory if parcel entry provided."""

    adrDetails: list[AdrData]
    """ADR dangerous goods details list."""


# =============================================================================
# MITTENTE REALE & DESTINATARIO RESO (SHOP TO SHOP / SHOP TO HOME)
# =============================================================================

class ActualSender(TypedDict, total=False):
    """Actual sender data (used when brtServiceCode is B13 or B14)."""

    actualSenderName: str
    """Actual sender name (max length: 70). Mandatory if actualSender is used."""

    actualSenderCity: str
    """Actual sender city / municipality (max length: 35)."""

    actualSenderAddress: str
    """Actual sender address (max length: 35)."""

    actualSenderZIPCode: str
    """Actual sender postal ZIP code (max length: 9)."""

    actualSenderProvince: str
    """Actual sender province abbreviation (max length: 2)."""

    actualSenderCountry: str
    """Actual sender country abbreviation ISO 3166-1 alpha-2 (max length: 3)."""

    actualSenderEmail: str
    """Actual sender email address (max length: 70). One of email or mobile phone is mandatory."""

    actualSenderMobilePhoneNumber: str
    """Actual sender mobile phone number (max length: 16). One of email or mobile phone is mandatory."""

    actualSenderPudoId: str
    """Actual sender BRT-fermopoint PUDO ID (max length: 20)."""


class ReturnShipmentConsignee(TypedDict, total=False):
    """Return shipment consignee data (used when brtServiceCode is B13 or B14)."""

    returnShipmentConsigneeName: str
    """Return consignee name (max length: 70). Mandatory if returnShipmentConsignee is used."""

    returnShipmentConsigneeCity: str
    """Return consignee city / municipality (max length: 35). Mandatory."""

    returnShipmentConsigneeAddress: str
    """Return consignee address (max length: 35). Mandatory."""

    returnShipmentConsigneeZIPCode: str
    """Return consignee postal ZIP code (max length: 9). Mandatory."""

    returnShipmentConsigneeProvince: str
    """Return consignee province abbreviation (max length: 2)."""

    returnShipmentConsigneeCountry: str
    """Return consignee country ISO 3166-1 alpha-2 code (max length: 3). Mandatory."""

    returnShipmentConsigneeEmail: str
    """Return consignee email address (max length: 70). One of email or mobile phone is mandatory."""

    returnShipmentConsigneeMobilePhoneNumber: str
    """Return consignee mobile phone number (max length: 16). One of email or mobile phone is mandatory."""

    returnShipmentConsigneePudoId: str
    """Return consignee BRT-fermopoint PUDO ID (max length: 20)."""


# =============================================================================
# LABEL PARAMETERS
# =============================================================================

class LabelParameters(TypedDict, total=False):
    """Parameters for building package labels."""

    outputType: str
    """Output format: 'PDF' (Base64 PDF stream) or 'ZPL' (Zebra Programming Language stream)."""

    offsetX: str
    """Horizontal offset from top-left (forced to '0' if omitted or non-numeric)."""

    offsetY: str
    """Vertical offset from top-left (forced to '0' if omitted or non-numeric)."""

    isBorderRequired: str
    """'1' to render label border, '0' otherwise."""

    isLogoRequired: str
    """'1' to render BRT logo on label, '0' otherwise."""

    isBarcodeControlRowRequired: str
    """'1' to render barcode control row, '0' otherwise."""

    labelFormat: str
    """Label format override: '' (default BRT 95x65mm), 'DP5' (DPD 100x150mm ZPL), 'DPH' (Hybrid 100x150mm ZPL)."""


# =============================================================================
# CREATE SHIPMENT (CREATE DATA & REQUEST)
# =============================================================================

class _CreateDataBase(TypedDict):
    """Required fields for BRT shipment creation."""

    departureDepot: int
    """Departure depot code (filiale di partenza, 3 digits). Mandatory."""

    senderCustomerCode: int
    """Sender customer code (codice cliente mittente, up to 7 digits). Mandatory."""

    deliveryFreightTypeCode: str
    """Freight payment type: 'DAP' (porto franco) or 'EXW' (porto assegnato). Mandatory."""

    numberOfParcels: int
    """Number of parcels (numero colli, max 30). Mandatory."""

    weightKG: float
    """Total shipment gross weight in kilograms (precision: 5.1). Mandatory."""

    numericSenderReference: int
    """Sender numeric reference (riferimento numerico mittente, up to 15 digits). Mandatory."""


class CreateData(_CreateDataBase, total=False):
    """Full shipment creation data schema (createData).

    Note: consigneeCompanyName, consigneeAddress, consigneeZIPCode, consigneeCity,
    and consigneeCountryAbbreviationISOAlpha2 are mandatory unless brtServiceCode is 'B15'.
    """

    network: str
    """Network code (max length: 1). Empty string uses default standard BRT network."""

    consigneeCompanyName: str
    """Consignee company or person name (max length: 70). Mandatory unless brtServiceCode == 'B15'."""

    consigneeAddress: str
    """Consignee street address (min 6, max 35 chars domestic IT / 105 chars international extended)."""

    consigneeZIPCode: str
    """Destination postal code (CAP, max length: 9). Mandatory unless brtServiceCode == 'B15'."""

    consigneeCity: str
    """Destination city / municipality (località, max length: 35). Mandatory unless brtServiceCode == 'B15'."""

    consigneeProvinceAbbreviation: str
    """Destination province 2-letter abbreviation (sigla provincia, e.g. 'BO', 'MI')."""

    consigneeCountryAbbreviationISOAlpha2: str
    """Destination country ISO 3166-1 alpha-2 code (e.g. 'IT', 'FR', 'DE'). Mandatory unless brtServiceCode == 'B15'."""

    consigneeClosingShift1_DayOfTheWeek: str
    """Closing shift 1 day: 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'."""

    consigneeClosingShift1_PeriodOfTheDay: str
    """Closing shift 1 period: 'AM' (morning) or 'PM' (afternoon)."""

    consigneeClosingShift2_DayOfTheWeek: str
    """Closing shift 2 day: 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'."""

    consigneeClosingShift2_PeriodOfTheDay: str
    """Closing shift 2 period: 'AM' (morning) or 'PM' (afternoon)."""

    consigneeContactName: str
    """Consignee contact person name (referente consegna, max length: 35)."""

    consigneeTelephone: str
    """Consignee landline telephone (max length: 16)."""

    consigneeEMail: str
    """Consignee email address for notifications (multiple emails separated by '|', max length: 70)."""

    consigneeMobilePhoneNumber: str
    """Consignee mobile phone number for SMS alerts (max length: 16)."""

    isAlertRequired: str
    """'1' to send delivery alert (SMS/email) to consignee, '0' otherwise."""

    consigneeVATNumber: str
    """Consignee VAT number / Partita IVA (max length: 16)."""

    consigneeVATNumberCountryISOAlpha2: str
    """Country ISO alpha-2 for consignee VAT number (max length: 2)."""

    consigneeItalianFiscalCode: str
    """Consignee Italian fiscal code / Codice Fiscale (max length: 16)."""

    pricingConditionCode: str
    """Pricing condition code / codice tariffa (e.g. '000', '002', max length: 3)."""

    serviceType: str
    """Service type: '' (standard), 'E' (priority), 'H' (10:30 delivery)."""

    insuranceAmount: float
    """Insurance value (precision 7.2)."""

    insuranceAmountCurrency: str
    """Currency for insurance (defaults to 'EUR', max length: 3)."""

    senderParcelType: str
    """Goods nature description / natura merce (max length: 15)."""

    volumeM3: float
    """Total shipment volume in cubic meters (precision: 5.3)."""

    quantityToBeInvoiced: float
    """Quantity to invoice / quantità da fatturare (precision: 7.3)."""

    cashOnDelivery: float
    """Cash on delivery / contrassegno amount (precision: 7.2)."""

    isCODMandatory: str
    """'1' if cash on delivery is mandatory, '0' otherwise."""

    codPaymentType: str
    """COD payment method code (max length: 2)."""

    codCurrency: str
    """COD currency (defaults to 'EUR', max length: 3)."""

    alphanumericSenderReference: str
    """Alphanumeric customer reference (max length: 15, case sensitive)."""

    notes: str
    """Delivery notes (max length: 70)."""

    parcelsHandlingCode: str
    """Parcels handling code / codice trattamento merce (max length: 2)."""

    deliveryDateRequired: str
    """Requested delivery date in ISO format 'YYYY-MM-DD' (max length: 10)."""

    deliveryType: str
    """Delivery timing type relative to requested delivery date (max length: 1)."""

    declaredParcelValue: float
    """Declared parcel value (precision 7.2)."""

    declaredParcelValueCurrency: str
    """Declared value currency (defaults to 'EUR', max length: 3)."""

    particularitiesDeliveryManagementCode: str
    """Delivery particularities code (max length: 2)."""

    particularitiesHoldOnStockManagementCode: str
    """Hold on stock particularities code (max length: 2)."""

    variousParticularitiesManagementCode: str
    """Various particularities code (max length: 2)."""

    particularDelivery1: str
    """Special delivery code 1 (max length: 1)."""

    particularDelivery2: str
    """Special delivery code 2 (max length: 1)."""

    palletType1: str
    """Pallet type 1 (e.g. 'EPAL', max length: 4)."""

    palletType1Number: int
    """Quantity of pallet type 1."""

    palletType2: str
    """Pallet type 2 (max length: 4)."""

    palletType2Number: int
    """Quantity of pallet type 2."""

    originalSenderCompanyName: str
    """Original sender company name (max length: 25)."""

    originalSenderZIPCode: str
    """Original sender postal code (max length: 9)."""

    originalSenderCountryAbbreviationISOAlpha2: str
    """Original sender country ISO alpha-2 (max length: 2)."""

    cmrCode: str
    """CMR code (max length: 35)."""

    neighborNameMandatoryAuthorization: str
    """Authorized neighbor name for delivery (max length: 70)."""

    pinCodeMandatoryAuthorization: str
    """Delivery authorization PIN code (max length: 15)."""

    packingListPDFName: str
    """Packing list PDF filename (max length: 33)."""

    packingListPDFFlagPrint: str
    """Packing list print flag (max length: 1)."""

    packingListPDFFlagEmail: str
    """Packing list email flag (max length: 1)."""

    pudoId: str
    """BRT-fermopoint pickup point ID (max length: 20)."""

    brtServiceCode: str
    """Special service code: 'B11' (Direct to Shop), 'B13' (Shop to Shop), 'B14' (Shop to Home), 'B15' (Return from Shop), 'B20' (Fresh 0-4°C)."""

    returnDepot: int
    """Return depot code (deposito di reso, precision: 10.0)."""

    expiryDate: str
    """Expiry date for Fresh service in ISO format 'YYYY-MM-DD' (max length: 10)."""

    holdForPickup: str
    """'1' for fermo deposito (hold for depot pickup), '0' otherwise."""

    genericReference: str
    """Generic reference string (max length: 35)."""

    parcels: list[Parcel]
    """Collection of parcel details with optional ADR specifications."""


class CreateRequest(TypedDict, total=False):
    """Complete payload for the Create Shipment API (POST /shipments/shipment)."""

    account: Account
    """BRT API authentication account."""

    createData: CreateData
    """Shipment data."""

    isLabelRequired: str
    """'1' if parcel label is requested, '0' otherwise."""

    labelParameters: LabelParameters
    """Label generation parameters (mandatory if isLabelRequired == '1')."""

    actualSender: ActualSender
    """Actual sender details for Shop to Shop (B13) / Shop to Home (B14)."""

    returnShipmentConsignee: ReturnShipmentConsignee
    """Return consignee details for Shop to Shop (B13) / Shop to Home (B14)."""


# =============================================================================
# DELETE SHIPMENT (DELETE DATA & REQUEST)
# =============================================================================

class DeleteData(TypedDict, total=False):
    """Target shipment identification for cancellation."""

    senderCustomerCode: int
    """Sender customer code (codice cliente mittente). Mandatory."""

    numericSenderReference: int
    """Sender numeric reference (riferimento numerico mittente). Mandatory."""

    alphanumericSenderReference: str
    """Sender alphanumeric reference (riferimento alfanumerico mittente, case sensitive)."""


class DeleteRequest(TypedDict):
    """Complete payload for Delete Shipment API (PUT /shipments/delete)."""

    account: Account
    """BRT API authentication account."""

    deleteData: DeleteData
    """Shipment identification data."""


# =============================================================================
# CONFIRM SHIPMENT (CONFIRM DATA & REQUEST)
# =============================================================================

class ConfirmData(TypedDict, total=False):
    """Shipment confirmation data for explicit confirmation mode."""

    senderCustomerCode: int
    """Sender customer code (codice cliente mittente). Mandatory."""

    numericSenderReference: int
    """Sender numeric reference (riferimento numerico mittente). Mandatory."""

    alphanumericSenderReference: str
    """Sender alphanumeric reference (riferimento alfanumerico mittente)."""

    cmrCode: str
    """CMR code for bolle aggregation / confirmation."""


class ConfirmRequest(TypedDict):
    """Complete payload for Confirm Shipment API (PUT /shipments/shipment)."""

    account: Account
    """BRT API authentication account."""

    confirmData: ConfirmData
    """Shipment confirmation data."""


# =============================================================================
# ROUTING (ROUTING DATA & REQUEST)
# =============================================================================

class RoutingData(TypedDict, total=False):
    """Destination coordinates calculation data (routingData)."""

    network: str
    """Network code (max length: 1)."""

    departureDepot: int
    """Departure depot code (precision: 3.0). Mandatory."""

    senderCustomerCode: int
    """Sender customer code (precision: 7.0). Mandatory."""

    deliveryFreightTypeCode: str
    """Freight payment type: 'DAP' or 'EXW'. Mandatory."""

    consigneeCompanyName: str
    """Consignee company name (max length: 70). Mandatory."""

    consigneeAddress: str
    """Consignee address (min 6, max 35 domestic / 105 international). Mandatory."""

    consigneeZIPCode: str
    """Destination postal code (CAP, max length: 9). Mandatory."""

    consigneeCity: str
    """Destination city (max length: 35). Mandatory."""

    consigneeProvinceAbbreviation: str
    """Destination province (max length: 2). Mandatory if IT."""

    consigneeCountryAbbreviationISOAlpha2: str
    """Destination country ISO alpha-2 (max length: 2). Mandatory."""

    serviceType: str
    """Service type: '' (standard), 'E' (priority), 'H' (10:30)."""

    numberOfParcels: int
    """Number of parcels."""

    weightKG: float
    """Total weight in KG."""

    volumeM3: float
    """Total volume in M3."""

    variousParticularitiesManagementCode: str
    """Various particularities code."""

    particularDelivery1: str
    """Particular delivery code 1."""

    particularDelivery2: str
    """Particular delivery code 2."""


class RoutingRequest(TypedDict):
    """Complete payload for Routing calculation API (PUT /shipments/routing)."""

    account: Account
    """BRT API authentication account."""

    routingData: RoutingData
    """Routing input data."""


# =============================================================================
# RESPONSES & RESULTS
# =============================================================================

class ExecutionMessage(TypedDict, total=False):
    """Execution status and diagnostics returned by BRT services."""

    code: int
    """Execution status code: 0 = success, >0 = success with warnings, <0 = error."""

    severity: str
    """Message severity: 'INFO', 'WARNING', 'ERROR'."""

    codeDesc: str
    """Short description of the status code."""

    message: str
    """Detailed error / warning message."""


class Label(TypedDict, total=False):
    """Individual parcel label data and barcode."""

    dataLength: int
    """Byte length of the label stream."""

    parcelID: str
    """BRT barcode 18-digit Code 128 (segnacollo BRT)."""

    trackingByParcelID: str
    """15-character parcel tracking ID."""

    parcelNumberGeoPost: str
    """GeoPost parcel number."""

    stream: str
    """Base64-encoded PDF or ZPL label stream."""

    streamDigitalLabel: str
    """Base64-encoded PNG image of the 2D digital QR / barcode."""


class Labels(TypedDict, total=False):
    """Collection of parcel labels."""

    label: list[Label]
    """List of generated parcel labels."""


class CreateResponse(TypedDict, total=False):
    """Body of successful shipment creation response."""

    currentTimeUTC: str
    """Response timestamp in UTC with timezone offset."""

    executionMessage: ExecutionMessage
    """Execution outcome diagnostics."""

    arrivalTerminal: str
    """BRT arrival routing terminal."""

    arrivalDepot: str
    """BRT arrival depot code."""

    deliveryZone: str
    """BRT delivery zone code."""

    parcelNumberFrom: str
    """Starting parcel ID in the assigned range."""

    parcelNumberTo: str
    """Ending parcel ID in the assigned range."""

    departureDepot: int
    """Departure depot code."""

    seriesNumber: int
    """Assigned client series number."""

    serviceType: str
    """Effective service type."""

    consigneeCompanyName: str
    """Normalized consignee company name."""

    consigneeAddress: str
    """Normalized consignee address."""

    consigneeZIPCode: str
    """Normalized consignee ZIP code."""

    consigneeCity: str
    """Normalized consignee city."""

    consigneeProvinceAbbreviation: str
    """Normalized consignee province."""

    consigneeCountryAbbreviationBRT: str
    """BRT consignee country code."""

    numberOfParcels: int
    """Total parcels count."""

    weightKG: float
    """Total shipment weight in KG."""

    volumeM3: float
    """Total shipment volume in M3."""

    alphanumericSenderReference: str
    """Alphanumeric sender reference."""

    senderCompanyName: str
    """Sender company name."""

    senderProvinceAbbreviation: str
    """Sender province."""

    labels: Labels
    """Generated labels container (if requested)."""


class CreateResult(TypedDict, total=False):
    """Top-level HTTP 200 response structure for shipment creation."""

    createResponse: CreateResponse


class DeleteResponse(TypedDict, total=False):
    """Body of shipment cancellation response."""

    currentTimeUTC: str
    """Response timestamp in UTC with timezone offset."""

    executionMessage: ExecutionMessage
    """Execution outcome diagnostics."""


class DeleteResult(TypedDict, total=False):
    """Top-level HTTP 200 response structure for shipment deletion."""

    deleteResponse: DeleteResponse


class ConfirmResponse(TypedDict, total=False):
    """Body of shipment confirmation response."""

    currentTimeUTC: str
    """Response timestamp in UTC with timezone offset."""

    executionMessage: ExecutionMessage
    """Execution outcome diagnostics."""


class ConfirmResult(TypedDict, total=False):
    """Top-level HTTP 200 response structure for shipment confirmation."""

    confirmResponse: ConfirmResponse


class RoutingResponse(TypedDict, total=False):
    """Body of routing calculation response."""

    currentTimeUTC: str
    """Response timestamp in UTC with timezone offset."""

    executionMessage: ExecutionMessage
    """Execution outcome diagnostics."""

    arrivalTerminal: str
    """BRT arrival terminal."""

    arrivalDepot: str
    """BRT arrival depot code."""

    deliveryZone: str
    """BRT delivery zone code."""

    consigneeZIPCode: str
    """Normalized postal code."""

    consigneeCity: str
    """Normalized destination city."""

    consigneeProvinceAbbreviation: str
    """Normalized destination province."""


class RoutingResult(TypedDict, total=False):
    """Top-level HTTP 200 response structure for routing calculation."""

    routingResponse: RoutingResponse
