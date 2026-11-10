import unittest
from unittest.mock import MagicMock, patch

from brt_pz import BrtPZ, CreateData


class TestBrtPZ(unittest.TestCase):
    def setUp(self) -> None:
        self.client = BrtPZ(
            user_id="test_user",
            password="test_password",
            customer_code=1020100,
            departure_depot=102,
        )

    def tearDown(self) -> None:
        self.client.close()

    def test_init_credentials_password(self) -> None:
        client = BrtPZ(user_id="user1", password="pw1")
        self.assertEqual(client.user_id, "user1")
        self.assertEqual(client._password, "pw1")
        self.assertTrue(client.base_url.endswith("/shipments"))

    def test_init_missing_required_params_raises(self) -> None:
        with self.assertRaises(TypeError):
            BrtPZ(user_id="user1")  # type: ignore[call-arg]
        with self.assertRaises(ValueError):
            BrtPZ(user_id="", password="pw1")
        with self.assertRaises(ValueError):
            BrtPZ(user_id="user1", password="")
        with self.assertRaises(TypeError):
            BrtPZ(user_id=123, password="pw1")  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            BrtPZ(user_id="user1", password=123)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            BrtPZ(user_id="user1", password="pw1", customer_code="not_an_int")  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            BrtPZ(user_id="user1", password="pw1", departure_depot="not_an_int")  # type: ignore[arg-type]

    def test_default_base_url(self) -> None:
        client = BrtPZ(user_id="user", password="pw")
        self.assertEqual(client.base_url, "https://api.brt.it/rest/v1/shipments")

    def test_custom_base_url_normalization(self) -> None:
        client1 = BrtPZ(user_id="user", password="pw", base_url="https://api.brt.it/rest/v1")
        self.assertEqual(client1.base_url, "https://api.brt.it/rest/v1/shipments")

        client2 = BrtPZ(user_id="user", password="pw", base_url="https://api.brt.it/rest/v1/shipments/")
        self.assertEqual(client2.base_url, "https://api.brt.it/rest/v1/shipments")

    def test_headers_transport_layer(self) -> None:
        headers = self.client._headers
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        self.assertEqual(headers["Accept"], "application/json")
        self.assertNotIn("userID", headers)
        self.assertNotIn("securityToken", headers)

    @patch("requests.Session.request")
    def test_create_shipment_success(self, mock_request: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "createResponse": {
                "currentTimeUTC": "2026-11-10T15:30:00+01:00",
                "executionMessage": {
                    "code": 0,
                    "severity": "INFO",
                    "codeDesc": "Shipment created",
                    "message": "OK",
                },
                "arrivalTerminal": "BO",
                "arrivalDepot": "102",
                "deliveryZone": "01",
                "parcelNumberFrom": "102000000001",
                "parcelNumberTo": "102000000001",
                "departureDepot": 102,
                "seriesNumber": 1,
                "labels": {
                    "label": [
                        {
                            "dataLength": 100,
                            "parcelID": "102165010070284108",
                            "stream": "BASE64PDF",
                        }
                    ]
                },
            }
        }
        mock_request.return_value = mock_response

        shipment_data: CreateData = {
            "departureDepot": 102,
            "senderCustomerCode": 1020100,
            "deliveryFreightTypeCode": "DAP",
            "consigneeCompanyName": "Test Consignee",
            "consigneeAddress": "Via Test 123",
            "consigneeZIPCode": "40100",
            "consigneeCity": "Bologna",
            "consigneeCountryAbbreviationISOAlpha2": "IT",
            "numberOfParcels": 1,
            "weightKG": 2.5,
            "numericSenderReference": 12345,
        }

        res = self.client.create_shipment(shipment_data, is_label_required="1")

        self.assertIsNotNone(res)
        self.assertIn("createResponse", res)
        self.assertEqual(res["createResponse"]["executionMessage"]["code"], 0)

        # Verify sent payload
        call_kwargs = mock_request.call_args[1]
        sent_json = call_kwargs["json"]
        self.assertEqual(sent_json["account"]["userID"], "test_user")
        self.assertEqual(sent_json["account"]["password"], "test_password")
        self.assertEqual(sent_json["createData"]["numericSenderReference"], 12345)
        self.assertEqual(sent_json["isLabelRequired"], "1")
        self.assertIn("labelParameters", sent_json)

    @patch("requests.Session.request")
    def test_create_shipment_injects_defaults(self, mock_request: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"createResponse": {"executionMessage": {"code": 0}}}
        mock_request.return_value = mock_response

        # Omit departureDepot and senderCustomerCode; client defaults should be injected
        shipment_data = {
            "deliveryFreightTypeCode": "DAP",
            "consigneeCompanyName": "Test Consignee",
            "consigneeAddress": "Via Test 123",
            "consigneeZIPCode": "40100",
            "consigneeCity": "Bologna",
            "consigneeCountryAbbreviationISOAlpha2": "IT",
            "numberOfParcels": 1,
            "weightKG": 1.0,
            "numericSenderReference": 54321,
        }

        self.client.create_shipment(shipment_data)

        sent_json = mock_request.call_args[1]["json"]
        self.assertEqual(sent_json["createData"]["departureDepot"], 102)
        self.assertEqual(sent_json["createData"]["senderCustomerCode"], 1020100)

    @patch("requests.Session.request")
    def test_create_shipment_error_response(self, mock_request: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "createResponse": {
                "executionMessage": {
                    "code": -67,
                    "severity": "ERROR",
                    "codeDesc": "Errore su User/Account",
                    "message": "Codice cliente non associato",
                }
            }
        }
        mock_request.return_value = mock_response

        res = self.client.create_shipment({"numericSenderReference": 1})
        self.assertIsNotNone(res)
        self.assertEqual(res["createResponse"]["executionMessage"]["code"], -67)

    @patch("requests.Session.request")
    def test_delete_shipment_success(self, mock_request: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "deleteResponse": {
                "currentTimeUTC": "2026-11-10T16:00:00+01:00",
                "executionMessage": {
                    "code": 0,
                    "severity": "INFO",
                    "codeDesc": "Shipment cancelled",
                    "message": "OK",
                },
            }
        }
        mock_request.return_value = mock_response

        res = self.client.delete_shipment(
            numeric_sender_reference=55,
            alphanumeric_sender_reference="REF-001",
        )

        self.assertIsNotNone(res)
        self.assertEqual(res["deleteResponse"]["executionMessage"]["code"], 0)

        # Verify method and URL
        call_args = mock_request.call_args
        self.assertEqual(call_args[1]["method"], "PUT")
        self.assertTrue(call_args[1]["url"].endswith("/delete"))

        sent_json = call_args[1]["json"]
        self.assertEqual(sent_json["account"]["userID"], "test_user")
        self.assertEqual(sent_json["account"]["password"], "test_password")
        self.assertEqual(sent_json["deleteData"]["senderCustomerCode"], 1020100)
        self.assertEqual(sent_json["deleteData"]["numericSenderReference"], 55)
        self.assertEqual(sent_json["deleteData"]["alphanumericSenderReference"], "REF-001")

    @patch("requests.Session.request")
    def test_delete_shipment_type_validation(self, mock_request: MagicMock) -> None:
        with self.assertRaises(TypeError):
            self.client.delete_shipment(numeric_sender_reference="not_an_int")  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            self.client.delete_shipment(numeric_sender_reference=10, alphanumeric_sender_reference=123)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            self.client.delete_shipment(numeric_sender_reference=10, sender_customer_code="invalid")  # type: ignore[arg-type]

    def test_delete_shipment_missing_customer_code(self) -> None:
        client_no_code = BrtPZ(user_id="user", password="pw")
        with self.assertRaises(ValueError):
            client_no_code.delete_shipment(numeric_sender_reference=10)

    def test_label_utilities(self) -> None:
        import base64
        import tempfile

        raw_content = b"%PDF-1.4 test label content"
        b64_content = base64.b64encode(raw_content).decode("ascii")

        label_dict = {"parcelID": "P001", "stream": b64_content}
        decoded = BrtPZ.get_label_bytes(label_dict)
        self.assertEqual(decoded, raw_content)

        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = f"{tmpdir}/sub/test_label.pdf"
            saved_path = BrtPZ.save_label(label_dict, out_file)
            self.assertTrue(saved_path.is_file())
            self.assertEqual(saved_path.read_bytes(), raw_content)


if __name__ == "__main__":
    unittest.main()
