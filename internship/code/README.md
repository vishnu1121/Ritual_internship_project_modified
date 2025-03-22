# StakingOptimizer Agent 🥩

A character-driven Web3 agent that helps users optimize their staking positions using scheduled transactions. Built with LangChain and Next.js.

## Features

### Character-Driven Interface
- **Stake Mate**: Your friendly staking expert who speaks in crypto Twitter culture
- **Natural Language**: Interact with the agent using everyday language
- **Meme Culture**: Responses include emojis and common crypto phrases

### Staking Operations
- Basic ETH staking
- Scheduled transactions
- Auto-compound rewards
- Gas optimization
- Transaction safety checks

### Frontend Components
1. **StakingCard**: Traditional UI for staking operations
   - View staking positions
   - Stake/unstake tokens
   - Monitor rewards
   - Schedule transactions

2. **StakingAgent**: Chat interface with Stake Mate
   - Natural language interactions
   - Real-time responses
   - Transaction suggestions
   - Gas optimization tips

## Architecture

### Frontend (Next.js + TypeScript)
- `/frontend/src/components/staking/`
  - `StakingCard.tsx`: Traditional staking interface
  - `StakingAgent.tsx`: Chat-based agent interface
- `/frontend/src/services/`
  - `staking.ts`: API client for staking operations

### Backend (FastAPI + LangChain)
- `/src/staking_optimizer/`
  - `agent/`: LangChain agent implementation
  - `api/`: FastAPI endpoints
  - `blockchain/`: Mock blockchain implementation
  - `character/`: Stake Mate personality

## Getting Started

1. Install Dependencies:
```bash
# Backend

python3.12 -m venv .venv
source .venv/bin/activate

pip install -e langchain-ritual-toolkit
pip install -e .

# Frontend
cd frontend
npm install
```

2. Set Environment Variables:
```bash
# Backend (.env)
# !important, use an openrouter key
OPENAI_API_KEY=YOUR_OPENROUTER_KEY

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Run the Application:
```bash
# Backend
cd src
uvicorn staking_optimizer.api.main:app --reload

# Alternatively with Docker
docker-compose up -d

# Frontend
cd frontend
npm run dev
```

4. Visit http://localhost:3000 to interact with Stake Mate!

## API Endpoints

### POST /api/v1/chat
Natural language interface for all staking operations.

Request:
```json
{
  "message": "I want to stake 1 ETH"
}
```

Response:
```json
{
  "success": true,
  "response": "gm fren! 🚀 Let's get that ETH staked for you...",
  "data": {
    "stakedAmount": "1.0",
    "rewards": "0.0",
    "gasSavings": "0.002",
    "nextRewardDate": "2024-02-18T14:30:00Z"
  }
}
```

## Development

### Adding New Features
1. Implement the feature in the mock blockchain
2. Add corresponding agent tools
3. Update the frontend components
4. Add tests

### Testing
```bash
# Backend
pip install -e ".[test,dev]"
pytest

# Frontend
npm test
```

## Security

- All transactions are simulated before execution
- Gas optimization checks
- Balance verification
- Clear user confirmations

## Future Enhancements

1. **Protocol Extensions**
   - ERC20 token support
   - Variable reward rates
   - Governance features

2. **Agent Capabilities**
   - Multi-protocol support
   - Portfolio analytics
   - Risk assessment

3. **Frontend Features**
   - Mobile optimization
   - Dark mode
   - Transaction history

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

The Clear BSD License

Copyright (c) 2023 Origin Research Ltd
All rights reserved.