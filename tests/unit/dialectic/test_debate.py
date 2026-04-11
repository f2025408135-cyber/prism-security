"""Tests for the LLM dialectic engine."""

import pytest
import asyncio
from unittest.mock import AsyncMock

from prism.dialectic.models import DialecticModelRouter
from prism.dialectic.attacker import AttackerAgent
from prism.dialectic.defender import DefenderAgent
from prism.dialectic.debate import DebateManager

@pytest.fixture
def mock_router() -> DialecticModelRouter:
    router = DialecticModelRouter()
    # Mock the internal LLM call to avoid hitting real APIs
    router._call_llm = AsyncMock()  # type: ignore
    return router

@pytest.mark.asyncio
async def test_attacker_agent_argues(mock_router: DialecticModelRouter) -> None:
    """Test the attacker formats context properly."""
    mock_router._call_llm.return_value = "Attacker test response"
    
    agent = AttackerAgent(mock_router)
    resp = await agent.argue("evidence data", "history data")
    
    assert resp == "Attacker test response"
    mock_router._call_llm.assert_called_once()

@pytest.mark.asyncio
async def test_defender_agent_argues(mock_router: DialecticModelRouter) -> None:
    """Test the defender formats context properly."""
    mock_router._call_llm.return_value = "Defender test response"
    
    agent = DefenderAgent(mock_router)
    resp = await agent.argue("evidence data", "history data")
    
    assert resp == "Defender test response"
    mock_router._call_llm.assert_called_once()

@pytest.mark.asyncio
async def test_debate_loop_attacker_concedes(mock_router: DialecticModelRouter) -> None:
    """Test the debate loop terminates early if attacker concedes."""
    attacker = AttackerAgent(mock_router)
    defender = DefenderAgent(mock_router)
    
    # We mock the specific get_response methods to control the debate
    mock_router.get_attacker_response = AsyncMock(return_value="I am wrong. CONCEDE: FALSE POSITIVE")
    mock_router.get_defender_response = AsyncMock() # Should never be called
    
    manager = DebateManager(attacker, defender)
    
    transcript = await manager.conduct_debate("f_1", "evidence")
    
    assert transcript.finding_id == "f_1"
    assert transcript.final_verdict == "DEFENDER_WINS_FALSE_POSITIVE"
    assert len(transcript.rounds) == 1
    assert "CONCEDE" in transcript.rounds[0]["attacker"]
    
    mock_router.get_defender_response.assert_not_called()

@pytest.mark.asyncio
async def test_debate_loop_defender_concedes(mock_router: DialecticModelRouter) -> None:
    """Test the debate loop terminates early if defender concedes."""
    attacker = AttackerAgent(mock_router)
    defender = DefenderAgent(mock_router)
    
    mock_router.get_attacker_response = AsyncMock(return_value="Here is the proof.")
    mock_router.get_defender_response = AsyncMock(return_value="You are right. CONCEDE: TRUE POSITIVE")
    
    manager = DebateManager(attacker, defender)
    
    transcript = await manager.conduct_debate("f_2", "evidence")
    
    assert transcript.finding_id == "f_2"
    assert transcript.final_verdict == "ATTACKER_WINS_TRUE_POSITIVE"
    assert len(transcript.rounds) == 1
    assert "proof" in transcript.rounds[0]["attacker"]
    assert "CONCEDE" in transcript.rounds[0]["defender"]

@pytest.mark.asyncio
async def test_debate_loop_stalemate(mock_router: DialecticModelRouter) -> None:
    """Test the debate loop goes to MAX_ROUNDS and stalemates if no one concedes."""
    attacker = AttackerAgent(mock_router)
    defender = DefenderAgent(mock_router)
    
    mock_router.get_attacker_response = AsyncMock(return_value="It's a bug.")
    mock_router.get_defender_response = AsyncMock(return_value="No it's not.")
    
    manager = DebateManager(attacker, defender)
    
    transcript = await manager.conduct_debate("f_3", "evidence")
    
    assert transcript.final_verdict == "STALEMATE"
    assert len(transcript.rounds) == 5
    assert mock_router.get_attacker_response.call_count == 5
    assert mock_router.get_defender_response.call_count == 5
