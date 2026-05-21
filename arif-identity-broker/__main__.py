"""arif-identity-broker entry point. Run as: python -m arif_identity_broker.broker"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from broker import main as broker_main

if __name__ == "__main__":
    asyncio.run(broker_main())
