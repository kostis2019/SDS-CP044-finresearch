# config.py
# Centralized configuration for FinResearch AI
# ---------------------------------------------

# =============================================================================
# SECTOR BENCHMARKS FOR RELATIVE VALUATION
# =============================================================================
#
# PURPOSE:
# These benchmarks represent median/typical values for companies within each
# sector. They are used to compare individual stocks against their sector peers
# for relative valuation analysis.
#
# HOW THEY'RE USED:
# 1. Valuation Score: A stock's P/E is compared to sector median
#    - P/E below sector median = positive adjustment (+8 to +15 points)
#    - P/E above sector median = negative adjustment (-8 to -15 points)
# 2. Sector Comparison Charts: Visual comparison of stock vs sector
# 3. Reporter Analysis: Context for valuation commentary
#
# DATA SOURCES & METHODOLOGY:
# - Values are approximate medians based on S&P 500 sector constituents
# - Sources: Yahoo Finance, Morningstar, NYU Stern Damodaran datasets
# - Last updated: December 2024
# - These are STATIC values and should be reviewed/updated quarterly
#
# LIMITATIONS:
# - Medians vary based on market conditions and index composition
# - Large-cap bias (based primarily on S&P 500 companies)
# - Does not account for sub-industry variations
# - Consider implementing dynamic fetching for production use
#
# UPDATE SCHEDULE:
# Recommend updating these values quarterly or when significant market
# shifts occur. Check against sources like:
# - https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/pedata.html
# - https://www.yardeni.com/pub/peacockfeval.pdf
# - Bloomberg/Reuters sector reports
#
# =============================================================================

