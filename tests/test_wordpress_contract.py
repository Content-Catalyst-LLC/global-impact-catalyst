from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PHP = (ROOT / "wordpress/global-impact-catalyst-demo/global-impact-catalyst-demo.php").read_text()


def test_shortcode_uses_per_instance_ids():
    assert "static $instance = 0" in PHP
    assert "$id_prefix" in PHP
    assert 'id="gic-' not in PHP


def test_accessibility_contract_present():
    assert "data-gic-errors" in PHP
    assert 'role="alert"' in PHP
    assert 'aria-live="polite"' in PHP
    assert "required" in PHP
