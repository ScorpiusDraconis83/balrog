from unittest.mock import MagicMock

import auslib.web.public.helpers
import auslib.web.public.json


def test_get_content_signature_headers(monkeypatch):
    mockapp = MagicMock()
    mockapp.config = {
        "AUTOGRAPH_product_URL": "foo://bar",
        "AUTOGRAPH_product_KEYID": "fookeyid",
        "AUTOGRAPH_product_KEYID_LEGACY": "foolegacykeyid",
        "AUTOGRAPH_product_USERNAME": "foousername",
        "AUTOGRAPH_product_PASSWORD": "foopassword",
    }
    monkeypatch.setattr("auslib.web.public.helpers.app", mockapp)

    content = "some content"
    product = "product"

    x5u = "https://this.is/a.x5u"
    x5u_legacy = "https://this.is/legacy.x5u"
    ecdsa = "foobar"

    def mock_sign_hash(_, key, *__):
        if key == "fookeyid":
            return (ecdsa, x5u)
        elif key == "foolegacykeyid":
            return (ecdsa, x5u_legacy)
        raise ValueError(f"Unexpected key {key}")

    mocksign = MagicMock()
    mocksign.side_effect = mock_sign_hash
    monkeypatch.setattr(auslib.web.public.helpers, "sign_hash", mocksign)

    # Test without legacy key
    assert auslib.web.public.helpers.get_content_signature_headers(content, product, False) == {"Content-Signature": f"x5u={x5u}; p384ecdsa={ecdsa}"}

    # Test with legacy key - should return different x5u
    assert auslib.web.public.helpers.get_content_signature_headers(content, product, True) == {"Content-Signature": f"x5u={x5u_legacy}; p384ecdsa={ecdsa}"}

    assert mocksign.call_count == 2
