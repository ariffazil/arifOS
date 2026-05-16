# arifOS SENSE Pipeline — Phase 4D Verify + Expand Tests
# DITEMPA BUKAN DIBERI

from __future__ import annotations

import pytest

import arifosmcp.runtime.verify_expander as ve_module


class TestIsSafeUrl:
    def test_valid_https_url(self):
        assert ve_module._is_safe_url("https://python.dev/test")

    def test_valid_http_url(self):
        assert ve_module._is_safe_url("http://python.dev/test")

    def test_ftp_scheme_blocked(self):
        assert not ve_module._is_safe_url("ftp://python.dev/file")

    def test_file_scheme_blocked(self):
        assert not ve_module._is_safe_url("file:///etc/passwd")

    def test_tel_scheme_blocked(self):
        assert not ve_module._is_safe_url("tel:+1234567890")

    def test_mailto_scheme_blocked(self):
        assert not ve_module._is_safe_url("mailto:test@example.com")

    def test_javascript_scheme_blocked(self):
        assert not ve_module._is_safe_url("javascript:alert(1)")

    def test_empty_url_blocked(self):
        assert not ve_module._is_safe_url("")

    def test_too_long_url_blocked(self):
        long_url = "https://python.dev/" + "a" * 600000
        assert not ve_module._is_safe_url(long_url)


class TestVerifyUrl:
    @pytest.mark.asyncio
    async def test_verify_python_dev_reachable(self):
        result = await ve_module.verify_url("https://python.dev/")
        assert result.is_safe
        assert result.url == "https://python.dev/"

    @pytest.mark.asyncio
    async def test_verify_http_blocked_scheme(self):
        result = await ve_module.verify_url("ftp://python.dev/")
        assert not result.is_safe

    @pytest.mark.asyncio
    async def test_verify_none_url(self):
        result = await ve_module.verify_url("")
        assert not result.is_safe


class TestExpandUrl:
    @pytest.mark.asyncio
    async def test_expand_direct(self):
        result = await ve_module.expand_url("https://python.dev/", method="direct")
        assert result.original_url == "https://python.dev/"
        assert result.method == "direct"

    @pytest.mark.asyncio
    async def test_expand_without_key_falls_to_direct(self):
        result = await ve_module.expand_url("https://python.dev/", method="firecrawl")
        assert result.method in ("firecrawl", "direct")


class TestVerifyExpander:
    @pytest.mark.asyncio
    async def test_verify_method(self):
        ve = ve_module.VerifyExpander()
        result = await ve.verify("https://python.dev/")
        assert result.is_safe

    @pytest.mark.asyncio
    async def test_expand_method(self):
        ve = ve_module.VerifyExpander(default_method="direct")
        result = await ve.expand("https://python.dev/")
        assert result.original_url == "https://python.dev/"

    @pytest.mark.asyncio
    async def test_verify_and_expand(self):
        ve = ve_module.VerifyExpander(default_method="direct")
        verify_result, expand_result = await ve.verify_and_expand("https://python.dev/")
        assert verify_result.is_safe
        assert expand_result.original_url == "https://python.dev/"

    def test_verify_expander_default_method(self):
        ve = ve_module.VerifyExpander(default_method="firecrawl")
        assert ve._default_method == "firecrawl"


class TestExpansionResult:
    @pytest.mark.asyncio
    async def test_expansion_result_fields(self):
        result = await ve_module.expand_url("https://python.dev/", method="direct")
        assert hasattr(result, "original_url")
        assert hasattr(result, "expanded_urls")
        assert hasattr(result, "verification")
        assert hasattr(result, "method")


class TestVerifyResult:
    def test_verify_result_fields(self):
        from arifosmcp.runtime.verify_expander import VerifyResult

        vr = VerifyResult(
            url="https://python.dev/",
            is_safe=True,
            is_reachable=False,
            status_code=None,
            content_type=None,
            content_length=None,
            final_url=None,
            error="failed",
        )
        assert vr.url == "https://python.dev/"
        assert vr.is_safe
        assert not vr.is_reachable
