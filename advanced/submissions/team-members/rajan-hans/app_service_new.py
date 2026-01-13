# app_service_new.py
# Service layer for the FinResearch Streamlit application
# Uses the pure CrewAI FinResearchCrew with auto sector detection
# Note: load_dotenv() should be called at application entry point only
# ---------------------------------------------

import asyncio
from typing import Dict, Any
from datetime import datetime

from crews.finresearch_crew import FinResearchCrew
from llm.llm_factory import get_llm
from tools.sector_detection import detect_sector
from tools.chroma_save_tools import save_to_chroma
from tools.chroma_retrieve_tools import retrieve_from_chroma

# Configuration
ANALYSIS_TIMEOUT_SECONDS = 300  # 5 minutes timeout


async def run_full_research(
    *,
    ticker: str,
    force_refresh: bool = False,
    timeout_seconds: float = ANALYSIS_TIMEOUT_SECONDS,
) -> Dict[str, Any]:
    """
    Execute the full FinResearch pipeline using pure CrewAI.
    Sector is automatically detected from the ticker using Yahoo Finance.

    Now supports Smart Caching via ChromaDB with Self-Healing Logic.
    """
    start_time = datetime.now()

    # 1. Detect Sector (Fast, always run this first)
    mapped_sector, raw_sector = detect_sector(ticker)

    # ---------------------------------------------------------
    # SMART CACHING LOGIC (WITH VALIDATION)
    # ---------------------------------------------------------
    if not force_refresh:
        try:
            print(f"Checking cache for {ticker}...")
            cached_result = retrieve_from_chroma(ticker=ticker, artifact_type="report")

            # CRITICAL FIX: Validate the cached data before using it.
            # If the cached report has no score (is None), it's a "Black Report" / Bad Record.
            # We must ignore it and force a re-run to heal the cache.
            if cached_result and cached_result.get("final_score") is not None:
                print(f"Cache hit for {ticker} and data is valid.")

                # Update execution info to show it came from cache
                cached_result["execution_info"] = {
                    "execution_time_seconds": 0.0,
                    "status": "success (cached)",
                    "cache_hit": True,
                }
                # Ensure sector info is consistent
                cached_result["sector"] = mapped_sector
                cached_result["raw_sector"] = raw_sector

                return cached_result
            elif cached_result:
                print(
                    f"Cache hit for {ticker} but data was incomplete (Black Report). Ignoring cache to self-heal."
                )
            else:
                print(f"Cache miss for {ticker}.")

        except Exception as e:
            print(f"Cache lookup failed (continuing with fresh analysis): {e}")
    # ---------------------------------------------------------

    try:
        # 2. Initialize Crew
        llm = get_llm()
        crew = FinResearchCrew(llm=llm)

        # 3. Run Crew (in thread to avoid blocking asyncio loop)
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(
                    crew.run,
                    ticker=ticker,
                    sector=mapped_sector,
                    force_refresh=force_refresh,
                ),
                timeout=timeout_seconds,
            )
        except asyncio.TimeoutError:
            end_time = datetime.now()
            return {
                "ticker": ticker,
                "sector": mapped_sector,
                "raw_sector": raw_sector,
                "error": f"Analysis timed out after {timeout_seconds} seconds",
                "execution_info": {
                    "execution_time_seconds": round(
                        (end_time - start_time).total_seconds(), 2
                    ),
                    "status": "timeout",
                },
            }

        end_time = datetime.now()

        # Enrich result
        result["sector"] = mapped_sector
        result["raw_sector"] = raw_sector
        result["execution_info"] = {
            "execution_time_seconds": round((end_time - start_time).total_seconds(), 2),
            "status": "success",
            "cache_hit": False,
        }

        # 4. SAVE TO MEMORY (CHROMA DB)
        try:
            # VALIDATION CHECK: Only save if we have a valid score
            if result.get("final_score") is not None:
                save_to_chroma(
                    ticker=ticker,
                    artifact_type="report",
                    content=result,
                    metadata={
                        "sector": mapped_sector,
                        "rating": result.get("rating_5_tier", "Unknown"),
                        "score": result.get("final_score", 0),
                        "source": "FinResearchCrew",
                    },
                    ttl_days=7,  # Cache valid for 7 days
                )
                print(f"Successfully saved report for {ticker} to ChromaDB.")
            else:
                print(
                    f"Skipping save for {ticker}: Missing final_score (incomplete run)."
                )

        except Exception as e:
            # Don't fail the whole request if saving fails, just log it
            print(f"Warning: Failed to save to ChromaDB: {e}")

        return result

    except Exception as e:
        end_time = datetime.now()
        return {
            "ticker": ticker,
            "error": f"Analysis failed: {str(e)}",
            "error_type": type(e).__name__,
            "execution_info": {
                "execution_time_seconds": round(
                    (end_time - start_time).total_seconds(), 2
                ),
                "status": "error",
            },
        }