SECTOR_BENCHMARKS = {
    # -------------------------------------------------------------------------
    # TECHNOLOGY
    # Includes: Software, Hardware, Semiconductors, IT Services
    # Characteristics: High growth, high margins, premium valuations
    # Examples: AAPL, MSFT, NVDA, ADBE, CRM
    # -------------------------------------------------------------------------
    "Technology": {
        "valuation": {
            "pe_median": 32.0,  # Higher due to AI/cloud growth (was 28)
            "forward_pe_median": 27.0,  # Forward expectations remain high
            "peg_median": 1.9,  # Reasonable given growth rates
            "ps_median": 7.5,  # Premium for recurring revenue models
        },
        "profitability": {
            "gross_margin_median": 0.58,  # 58% - strong for software/semis
            "operating_margin_median": 0.26,  # 26% - healthy operating leverage
            "net_margin_median": 0.21,  # 21% - after tax profits
        },
    },
    # -------------------------------------------------------------------------
    # HEALTHCARE
    # Includes: Pharma, Biotech, Medical Devices, Healthcare Services
    # Characteristics: Defensive, R&D intensive, regulatory moats
    # Examples: JNJ, UNH, PFE, MRK, ABBV
    # -------------------------------------------------------------------------
    "Healthcare": {
        "valuation": {
            "pe_median": 20.0,  # Moderate, reflecting patent cliffs
            "forward_pe_median": 17.0,  # Slightly lower on pipeline concerns
            "peg_median": 1.8,  # Growth challenged in big pharma
            "ps_median": 4.0,  # Varies widely (biotech vs devices)
        },
        "profitability": {
            "gross_margin_median": 0.62,  # 62% - high for pharma
            "operating_margin_median": 0.22,  # 22% - R&D weighs on margins
            "net_margin_median": 0.16,  # 16% - regulatory costs
        },
    },
    # -------------------------------------------------------------------------
    # FINANCIAL SERVICES
    # Includes: Banks, Insurance, Asset Management, Fintech
    # Characteristics: Rate sensitive, leverage-based, regulatory
    # Examples: JPM, BAC, GS, BRK.B, V, MA
    # -------------------------------------------------------------------------
    "Financial Services": {
        "valuation": {
            "pe_median": 14.0,  # Historically low multiples
            "forward_pe_median": 12.5,  # Rate normalization concerns
            "peg_median": 1.3,  # Modest growth expectations
            "ps_median": 3.5,  # Revenue recognition differs
        },
        "profitability": {
            "gross_margin_median": 0.50,  # 50% - varies by sub-sector
            "operating_margin_median": 0.32,  # 32% - high for asset-light
            "net_margin_median": 0.24,  # 24% - good efficiency
        },
    },
    # -------------------------------------------------------------------------
    # CONSUMER CYCLICAL (Consumer Discretionary)
    # Includes: Retail, Auto, Restaurants, Travel, Apparel
    # Characteristics: Economic sensitivity, consumer spending dependent
    # Examples: AMZN, TSLA, HD, MCD, NKE
    # -------------------------------------------------------------------------
    "Consumer Cyclical": {
        "valuation": {
            "pe_median": 22.0,  # Elevated by AMZN, TSLA
            "forward_pe_median": 19.0,  # Growth expectations
            "peg_median": 1.5,  # Reasonable for growth
            "ps_median": 1.8,  # Lower margins = lower P/S
        },
        "profitability": {
            "gross_margin_median": 0.38,  # 38% - retail pressures
            "operating_margin_median": 0.12,  # 12% - competitive markets
            "net_margin_median": 0.07,  # 7% - thin margins typical
        },
    },
    # -------------------------------------------------------------------------
    # INDUSTRIALS
    # Includes: Aerospace, Defense, Machinery, Transportation, Construction
    # Characteristics: Capex intensive, economic cycle sensitive
    # Examples: CAT, BA, UNP, HON, GE
    # -------------------------------------------------------------------------
    "Industrials": {
        "valuation": {
            "pe_median": 22.0,  # Infrastructure spending boost
            "forward_pe_median": 19.0,  # Reshoring tailwinds
            "peg_median": 1.6,  # Moderate growth
            "ps_median": 2.2,  # Capital goods premiums
        },
        "profitability": {
            "gross_margin_median": 0.32,  # 32% - manufacturing costs
            "operating_margin_median": 0.14,  # 14% - improving efficiency
            "net_margin_median": 0.09,  # 9% - capex heavy
        },
    },
    # -------------------------------------------------------------------------
    # ENERGY
    # Includes: Oil & Gas, Exploration, Refining, Energy Equipment
    # Characteristics: Commodity price sensitive, capital intensive
    # Examples: XOM, CVX, SLB, COP, EOG
    # -------------------------------------------------------------------------
    "Energy": {
        "valuation": {
            "pe_median": 12.0,  # Commodity discount
            "forward_pe_median": 10.5,  # Earnings volatility priced in
            "peg_median": 1.0,  # Low growth expectations
            "ps_median": 1.3,  # Revenue tied to oil prices
        },
        "profitability": {
            "gross_margin_median": 0.35,  # 35% - refining margins vary
            "operating_margin_median": 0.18,  # 18% - improved discipline
            "net_margin_median": 0.11,  # 11% - tax and royalty impact
        },
    },
    # -------------------------------------------------------------------------
    # UTILITIES
    # Includes: Electric, Gas, Water Utilities, Renewable Energy
    # Characteristics: Regulated, stable dividends, rate base growth
    # Examples: NEE, DUK, SO, D, AEP
    # -------------------------------------------------------------------------
    "Utilities": {
        "valuation": {
            "pe_median": 18.0,  # Bond proxy valuations
            "forward_pe_median": 16.5,  # Rate case uncertainty
            "peg_median": 2.8,  # Low growth = high PEG
            "ps_median": 2.5,  # Regulated revenue
        },
        "profitability": {
            "gross_margin_median": 0.42,  # 42% - regulated margins
            "operating_margin_median": 0.22,  # 22% - infrastructure costs
            "net_margin_median": 0.14,  # 14% - interest expense heavy
        },
    },
    # -------------------------------------------------------------------------
    # COMMUNICATION SERVICES
    # Includes: Telecom, Media, Entertainment, Interactive Media
    # Characteristics: Mix of old telecom and new media/tech
    # Examples: GOOG, META, DIS, NFLX, VZ, T
    # -------------------------------------------------------------------------
    "Communication Services": {
        "valuation": {
            "pe_median": 20.0,  # Blended old/new media
            "forward_pe_median": 17.0,  # Ad market normalization
            "peg_median": 1.4,  # Growth moderating
            "ps_median": 3.8,  # Digital ad premium
        },
        "profitability": {
            "gross_margin_median": 0.55,  # 55% - digital platforms high
            "operating_margin_median": 0.24,  # 24% - content costs vary
            "net_margin_median": 0.16,  # 16% - investment phase
        },
    },
    # -------------------------------------------------------------------------
    # BASIC MATERIALS
    # Includes: Chemicals, Metals & Mining, Paper, Construction Materials
    # Characteristics: Commodity exposure, cyclical, global demand
    # Examples: LIN, APD, NEM, FCX, NUE
    # -------------------------------------------------------------------------
    "Basic Materials": {
        "valuation": {
            "pe_median": 15.0,  # Commodity cycle discount
            "forward_pe_median": 13.0,  # Earnings volatility
            "peg_median": 1.2,  # Low sustainable growth
            "ps_median": 1.8,  # Capital intensive
        },
        "profitability": {
            "gross_margin_median": 0.28,  # 28% - raw material costs
            "operating_margin_median": 0.14,  # 14% - processing costs
            "net_margin_median": 0.09,  # 9% - capital heavy
        },
    },
    # -------------------------------------------------------------------------
    # REAL ESTATE (REITs)
    # Includes: Residential, Commercial, Industrial, Specialty REITs
    # Characteristics: Dividend focused, FFO-based valuation, rate sensitive
    # Examples: PLD, AMT, EQIX, SPG, O
    # Note: P/E less meaningful for REITs; FFO multiples preferred
    # -------------------------------------------------------------------------
    "Real Estate": {
        "valuation": {
            "pe_median": 38.0,  # Distorted by depreciation (use FFO)
            "forward_pe_median": 34.0,  # High due to GAAP accounting
            "peg_median": 3.0,  # Low growth, high multiples
            "ps_median": 9.0,  # Asset-heavy model
        },
        "profitability": {
            "gross_margin_median": 0.58,  # 58% - rental income
            "operating_margin_median": 0.38,  # 38% - NOI focused
            "net_margin_median": 0.22,  # 22% - depreciation impact
        },
    },
    # -------------------------------------------------------------------------
    # CONSUMER DEFENSIVE (Consumer Staples)
    # Includes: Food & Beverage, Household Products, Tobacco, Retail Staples
    # Characteristics: Recession resistant, stable demand, dividend focus
    # Examples: PG, KO, PEP, WMT, COST
    # -------------------------------------------------------------------------
    "Consumer Defensive": {
        "valuation": {
            "pe_median": 24.0,  # Defensive premium
            "forward_pe_median": 21.0,  # Stable earnings
            "peg_median": 2.5,  # Low growth = high PEG
            "ps_median": 2.8,  # Brand value premium
        },
        "profitability": {
            "gross_margin_median": 0.36,  # 36% - COGS pressures
            "operating_margin_median": 0.14,  # 14% - marketing costs
            "net_margin_median": 0.09,  # 9% - mature businesses
        },
    },
}


# =============================================================================
# SCORING CONFIGURATION
# =============================================================================
#
# These weights determine how much each factor contributes to the final score.
# Total weights should sum to 1.0 (100%)
#
# RATIONALE:
# - Valuation (25%): Core driver of returns, but can stay extended
# - Growth (25%): Future earnings power, key for appreciation
# - Profitability (15%): Quality indicator, margin sustainability
# - Financial Health (15%): Risk factor, balance sheet strength
# - Technical (20%): Timing and momentum, market sentiment
#
# =============================================================================

SCORING = {
    "valuation": {
        "weights": {
            "pe": 0.4,  # P/E is primary valuation metric
            "peg": 0.3,  # Growth-adjusted valuation
            "sector_rel": 0.3,  # Relative to sector peers
        }
    },
    "weights": {
        "valuation": 0.25,
        "growth": 0.25,
        "profitability": 0.15,
        "financial_health": 0.15,
        "technical": 0.20,
    },
}


# =============================================================================
# VERSION & METADATA
# =============================================================================

CONFIG_VERSION = "2.0"
LAST_UPDATED = "2024-12-26"
BENCHMARK_SOURCE = "S&P 500 sector medians (approximate)"
