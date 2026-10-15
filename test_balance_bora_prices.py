
import importlib.util
from pathlib import Path

base = Path(__file__).resolve().parent
server_file = base / "balance_bora_price_mcp.py"

spec = importlib.util.spec_from_file_location(
    "balance_bora_price_mcp", server_file
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

result = module.lookup_feed_prices(
    ingredient_name="maize bran"
)

print("Status:", result.get("status"))
print("Number of matching prices:", result.get("count", 0))

for price in result.get("prices", []):
    print(price)
