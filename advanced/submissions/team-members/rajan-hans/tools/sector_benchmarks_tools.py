# tools/sector_benchmarks_tools.py
from datetime import date
from config import SECTOR_BENCHMARKS  # Imports from your new config file


class SectorBenchmarkError(Exception):
    """Raised when sector benchmarks cannot be resolved."""


def get_sector_benchmarks(ticker: str, sector: str | None = None) -> dict:
    if not sector:
        raise SectorBenchmarkError("Sector not provided.")

    if sector not in SECTOR_BENCHMARKS:
        # Graceful fallback instead of crashing
        print(
            f"Warning: Sector '{sector}' not found in benchmarks. Using Technology default."
        )
        sector = "Technology"

    benchmarks = SECTOR_BENCHMARKS[sector]

    return {
        "sector": sector,
        "valuation": benchmarks["valuation"],
        "profitability": benchmarks["profitability"],
        "as_of_date": date.today().isoformat(),
        "source": "static_v1",
    }
