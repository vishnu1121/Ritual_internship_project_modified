"""API for interacting with Ritual network."""

from typing import Any
import logging

from web3 import Web3

from langchain_ritual_toolkit.configuration import RitualConfig

logger = logging.getLogger(__name__)


class RitualAPI:
    def __init__(self, private_key: str, rpc_url: str, ritual_config: RitualConfig):
        super().__init__()
        self.private_key = private_key
        self.rpc_url = rpc_url
        self.ritual_config = ritual_config
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = self.web3.eth.account.from_key(self.private_key)

    def _send_transaction(self, transaction):
        logger.info(f"Sending transaction: {transaction}")
        signed_txn = self.web3.eth.account.sign_transaction(
            transaction, self.private_key
        )
        return self.web3.eth.send_raw_transaction(signed_txn.raw_transaction)

    def _send_scheduled_transaction(self, **kwargs):
        logger.info(f"Scheduling transaction with kwargs: {kwargs}")
        contract = self.web3.eth.contract(
            address=self.ritual_config.contract_address,
            abi=self.ritual_config.raw_abi,
        )
        # Get the function from the contract using the schedule_fn name
        contract_function = getattr(contract.functions, self.ritual_config.schedule_fn)
        
        # Calculate the fee based on gas parameters
        fee = int(
            kwargs["gasLimit"]
            * (kwargs["gasPrice"] * (kwargs["numBlocks"] / kwargs["frequency"]))
        )
        
        # Build the transaction with the provided kwargs and fee as value
        transaction = contract_function(**kwargs).build_transaction(
            {
                "from": self.account.address,
                "nonce": self.web3.eth.get_transaction_count(self.account.address),
                "value": fee,
            }
        )
        tx_hash = self._send_transaction(transaction)
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        assert receipt.status == 1
        return tx_hash

    def _send_cancel_scheduled_transaction(self, **kwargs):
        logger.info(f"Canceling transaction with kwargs: {kwargs}")
        contract = self.web3.eth.contract(
            address=self.ritual_config.contract_address,
            abi=self.ritual_config.raw_abi,
        )

        # Get the function from the contract using the cancel_fn name
        contract_function = getattr(contract.functions, self.ritual_config.cancel_fn)

        # Build the transaction with the provided kwargs
        transaction = contract_function(**kwargs).build_transaction(
            {
                "from": self.account.address,
                "nonce": self.web3.eth.get_transaction_count(self.account.address),
            }
        )

        # Send the transaction using the existing _send_transaction method
        tx_hash = self._send_transaction(transaction)
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        assert receipt.status == 1
        return tx_hash

    def run(self, method: str, *args: Any, **kwargs: Any) -> str:
        if method == "schedule_transaction":
            tx_hash = self._send_scheduled_transaction(**kwargs)
            return f"Schedule transaction successful. Transaction hash: 0x{tx_hash.hex()}"

        elif method == "cancel_scheduled_transaction":
            tx_hash = self._send_cancel_scheduled_transaction(**kwargs)
            return f"Cancel transaction successful. Transaction hash: 0x{tx_hash.hex()}"
        else:
            raise ValueError(f"Unknown method: {method}")
