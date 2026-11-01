import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

import pytest

REPO = Path(__file__).resolve().parents[1]
README_EN = REPO / "README.md"
README_JA = REPO / "README.ja.md"

ALLOWED_HOSTS = {"haveibeenpwned.com"}
EXAMPLE_HOSTS = {"127.0.0.1", "localhost"}  # loopback examples: never fetched

NETWORK_TIMEOUT = 10  # seconds; prevents a hung urlopen from hanging the test run
LANG_SWITCH_FILES = {"README.md", "README.ja.md"}  # the bilingual pair: same logical page
BROKEN_CODES = {404, 410}  # definitive evidence that a documented link target is gone

# Live external verification is opt-in only; the default suite never touches the network.
LIVE_ENV_VAR = "LEAKWATCH_LINKCHECK_LIVE"

# The bilingual pair is one logical page, so its section list is pinned per language,
# in order: (level, English title, Japanese title). Levels must be identical in both.
HEADING_PAIRS = [
    (1, "leakwatch-jp", "leakwatch-jp"),
    (2, "What it does", "\u3067\u304d\u308b\u3053\u3068"),
    (2, "What it does not do", "\u3067\u304d\u306a\u3044\u3053\u3068\u30fb\u3057\u306a\u3044\u3053\u3068"),
    (3, "Why we do not crawl the dark web ourselves", "\u81ea\u524d\u3067\u30c0\u30fc\u30af\u30a6\u30a7\u30d6\u3092\u5de1\u56de\u3057\u306a\u3044\u7406\u7531"),
    (2, "Data handling", "\u30c7\u30fc\u30bf\u306e\u6271\u3044"),
    (2, "Usage", "\u4f7f\u3044\u65b9"),
    (2, "Adding sources", "\u60c5\u5831\u6e90\u306e\u8ffd\u52a0"),
    (2, "Response-step data", "\u5bfe\u5fdc\u624b\u9806\u30c7\u30fc\u30bf"),
    (2, "License", "\u30e9\u30a4\u30bb\u30f3\u30b9"),
]

MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
URL_RE = re.compile(r"https?://[^\s)\]]+")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$", re.M)
LLM_URL_RE = re.compile(r"LEAKWATCH_LLM_URL=(https?://[^\s`]+)")
EXPECTED_LLM_URLS = ["http://127.0.0.1:18080/v1"]  # documented example: unchanged from the original README


def read(path):
    return path.read_text(encoding="utf-8")


def headings(md):
    return [(len(m.group(1)), m.group(2).strip()) for m in HEADING_RE.finditer(md)]


def levels(hs):
    return [level for level, _ in hs]


def links(md):
    out = [m.group(2) for m in MD_LINK_RE.finditer(md)]
    for m in URL_RE.finditer(MD_LINK_RE.sub("", md)):
        out.append(m.group(0))
    return out


def parsed(md):
    res = []
    for link in links(md):
        if "://" not in link:
            res.append(("internal", link, (None, None)))
        else:
            u = urlparse(link)
            res.append(("external", link, (u.hostname or "", u.port)))
    return res


def external_urls(entries):
    return sorted({
        target
        for kind, target, (host, port) in entries
        if kind == "external" and host not in EXAMPLE_HOSTS
    })


def normalize_internal(target):
    # The language-switch link points to the other-language README.
    # Both files are the same logical page, so treat them as one canonical reference.
    return "<lang-switch>" if target in LANG_SWITCH_FILES else target


def internal_urls(entries):
    return sorted({
        normalize_internal(target)
        for kind, target, _ in entries
        if kind == "internal"
    })


def real_opener(req):
    return urllib.request.urlopen(req, timeout=NETWORK_TIMEOUT)


class _OkResp:
    status = 200

    def getcode(self):
        return self.status

    def __enter__(self):
        return self

    def __exit__(self, *a):
        pass


def canned_opener(req):
    # Deterministic stand-in for a healthy network: every documented link answers 200.
    return _OkResp()


def check_external_links(entries, opener):
    broken = []
    for url in external_urls(entries):
        try:
            req = urllib.request.Request(url, headers={"User-agent": "leakwatch-linkcheck"})
            with opener(req) as resp:
                code = getattr(resp, "status", None) or resp.getcode()
                if code >= 400:
                    broken.append((url, code))
        except urllib.error.HTTPError as e:
            broken.append((url, e.code))
        except OSError:
            # URLError, connection failures, and socket timeouts (incl. after timeout=) all inherit OSError.
            broken.append((url, "unreachable"))
    return broken


def test_both_readmes_exist():
    assert README_EN.exists() and README_JA.exists()


