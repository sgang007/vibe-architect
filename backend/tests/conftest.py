"""Shared fixtures for all tests."""
import pytest
import asyncio
from uuid import uuid4
from app.models import SessionContext, EnrichmentPhase
from app.core.enrichment.adapters.mock import MockLLMAdapter


@pytest.fixture
def mock_adapter():
    return MockLLMAdapter()


@pytest.fixture
def fresh_session():
    session = SessionContext()
    session.phase = EnrichmentPhase.IDEA
    return session


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
