import time
import hmac
import hashlib
import logging
import aiohttp


class BybitClient:
    BASE_URL = "https://api.bybit.com"

    def __init__(self, api_key: str | None, api_secret: str | None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.has_keys = bool(api_key and api_secret)

    async def _request(self, method: str, path: str, params: dict | None = None, auth: bool = False):
        url = self.BASE_URL + path
        params = params or {}

        headers = {
            "Content-Type": "application/json",
        }

        if auth:
            if not self.has_keys:
                logging.warning("Richiesta privata Bybit senza API key configurate.")
                return None

            timestamp = str(int(time.time() * 1000))
            recv_window = "5000"

            query = ""
            if method == "GET" and params:
                # Bybit v5 firma il body, non la query, ma per semplicità qui usiamo body vuoto
                pass

            body = ""
            sign_payload = timestamp + self.api_key + recv_window + body
            signature = hmac.new(
                self.api_secret.encode(),
                sign_payload.encode(),
                hashlib.sha256,
            ).hexdigest()

            headers.update(
                {
                    "X-BAPI-API-KEY": self.api_key,
                    "X-BAPI-TIMESTAMP": timestamp,
                    "X-BAPI-RECV-WINDOW": recv_window,
                    "X-BAPI-SIGN": signature,
                }
            )

        try:
            async with aiohttp.ClientSession() as session:
                if method == "GET":
                    async with session.get(url, headers=headers, params=params, timeout=10) as resp:
                        return await resp.json()
                else:
                    async with session.post(url, headers=headers, json=params, timeout=10) as resp:
                        return await resp.json()
        except Exception as e:
            logging.error(f"Errore richiesta Bybit {method} {path}: {e}")
            return None

    async def get_wallet_balance(self):
        """
        Esempio di chiamata privata (semplificata).
        """
        res = await self._request(
            "GET",
            "/v5/account/wallet-balance",
            params={"accountType": "UNIFIED"},
            auth=True,
        )
        if not res or res.get("retCode") != 0:
            logging.error(f"Errore wallet-balance: {res}")
            return None

        # Ritorno un dict {coin: info}
        balances = {}
        for item in res["result"]["list"]:
            for coin in item.get("coin", []):
                balances[coin["coin"]] = coin
        return balances
