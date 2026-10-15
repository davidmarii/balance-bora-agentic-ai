
import math
import sqlite3
from pathlib import Path
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("Balance Bora Formulation Assessment")

DB_FILE = Path(
    r"C:\Users\Admin\Downloads\Balance_Bora_Feed.db"
)

@mcp.tool()
def assess_formulation_inputs(
    ingredient_names: list[str],
    prices_kes_per_kg: dict[str, float]
) -> dict:
    """Validate ingredient nutrient records and supplied prices
    before a ration formulation is attempted.

    Prices must be provided explicitly by the caller. This tool
    does not assume database nutrient values are prices.
    """

    if not ingredient_names:
        return {
            "status": "invalid_input",
            "message": "Provide at least one ingredient name."
        }

    if not DB_FILE.is_file():
        return {
            "status": "database_missing",
            "message": f"Database not found: {DB_FILE}"
        }

    try:
        conn = sqlite3.connect(
            DB_FILE.resolve().as_uri() + "?mode=ro",
            uri=True
        )
        conn.row_factory = sqlite3.Row

        results = []
        missing_ingredients = []
        invalid_prices = []
        missing_prices = []

        for name in ingredient_names:
            name = name.strip()

            if not name:
                continue

            row = conn.execute(
                """
                SELECT *
                FROM ingredients
                WHERE lower(ingredient_name) = lower(?)
                LIMIT 1
                """,
                (name,)
            ).fetchone()

            if row is None:
                missing_ingredients.append(name)
                continue

            data = dict(row)

            price = prices_kes_per_kg.get(name)

            if price is None:
                # Allow case-insensitive price keys.
                for key, value in prices_kes_per_kg.items():
                    if key.casefold() == name.casefold():
                        price = value
                        break

            if price is None:
                missing_prices.append(name)
            else:
                try:
                    price = float(price)
                    if not math.isfinite(price) or price < 0:
                        raise ValueError
                except (TypeError, ValueError):
                    invalid_prices.append(name)
                    price = None

            nutrient_values = {
                key: data.get(key)
                for key in [
                    "DM", "CP", "ME", "NDF", "ADF",
                    "Ca", "P", "OM", "IVDMD"
                ]
            }

            missing_nutrients = [
                key for key, value in nutrient_values.items()
                if value is None
            ]

            results.append({
                "ingredient": data["ingredient_name"],
                "price_kes_per_kg": price,
                "observation_count": data.get("n"),
                "nutrients": nutrient_values,
                "missing_nutrients": missing_nutrients
            })

        conn.close()

        ready = (
            len(results) == len([
                n for n in ingredient_names if n.strip()
            ])
            and not missing_prices
            and not invalid_prices
            and all(not item["missing_nutrients"] for item in results)
        )

        return {
            "status": "ready_for_solver" if ready else "needs_review",
            "ingredient_count": len(results),
            "ingredients": results,
            "missing_ingredients": missing_ingredients,
            "missing_prices": missing_prices,
            "invalid_prices": invalid_prices,
            "message": (
                "Inputs passed these basic completeness checks. "
                "This does not establish that a ration is nutritionally "
                "adequate or safe."
                if ready else
                "Resolve missing ingredients, prices, or nutrient values "
                "before sending these inputs to the ration solver."
            )
        }

    except (sqlite3.Error, OSError) as exc:
        return {
            "status": "error",
            "message": str(exc)
        }


if __name__ == "__main__":
    mcp.run(transport="stdio")
