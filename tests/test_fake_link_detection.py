"""Regression tests for local fake-link analysis without network access."""

import asyncio

import httpx
import pytest
from fastapi.testclient import TestClient

from sentinel_ai.main import app
from sentinel_ai.services.gophish_simulation import (
    GoPhishSimulationAdapter,
    GoPhishSimulationSettings,
)

client = TestClient(app)


@pytest.mark.parametrize(
    ("url", "signal"),
    [
        ("https://paypa1-login.example/signin", "Possible brand impersonation"),
        ("https://nu-cashback.link/", "Suspicious reward-lure domain"),
        ("https://amazon-account-verify.example/login", "Possible brand impersonation"),
        ("https://xn--e1afmkfd.xn--p1ai/", "Encoded domain"),
        ("https://192.0.2.12/", "IP-address URL"),
        ("https://10.196.252.46.host.secureserver.net/pdf/", "IP-address-style subdomain"),
        ("https://mahjxs.us.cc/5g/home.html", "Opaque free-subdomain host"),
        ("https://trusted.example@malicious.example/login", "Misleading URL authority"),
        ("https://example.com/?destination=https%3A%2F%2Fevil.example", "Redirect-style URL"),
        ("https://bit.ly/example", "URL shortener"),
        ("https://example.com/%6c%6f%67%69%6e", "Encoded URL content"),
        ("https://example.com/account/verify", "Credential-harvesting URL"),
        ("https://example.com/prize/payment", "Payment or prize lure URL"),
        ("https://example.com/adult-lure", "Potentially deceptive media link"),
        ("https://example.com/application.apk", "Executable or archive download link"),
        ("https://example.com/archive.zip", "Executable or archive download link"),
    ],
)
def test_fake_link_signals_are_explainable(url: str, signal: str) -> None:
    response = client.post("/analyze", json={"urls": [url]})

    assert response.status_code == 200
    assert signal in {item["signal"] for item in response.json()["evidence"]}
    assert response.json()["analysis_sources"] == ["local_rules"]


@pytest.mark.parametrize(
    "url",
    [
        "https://www.paypal.com/help",
        "https://www.amazon.com/gp/help/customer/display.html",
        "https://www.gov.uk/government/organisations",
        "https://www.harvard.edu/academics/",
        "https://www.microsoft.com/en-us/download",
    ],
)
def test_legitimate_urls_do_not_trigger_brand_impersonation(url: str) -> None:
    response = client.post("/analyze", json={"urls": [url]})

    assert response.status_code == 200
    assert "Possible brand impersonation" not in {
        item["signal"] for item in response.json()["evidence"]
    }


def test_reward_word_without_high_risk_domain_pattern_is_not_flagged() -> None:
    response = client.post("/analyze", json={"urls": ["https://offers.example/cashback"]})

    assert response.status_code == 200
    assert "Suspicious reward-lure domain" not in {
        item["signal"] for item in response.json()["evidence"]
    }


def test_gophish_adapter_is_disabled_without_explicit_authorization(monkeypatch) -> None:
    def no_network(*_args, **_kwargs):
        raise AssertionError("Disabled GoPhish integration must not create an HTTP client.")

    monkeypatch.setattr("sentinel_ai.services.gophish_simulation.httpx.AsyncClient", no_network)
    adapter = GoPhishSimulationAdapter(GoPhishSimulationSettings(None, None, False))

    assert asyncio.run(adapter.authorized_fixture_urls()) == []


def test_gophish_adapter_extracts_only_https_urls_from_mocked_metadata(monkeypatch) -> None:
    class FakeResponse:
        status_code = 200

        @staticmethod
        def json():
            return [
                {"url": "https://simulation.example/login", "name": "ignored"},
                {"url": "http://insecure.example", "targets": ["never returned"]},
                {"url": "https://simulation.example/login"},
            ]

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def get(self, *_args, **_kwargs):
            return FakeResponse()

    monkeypatch.setattr(
        "sentinel_ai.services.gophish_simulation.httpx.AsyncClient",
        lambda **_kwargs: FakeClient(),
    )
    adapter = GoPhishSimulationAdapter(
        GoPhishSimulationSettings("https://gophish.example", "test-key", True)
    )

    assert asyncio.run(adapter.authorized_fixture_urls()) == [
        "https://simulation.example/login"
    ]


def test_gophish_provider_failure_is_silent_and_safe(monkeypatch) -> None:
    class FailingClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def get(self, *_args, **_kwargs):
            raise httpx.ConnectError("provider unavailable")

    monkeypatch.setattr(
        "sentinel_ai.services.gophish_simulation.httpx.AsyncClient",
        lambda **_kwargs: FailingClient(),
    )
    adapter = GoPhishSimulationAdapter(
        GoPhishSimulationSettings("https://gophish.example", "test-key", True)
    )

    assert asyncio.run(adapter.authorized_fixture_urls()) == []
