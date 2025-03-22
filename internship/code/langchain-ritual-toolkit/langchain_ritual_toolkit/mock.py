"""Mock API for testing without blockchain."""

import uuid
from typing import Any


# Mock config
MockConfig: dict = {
    "contract_address": "0xa53C1aEf5a19d82037Fe7E54A3CBAa852f808E21",
    "abi": [
        {
            "type": "constructor",
            "inputs": [
                {
                    "name": "_scheduler",
                    "type": "address",
                    "internalType": "contract Scheduler"
                }
            ],
            "stateMutability": "nonpayable"
        },
        {
            "type": "fallback",
            "stateMutability": "payable"
        },
        {
            "type": "receive",
            "stateMutability": "payable"
        },
        {
            "type": "function",
            "name": "NETWORK_REQUEST",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "address",
                    "internalType": "address"
                }
            ],
            "stateMutability": "view"
        },
        {
            "type": "function",
            "name": "REGISTER_SECRET",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "address",
                    "internalType": "address"
                }
            ],
            "stateMutability": "view"
        },
        {
            "type": "function",
            "name": "cancelCallback",
            "inputs": [
                {
                    "name": "id",
                    "type": "uint256",
                    "internalType": "uint256"
                }
            ],
            "outputs": [],
            "stateMutability": "nonpayable"
        },
        {
            "type": "function",
            "name": "cancelJob",
            "inputs": [
                {
                    "name": "jobId",
                    "type": "string",
                    "internalType": "string"
                }
            ],
            "outputs": [],
            "stateMutability": "nonpayable"
        },
        {
            "type": "function",
            "name": "genericComputeCallback",
            "inputs": [
                {
                    "name": "jobId",
                    "type": "string",
                    "internalType": "string"
                },
                {
                    "name": "target",
                    "type": "address",
                    "internalType": "address"
                },
                {
                    "name": "inputs",
                    "type": "bytes",
                    "internalType": "bytes"
                }
            ],
            "outputs": [],
            "stateMutability": "nonpayable"
        },
        {
            "type": "function",
            "name": "getComputeOutputs",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "string[]",
                    "internalType": "string[]"
                }
            ],
            "stateMutability": "view"
        },
        {
            "type": "function",
            "name": "getJobOutput",
            "inputs": [
                {
                    "name": "jobId",
                    "type": "string",
                    "internalType": "string"
                }
            ],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes[]",
                    "internalType": "bytes[]"
                }
            ],
            "stateMutability": "view"
        },
        {
            "type": "function",
            "name": "getScheduledJobs",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "string[]",
                    "internalType": "string[]"
                }
            ],
            "stateMutability": "view"
        },
        {
            "type": "function",
            "name": "jobIdToCallId",
            "inputs": [
                {
                    "name": "",
                    "type": "string",
                    "internalType": "string"
                }
            ],
            "outputs": [
                {
                    "name": "",
                    "type": "uint256",
                    "internalType": "uint256"
                }
            ],
            "stateMutability": "view"
        },
        {
            "type": "function",
            "name": "jobIds",
            "inputs": [
                {
                    "name": "",
                    "type": "uint256",
                    "internalType": "uint256"
                }
            ],
            "outputs": [
                {
                    "name": "",
                    "type": "string",
                    "internalType": "string"
                }
            ],
            "stateMutability": "view"
        },
        {
            "type": "function",
            "name": "normalComputeCallback",
            "inputs": [
                {
                    "name": "jobId",
                    "type": "string",
                    "internalType": "string"
                }
            ],
            "outputs": [],
            "stateMutability": "nonpayable"
        },
        {
            "type": "function",
            "name": "receivedBlocks",
            "inputs": [
                {
                    "name": "",
                    "type": "string",
                    "internalType": "string"
                },
                {
                    "name": "",
                    "type": "uint256",
                    "internalType": "uint256"
                }
            ],
            "outputs": [
                {
                    "name": "",
                    "type": "uint256",
                    "internalType": "uint256"
                }
            ],
            "stateMutability": "view"
        },
        {
            "type": "function",
            "name": "receivedOutputs",
            "inputs": [
                {
                    "name": "",
                    "type": "string",
                    "internalType": "string"
                },
                {
                    "name": "",
                    "type": "uint256",
                    "internalType": "uint256"
                }
            ],
            "outputs": [
                {
                    "name": "",
                    "type": "bytes",
                    "internalType": "bytes"
                }
            ],
            "stateMutability": "view"
        },
        {
            "type": "function",
            "name": "scheduleCompute",
            "inputs": [
                {
                    "name": "jobId",
                    "type": "string",
                    "internalType": "string"
                },
                {
                    "name": "sidecarId",
                    "type": "uint8",
                    "internalType": "uint8"
                },
                {
                    "name": "inputs",
                    "type": "bytes",
                    "internalType": "bytes"
                },
                {
                    "name": "privateInputs",
                    "type": "tuple[]",
                    "internalType": "struct ScheduleConsumer.PrivateInput[]",
                    "components": [
                        {
                            "name": "name",
                            "type": "string",
                            "internalType": "string"
                        },
                        {
                            "name": "encryptions",
                            "type": "tuple[]",
                            "internalType": "struct ScheduleConsumer.Encryption[]",
                            "components": [
                                {
                                    "name": "recipient",
                                    "type": "string",
                                    "internalType": "string"
                                },
                                {
                                    "name": "encrypted_value",
                                    "type": "string",
                                    "internalType": "string"
                                }
                            ]
                        }
                    ]
                },
                {
                    "name": "gasLimit",
                    "type": "uint32",
                    "internalType": "uint32"
                },
                {
                    "name": "gasPrice",
                    "type": "uint48",
                    "internalType": "uint48"
                },
                {
                    "name": "frequency",
                    "type": "uint32",
                    "internalType": "uint32"
                },
                {
                    "name": "numBlocks",
                    "type": "uint32",
                    "internalType": "uint32"
                }
            ],
            "outputs": [],
            "stateMutability": "payable"
        },
        {
            "type": "function",
            "name": "scheduleGenericCompute",
            "inputs": [
                {
                    "name": "jobId",
                    "type": "string",
                    "internalType": "string"
                },
                {
                    "name": "target",
                    "type": "address",
                    "internalType": "address"
                },
                {
                    "name": "inputs",
                    "type": "bytes",
                    "internalType": "bytes"
                },
                {
                    "name": "gasLimit",
                    "type": "uint32",
                    "internalType": "uint32"
                },
                {
                    "name": "gasPrice",
                    "type": "uint48",
                    "internalType": "uint48"
                },
                {
                    "name": "frequency",
                    "type": "uint32",
                    "internalType": "uint32"
                },
                {
                    "name": "numBlocks",
                    "type": "uint32",
                    "internalType": "uint32"
                }
            ],
            "outputs": [],
            "stateMutability": "payable"
        },
        {
            "type": "function",
            "name": "scheduleNormal",
            "inputs": [
                {
                    "name": "jobId",
                    "type": "string",
                    "internalType": "string"
                },
                {
                    "name": "gasLimit",
                    "type": "uint32",
                    "internalType": "uint32"
                },
                {
                    "name": "gasPrice",
                    "type": "uint48",
                    "internalType": "uint48"
                },
                {
                    "name": "frequency",
                    "type": "uint32",
                    "internalType": "uint32"
                },
                {
                    "name": "numBlocks",
                    "type": "uint32",
                    "internalType": "uint32"
                }
            ],
            "outputs": [],
            "stateMutability": "payable"
        },
        {
            "type": "function",
            "name": "scheduledComputeCallback",
            "inputs": [
                {
                    "name": "jobId",
                    "type": "string",
                    "internalType": "string"
                },
                {
                    "name": "sidecarId",
                    "type": "uint8",
                    "internalType": "uint8"
                },
                {
                    "name": "inputs",
                    "type": "bytes",
                    "internalType": "bytes"
                },
                {
                    "name": "privateInputs",
                    "type": "tuple[]",
                    "internalType": "struct ScheduleConsumer.PrivateInput[]",
                    "components": [
                        {
                            "name": "name",
                            "type": "string",
                            "internalType": "string"
                        },
                        {
                            "name": "encryptions",
                            "type": "tuple[]",
                            "internalType": "struct ScheduleConsumer.Encryption[]",
                            "components": [
                                {
                                    "name": "recipient",
                                    "type": "string",
                                    "internalType": "string"
                                },
                                {
                                    "name": "encrypted_value",
                                    "type": "string",
                                    "internalType": "string"
                                }
                            ]
                        }
                    ]
                },
                {
                    "name": "deadline",
                    "type": "uint32",
                    "internalType": "uint32"
                }
            ],
            "outputs": [],
            "stateMutability": "nonpayable"
        },
        {
            "type": "function",
            "name": "scheduler",
            "inputs": [],
            "outputs": [
                {
                    "name": "",
                    "type": "address",
                    "internalType": "contract Scheduler"
                }
            ],
            "stateMutability": "view"
        },
        {
            "type": "event",
            "name": "ScheduledJobCreated",
            "inputs": [
                {
                    "name": "jobid",
                    "type": "string",
                    "indexed": False,
                    "internalType": "string"
                },
                {
                    "name": "callId",
                    "type": "uint256",
                    "indexed": False,
                    "internalType": "uint256"
                }
            ],
            "anonymous": False
        }
    ],
    "schedule_fn": "scheduleNormal",
    "cancel_fn": "cancelJob"
}


