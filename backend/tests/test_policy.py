"""Policy-as-code loading + resolution."""
from app.config import get_settings
from app.governance.policy import load_policies


def _registry():
    return load_policies(get_settings())


def test_ships_domain_policies():
    reg = _registry()
    assert {"default", "underwriting", "logistics"} <= {p.domain for p in reg.all()}


def test_unknown_domain_falls_back_to_default():
    reg = _registry()
    assert reg.resolve("does-not-exist").domain == "default"
    assert reg.resolve(None).domain == "default"


def test_underwriting_is_stricter_than_default():
    reg = _registry()
    default = reg.resolve(None)
    uw = reg.resolve("underwriting")
    assert uw.min_faithfulness > default.min_faithfulness
    assert uw.require_citations is True
    assert "guaranteed approval" in uw.banned_claims


def test_default_first_in_listing():
    assert _registry().all()[0].domain == "default"
