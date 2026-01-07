# tests/test_price_tools.py


from tools.price_tools import get_price_history, PriceHistoryError


def test_get_price_history_valid():
    df = get_price_history("AAPL", period="1y")

    assert not df.empty
    assert set(df.columns) == {"date", "open", "high", "low", "close", "volume"}
    assert df.isnull().sum().sum() == 0
    assert df.shape[0] > 200  # ~1y of trading days


def test_get_price_history_invalid_ticker():
    try:
        get_price_history("INVALIDTICKER123")
    except PriceHistoryError:
        assert True
    else:
        assert False
