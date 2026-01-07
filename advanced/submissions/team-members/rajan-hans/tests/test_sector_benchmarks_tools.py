# tests/test_sector_benchmarks_tools.py


from tools.sector_benchmarks_tools import get_sector_benchmarks


def test_get_sector_benchmarks_valid():
    result = get_sector_benchmarks(ticker="AAPL", sector="Technology")

    assert result["sector"] == "Technology"
    assert "valuation" in result
    assert "profitability" in result
    assert result["valuation"]["pe_median"] > 0


def test_get_sector_benchmarks_invalid_sector():
    try:
        get_sector_benchmarks("AAPL", sector="UnknownSector")
    except Exception:
        assert True
    else:
        assert False
