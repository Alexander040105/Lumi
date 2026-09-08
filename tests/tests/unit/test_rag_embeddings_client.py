from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from app.services import rag_embeddings_client


@pytest.fixture
def mock_settings():
    with patch('app.services.rag_embeddings_client.get_settings') as settings:
        settings.return_value = MagicMock(
            embedding_provider='huggingface-inference',
            embedding_model='sentence-transformers/all-MiniLM-L6-v2',
            embedding_api_key=None,
            hf_token=None,
            openai_api_key=None,
            embedding_batch_size=32,
        )
        yield settings


@pytest.fixture
def mock_redis_none():
    with patch('app.services.rag_embeddings_client.get_redis_sync', return_value=None):
        yield


def test_encode_single_returns_384d(mock_settings, mock_redis_none):
    embedding = [0.1] * 384
    with patch('app.services.rag_embeddings_client.httpx.Client') as client_class:
        client = client_class.return_value.__enter__.return_value
        client.post.return_value.status_code = 200
        client.post.return_value.json.return_value = [embedding]
        result = rag_embeddings_client.encode('solar panels')

    assert len(result) == 1
    assert len(result[0]) == 384


def test_encode_uses_redis_cache(mock_settings):
    embedding = [0.2] * 384
    redis = MagicMock()
    redis.get.return_value = json.dumps(embedding).encode()

    with patch('app.services.rag_embeddings_client.get_redis_sync', return_value=redis):
        with patch('app.services.rag_embeddings_client.httpx.Client') as client_class:
            result = rag_embeddings_client.encode('wind turbine')

    assert result == [embedding]
    client_class.return_value.__enter__.return_value.post.assert_not_called()


def test_encode_batch(mock_settings, mock_redis_none):
    embeddings = [[0.3] * 384, [0.4] * 384]
    with patch('app.services.rag_embeddings_client.httpx.Client') as client_class:
        client = client_class.return_value.__enter__.return_value
        client.post.return_value.status_code = 200
        client.post.return_value.json.return_value = embeddings
        result = rag_embeddings_client.encode(['solar', 'wind'])

    assert len(result) == 2
    assert [len(e) for e in result] == [384, 384]


def test_encode_openai():
    with patch('app.services.rag_embeddings_client.get_settings') as settings:
        settings.return_value = MagicMock(
            embedding_provider='openai',
            embedding_model='text-embedding-3-small',
            embedding_api_key='sk-test',
            hf_token=None,
            openai_api_key=None,
            embedding_batch_size=32,
        )
        with patch('app.services.rag_embeddings_client.httpx.Client') as client_class:
            client = client_class.return_value.__enter__.return_value
            client.post.return_value.status_code = 200
            client.post.return_value.json.return_value = {'data': [{'embedding': [0.5] * 1536}]}
            with patch('app.services.rag_embeddings_client.get_redis_sync', return_value=None):
                result = rag_embeddings_client.encode('hydropower')

    assert len(result) == 1
    assert len(result[0]) == 1536


def test_unsupported_provider(mock_settings, mock_redis_none):
    mock_settings.return_value.embedding_provider = 'unknown'
    with pytest.raises(ValueError):
        rag_embeddings_client.encode('solar')
