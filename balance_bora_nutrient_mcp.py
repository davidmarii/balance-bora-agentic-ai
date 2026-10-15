
import os
import sqlite3
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Balance Bora Nutrient Server")

DB_FILE = Path(
    os.environ.get(
        "BALANCE_BORA_DB",
        str(Path(__file__).with_name("Balance_Bora_Feed.db"))
    )
)

NUTRIENTS = {
    "DM": "Dry matter",
    "ADF": "Acid detergent fibre",
    "NDF": "Neutral detergent fibre",
    "ADL": "Acid detergent lignin",
    "CP": "Crude protein",
    "OM": "Organic matter",
    "P": "Phosphorus",
    "Ca": "Calcium",
    "Na": "Sodium",
    "Fe": "Iron",
    "K": "Potassium",
    "Mg": "Magnesium",
    "Cu": "Copper",
    "Mn": "Manganese",
    "Zn": "Zinc",
    "IVDMD": "In-vitro dry matter digestibility",
    "ME": "Metabolizable energy",
    "NEm": "Net energy for maintenance",
    "NEg": "Net energy for gain",
    "NEl": "Net energy for lactation",
}


def connect_readonly():
    if not DB_FILE.is_file():
        raise FileNotFoundError(f"Database not found: {DB_FILE}")

    uri = DB_FILE.resolve().as_uri() + "?mode=ro"
    return sqlite3.connect(uri, uri=True)


@mcp.tool()
def lookup_feed_nutrients(
    ingredient_name: str,
    include_ranges: bool = False
) -> dict:
    """Search Balance Bora's SQLite feed database for ingredient
    nutrient values. Optionally include summary ranges and variation.
    Returns recorded values only; does not estimate missing nutrients.
    """

    if not ingredient_name.strip():
        return {
            "status": "invalid_input",
            "message": "Enter an ingredient name."
        }

    try:
        with connect_readonly() as conn:
            conn.row_factory = sqlite3.Row

            # Exact matches first, then partial name matches.
            rows = conn.execute(
                """
                SELECT *
                FROM ingredients
                WHERE lower(ingredient_name) = lower(?)
                   OR lower(ingredient_name) LIKE lower(?)
                ORDER BY
                    CASE WHEN lower(ingredient_name) = lower(?)
                         THEN 0 ELSE 1 END,
                    ingredient_name
                LIMIT 10
                """,
                (
                    ingredient_name.strip(),
                    "%" + ingredient_name.strip() + "%",
                    ingredient_name.strip()
                )
            ).fetchall()

            if not rows:
                return {
                    "status": "not_found",
                    "query": ingredient_name,
                    "message": "No matching ingredient found."
                }

            results = []

            for row in rows:
                item = dict(row)
                nutrients = {}

                for code, label in NUTRIENTS.items():
                    value = item.get(code)
                    nutrients[code] = {
                        "name": label,
                        "value": value
                    }

                result = {
                    "ingredient": item["ingredient_name"],
                    "observation_count": item.get("n"),
                    "nutrients": nutrients,
                    "data_source": "ingredients table"
                }

                if include_ranges:
                    summary = conn.execute(
                        """
                        SELECT *
                        FROM ingredient_summary
                        WHERE lower(ingredient_name) = lower(?)
                        LIMIT 1
                        """,
                        (item["ingredient_name"],)
                    ).fetchone()

                    if summary:
                        summary = dict(summary)
                        result["summary"] = {
                            "mean": {
                                code: summary.get(code)
                                for code in NUTRIENTS
                            },
                            "standard_deviation": {
                                code: summary.get(code + "_SD")
                                for code in NUTRIENTS
                            },
                            "minimum": {
                                code: summary.get(code + "_MIN")
                                for code in NUTRIENTS
                            },
                            "maximum": {
                                code: summary.get(code + "_MAX")
                                for code in NUTRIENTS
                            }
                        }

                results.append(result)

            return {
                "status": "ok",
                "query": ingredient_name,
                "count": len(results),
                "results": results,
                "note": (
                    "Values and units follow the source database. "
                    "Confirm units and analytical basis before ration use. "
                    "Null values mean no value is recorded."
                )
            }

    except (sqlite3.Error, OSError) as exc:
        return {
            "status": "database_error",
            "message": str(exc)
        }


if __name__ == "__main__":
    mcp.run(transport="stdio")