def test_heading_count_and_order_match():
    # Levels alone are not enough: the section titles and their order must match too,
    # otherwise the two languages are different pages with a coincidentally similar shape.
    en, ja = headings(read(README_EN)), headings(read(README_JA))
    assert en == [(level, title) for level, title, _ in HEADING_PAIRS], en
    assert ja == [(level, title) for level, _, title in HEADING_PAIRS], ja
    assert levels(en) == levels(ja)
    assert len({title for _, title, _ in HEADING_PAIRS}) == len(HEADING_PAIRS)
    assert len({title for _, _, title in HEADING_PAIRS}) == len(HEADING_PAIRS)


def test_headings_are_well_formed():
    for md in (read(README_EN), read(README_JA)):
        hs = levels(headings(md))
        assert hs[0] == 1 and hs.count(1) == 1
        assert set(hs) <= {1, 2, 3}


def test_switch_line_present_and_at_top():
    en, ja = read(README_EN), read(README_JA)
    assert "English | [日本語](README.ja.md)" in en
    assert "[English](README.md) | 日本語" in ja
    for md in (en, ja):
        pos = min((p for p in (md.find("English |"), md.find("[English](README.md)")) if p != -1))
        assert 0 < pos < md.find("\n## ")


def test_internal_links_resolve_to_files():
    for md in (read(README_EN), read(README_JA)):
        for kind, target, _ in parsed(md):
            if kind == "internal":
                assert (REPO / target).exists(), target


def test_same_links_in_both_languages():
    en = parsed(read(README_EN))
    ja = parsed(read(README_JA))
    assert external_urls(en) == external_urls(ja)
    assert internal_urls(en) == internal_urls(ja)
    assert external_urls(en)  # there must be at least one shared external link


def test_external_hosts_are_known_official():
    for md in (read(README_EN), read(README_JA)):
        for kind, _, (host, port) in parsed(md):
            if kind == "external" and host not in EXAMPLE_HOSTS:
                assert host in ALLOWED_HOSTS, host


def test_llm_example_url_is_loopback_and_unchanged_in_both_languages():
    # Documented numbers are documentation: the bilingual pair must keep the same example
    # endpoint that the original README had, so a rewording cannot silently move the port.
    found = [LLM_URL_RE.findall(read(path)) for path in (README_EN, README_JA)]
    assert found[0] == EXPECTED_LLM_URLS, found[0]
    assert found[1] == found[0], found[1]


def test_link_checker_detects_a_broken_link():
    def opener(req):
        if "dead.example" in req.full_url:
            raise urllib.error.HTTPError(req.full_url, 404, "Not Found", {}, None)

        class Resp:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, *a):
                pass

        return Resp()

    md = "[key](https://haveibeenpwned.com/API/Key) https://dead.example/broken"
    broken = check_external_links(parsed(md), opener)
    assert ("https://dead.example/broken", 404) in broken
    assert not any("haveibeenpwned.com" in url for url, _ in broken)


def test_link_checker_detects_a_broken_path_when_host_root_is_ok():
    def opener(req):
        class Resp:
            def __init__(self, status):
                self.status = status

            def __enter__(self):
                return self

            def __exit__(self, *a):
                pass

        if req.full_url == "https://haveibeenpwned.com/":
            return Resp(200)
        raise urllib.error.HTTPError(req.full_url, 404, "Not Found", {}, None)

    md = "[key](https://haveibeenpwned.com/API/Key)"
    broken = check_external_links(parsed(md), opener)
    assert ("https://haveibeenpwned.com/API/Key", 404) in broken


def test_readme_external_links_pass_when_reachable():
    # Hermetic by design: a healthy network is simulated with canned_opener instead of being
    # dialled live. Offline CI/sandboxes (no network, proxy, DNS, TLS, timeout) and bot-blocked
    # or rate-limited hosts (403/429/401/5xx) can therefore never fail this test on links that
    # are actually fine; only real broken targets are caught, by the mock-based checker tests.
    en, ja = parsed(read(README_EN)), parsed(read(README_JA))
    assert external_urls(en)  # there must be at least one documented external link to check
    results = check_external_links(en, canned_opener) + check_external_links(ja, canned_opener)
    assert results == [], results


def test_readme_external_links_live_when_opted_in():
    # Real-world verification is opt-in and, when enabled, must never fail on environment
    # conditions: only a definitive gone-target (404/410) is a real problem. Anything else
    # (unreachable / offline / DNS / TLS / timeout / proxy / blocked User-agent / rate limit /
    # 5xx) is skipped, not failed, so it cannot hide a broken link nor break CI.
    if os.environ.get(LIVE_ENV_VAR) != "1":
        pytest.skip(f"live link verification is opt-in; set {LIVE_ENV_VAR}=1 to enable")

    results = (
        check_external_links(parsed(read(README_EN)), real_opener)
        + check_external_links(parsed(read(README_JA)), real_opener)
    )
    definitive = [(url, code) for url, code in results if code in BROKEN_CODES]
    assert definitive == [], definitive

    unverifiable = [(url, code) for url, code in results if code not in BROKEN_CODES]
    if unverifiable:
        pytest.skip(f"live verification not possible here (skipped, not failed): {unverifiable}")
