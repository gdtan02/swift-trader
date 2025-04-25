endpointsParams = {
    "cryptoquant": {
        "exchange-flows": {
            "reserve": { "exchange": "all_exchange", "window": "hour" },
            "netflow": { "exchange": "all_exchange", "window": "hour" },
            "inflow": { "exchange": "all_exchange", "window": "hour" },
            "outflow": { "exchange": "all_exchange", "window": "hour" },
            "transactions-count": { "exchange": "all_exchange", "window": "hour" },
            "addresses-count": { "exchange": "all_exchange", "window": "hour" }
        },
        "flow-indicator": {
            "mpi": { "window": "day" },
            "exchange-shutdown-index": { "exchange": "all_exchange", "window": "hour" },
            "exchange-whale-ratio": { "exchange": "all_exchange", "window": "hour" },
            "fund-flow-ratio": { "exchange": "all_exchange", "window": "day" },
            "stablecoins-ratio": { "exchange": "all_exchange", "window": "hour" },
            "exchange-supply-ratio": { "exchange": "all_exchange", "window": "hour" },
            "miner-supply-ratio": { "miner": "all_miner", "window": "hour" }
        },
        "market-indicator": {
            "estimated-leverage-ratio": { "exchange": "all_exchange", "window": "hour" },
            "stablecoin-supply-ratio": { "window": "day" },
            "mvrv": { "window": "day" },
            "sopr": { "window": "day" },
            "sopr-ratio": { "window": "day" },     
        },
        "network-indicator": {
            "nvt": { "window": "day" },  # Network Value to Transaction (supply_total * price_usd)
            "nvt-golden-cross": { "window": "day" },
            "nvm": { "window": "day" },  # Network Value to Metcalfe Ratio
            "puell-multiple": { "window": "day" },
            "nupl": { "window": "day" },  # Net Unralized Profit and Loss
            "nrpl": { "window": "day" },  # Net Realized Profit and Loss
        },
        "miner-flows": {
            "reserve": { "miner": "all_miner", "window": "hour" },
            "netflow": { "miner": "all_miner", "window": "hour" },
            "inflow": { "miner": "all_miner", "window": "hour" },
            "outflow": { "miner": "all_miner", "window": "hour" },
            "transactions-count": { "miner": "all_miner", "window": "hour" },
            "addresses-count": { "miner": "all_miner", "window": "hour" }
        },
        "market-data": {
            "price-ohlcv": { "market": "spot", "exchange" : "all_exchange", "window": "hour" },
            "open-interest": { "exchange": "all_exchange", "window": "hour" },
            "taker-buy-sell-stats": { "exchange": "all_exchange", "window": "hour" },
            "liquidations": { "exchange": "all_exchange", "window": "hour" },
            "capitalization": { "window": "day" },
            "coinbase-premium-index": { "window": "hour" }
        },
        "network-data": {
            "transactions-count": { "window": "hour" },
            "addresses-count": { "window": "hour" },
            "tokens-transferred": { "window": "hour" },
            "utxo-count": { "window": "hour" },
            "fees-transaction": { "window": "hour" },
            "blockreward": { "window": "hour" },
            "difficulty": { "window": "hour" }
        }
    },
    "glassnode": {},
    "coinbase": {}
}