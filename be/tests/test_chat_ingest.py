def test_ingestion_endpoints(client):
    title_response = client.post(
        '/api/ingest/titles',
        json={'name': 'Ingested Title', 'description': 'demo'},
    )
    assert title_response.status_code == 201
    title_payload = title_response.json()

    episode_response = client.post(
        '/api/ingest/episodes',
        json={
            'title_id': title_payload['id'],
            'season': 1,
            'episode_number': 1,
            'name': 'Ep1',
            'duration_ms': 100000,
        },
    )
    assert episode_response.status_code == 201
    episode_payload = episode_response.json()

    lines_response = client.post(
        '/api/ingest/subtitle-lines:bulk',
        json={
            'lines': [
                {
                    'episode_id': episode_payload['id'],
                    'start_ms': 1000,
                    'end_ms': 1200,
                    'text': 'hello',
                    'speaker_text': 'A',
                }
            ]
        },
    )
    assert lines_response.status_code == 202
    assert lines_response.json()['inserted_count'] == 1


def test_chat_session_endpoints(client, ids):
    signup_response = client.post(
        '/api/auth/signup',
        json={
            'name': 'Chat User',
            'email': 'chat-user@example.com',
            'password': 'secure-pass-123',
        },
    )
    user_id = signup_response.json()['user']['id']

    session_response = client.post(
        '/api/chat/sessions',
        json={
            'title_id': ids['title_id'],
            'episode_id': ids['episode_id'],
            'user_id': user_id,
            'current_time_ms': 1200,
            'meta': {'source': 'test'},
        },
    )
    assert session_response.status_code == 201
    session_id = session_response.json()['id']

    message_response = client.post(
        f'/api/chat/sessions/{session_id}/messages',
        json={
            'role': 'user',
            'content': 'what happened?',
            'current_time_ms': 1200,
        },
    )
    assert message_response.status_code == 201

    list_response = client.get(f'/api/chat/sessions/{session_id}/messages')
    assert list_response.status_code == 200
    assert list_response.json()['session_id'] == session_id
    assert len(list_response.json()['items']) == 1

