from http import HTTPStatus


def test_get_token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_token_invalid_username(client, user):
    response = client.post(
        '/auth/token',
        data={'username': 'not_username', 'password': user.clean_password},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_token_invalid_password(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': 'not-password'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect email or password'}
