"""Tests for mapper interface compliance."""

import pytest
from prism.interfaces.mapper import IAuthzMapper

# This module doesn't yet implement a full IAuthzMapper that ties it all
# together, but we test the interface loading.
def test_mapper_interface_loading() -> None:
    assert IAuthzMapper is not None
