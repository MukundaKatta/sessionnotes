"""Tests for Sessionnotes."""
from src.core import Sessionnotes
def test_init(): assert Sessionnotes().get_stats()["ops"] == 0
def test_op(): c = Sessionnotes(); c.generate(x=1); assert c.get_stats()["ops"] == 1
def test_multi(): c = Sessionnotes(); [c.generate() for _ in range(5)]; assert c.get_stats()["ops"] == 5
def test_reset(): c = Sessionnotes(); c.generate(); c.reset(); assert c.get_stats()["ops"] == 0
def test_service_name(): c = Sessionnotes(); r = c.generate(); assert r["service"] == "sessionnotes"
