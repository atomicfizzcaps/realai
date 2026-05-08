"""EVM backend with read and write support."""

from typing import Any, Dict

try:
    from web3 import Web3
except ImportError:  # pragma: no cover
    Web3 = None


def _to_jsonable(value: Any):
    if isinstance(value, (bytes, bytearray)):
        return value.hex()
    if hasattr(value, "hex") and callable(value.hex):
        try:
            return value.hex()
        except Exception:
            return value
    if isinstance(value, dict):
        return {key: _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(item) for item in value]
    return value


class EVMBackend:
    name = "evm"

    def __init__(self, rpc_url: str, private_key: str = None):
        if Web3 is None:
            raise RuntimeError("web3 dependency is unavailable for EVM backend")
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.private_key = private_key

    def get_account(self, address: str) -> Dict[str, Any]:
        return {
            "balance": int(self.w3.eth.get_balance(address)),
            "nonce": int(self.w3.eth.get_transaction_count(address)),
        }

    def simulate(self, tx: Dict[str, Any]) -> Dict[str, Any]:
        return {"result": _to_jsonable(self.w3.eth.call(tx))}

    def send(self, tx: Dict[str, Any]) -> Dict[str, Any]:
        private_key = tx.get("private_key") or self.private_key
        if not private_key:
            raise ValueError("private_key is required to send EVM transactions")
        tx_payload = dict(tx)
        tx_payload.pop("private_key", None)
        tx_payload.pop("approved", None)
        signed = self.w3.eth.account.sign_transaction(tx_payload, private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        return {"tx_hash": _to_jsonable(tx_hash)}

    def call(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        target = getattr(self.w3.eth, method)
        if isinstance(params, dict):
            args = params.get("args", [])
            kwargs = params.get("kwargs", {})
            return {"result": _to_jsonable(target(*args, **kwargs))}
        if isinstance(params, list):
            return {"result": _to_jsonable(target(*params))}
        return {"result": _to_jsonable(target(params))}