class MockRitualAPI:
    """Mock implementation of RitualAPI for testing.
    
    This class mimics the behavior of RitualAPI without making actual
    blockchain calls. It's useful for testing and development.
    """
    
    def __init__(self):
        """Initialize mock API."""
        self.scheduled_jobs = {}
        
    def _send_scheduled_transaction(self, **kwargs):
        """Mock scheduling a transaction.
        
        Args:
            **kwargs: Transaction parameters including jobId
            
        Returns:
            str: Mock transaction hash
        """
        job_id = kwargs.get("jobId")
        self.scheduled_jobs[job_id] = kwargs
        return uuid.uuid4().hex
        
    def _send_cancel_scheduled_transaction(self, **kwargs):
        """Mock canceling a scheduled transaction.
        
        Args:
            **kwargs: Transaction parameters including jobId
            
        Returns:
            str: Mock transaction hash
            
        Raises:
            ValueError: If job_id doesn't exist
        """
        job_id = kwargs.get("jobId")
        if job_id not in self.scheduled_jobs:
            raise ValueError(f"No scheduled job found with id {job_id}")
            
        del self.scheduled_jobs[job_id]
        return uuid.uuid4().hex
        
    def run(self, method: str, *args: Any, **kwargs: Any) -> str:
        """Run a mock operation.
        
        Args:
            method: Operation to perform
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            str: Operation result message
            
        Raises:
            ValueError: If method is unknown
        """
        if method == "schedule_transaction":
            tx_hash = self._send_scheduled_transaction(**kwargs)
            return f"Mock schedule transaction successful. Transaction hash: 0x{tx_hash}"
            
        elif method == "cancel_scheduled_transaction":
            tx_hash = self._send_cancel_scheduled_transaction(**kwargs)
            return f"Mock cancel transaction successful. Transaction hash: 0x{tx_hash}"
            
        else:
            raise ValueError(f"Unknown method: {method}")
