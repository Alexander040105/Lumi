from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.services import rag_pgvector_store


@pytest.fixture
def mock_settings():
    with patch('app.services.rag_pgvector_store.get_settings') as settings:
        settings.return_value = MagicMock(
            embedding_model='sentence-transformers/all-MiniLM-L6-v2',
            rag_pgvector_table='rag_chunks',
            rag_pgvector_rpc='match_rag_chunks',
        )
        yield settings


@pytest.fixture
def mock_client():
    client = MagicMock()
    with patch('app.services.rag_pgvector_store.get_supabase_client', return_value=client):
        yield client


@pytest.fixture
def mock_embeddings():
    with patch('app.services.rag_pgvector_store.encode') as encode:
        encode.return_value = [[0.1] * 384]
        yield encode


def test_retrieve_context_shape(mock_settings, mock_client, mock_embeddings):
    mock_client.rpc.return_value.execute.return_value.data = [
        {
            'id': 1,
            'chunk_text': 'solar panels in the Philippines',
            'renewable_type': 'solar',
            'category': 'equipment_cost',
            'product_type': 'panel',
            'sources': [{'title': 'Alibaba', 'url': 'https://alibaba.com'}],
            'similarity': 0.85,
        }
    ]
    results = rag_pgvector_store.retrieve_context('solar panels', top_k=5)

    assert len(results) == 1
    assert results[0]['text'] == 'solar panels in the Philippines'
    assert results[0]['score'] == 0.85
    assert results[0]['renewable_type'] == 'solar'
    assert isinstance(results[0]['sources'], list)


def test_retrieve_with_filter_passes_params(mock_settings, mock_client, mock_embeddings):
    mock_client.rpc.return_value.execute.return_value.data = []
    rag_pgvector_store.retrieve_with_filter(
        'solar budget',
        top_k=3,
        renewable_type='solar',
        category='equipment_cost',
    )
    call_args = mock_client.rpc.call_args
    assert call_args[0][0] == 'match_rag_chunks'
    params = call_args[0][1]
    assert params['filter_renewable_type'] == 'solar'
    assert params['filter_category'] == 'equipment_cost'
    assert params['match_count'] == 3


def test_index_stats_count(mock_settings, mock_client):
    resp = MagicMock()
    resp.count = 123
    mock_client.table.return_value.select.return_value.limit.return_value.execute.return_value = resp

    stats = rag_pgvector_store.index_stats()

    assert stats['chunks_loaded'] == 123
    assert stats['index_present'] is True


def test_ensure_index_built_empty(mock_settings, mock_client):
    mock_client.table.return_value.select.return_value.limit.return_value.execute.return_value.data = []

    assert rag_pgvector_store.ensure_index_built() is False


def test_ensure_index_built_ready(mock_settings, mock_client):
    mock_client.table.return_value.select.return_value.limit.return_value.execute.return_value.data = [{'id': 1}]

    assert rag_pgvector_store.ensure_index_built() is True
