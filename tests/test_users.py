from http import HTTPStatus

from fast_zero.schemas import UserPublic


def test_creat_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'testusername',
            'password': 'password',
            'email': 'test@test.com',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'testusername',
        'email': 'test@test.com',
        'id': 1,
    }


def test_read_users(client):
    response = client.get('/users')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_with_users(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')
    assert response.json() == {'users': [user_schema]}


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'bob',
        'email': 'bob@example.com',
        'id': user.id,
    }


def test_update_integrity_error(client, user, other_user, token):
    response_update = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': other_user.username,
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )
    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        'detail': 'Username or Email already exists'
    }


def test_update_user_with_wrong_user(client, other_user, token):
    response = client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_exerc_get_user_found(client, other_user):
    response = client.get(
        f'/users/{other_user.id}',
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': other_user.username,
        'email': other_user.email,
        'id': other_user.id,
    }


def test_delete_user_wrong_user(client, other_user, token):
    response = client.delete(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_exerc_get_user_not_found(client):
    response = client.get('/users/2')
    assert response.json() == {'detail': 'User not found'}


def test_exerc_post_already_exist_username(client, user):
    response_create = client.post(
        '/users/',
        json={
            'username': user.username,
            'email': 'teste2@test.com',
            'password': 'mynewpassword',
        },
    )
    assert response_create.status_code == HTTPStatus.BAD_REQUEST
    assert response_create.json() == {'detail': 'Username already exists'}


def test_exerc_post_already_exist_email(client, user):
    response_create = client.post(
        '/users/',
        json={
            'username': 'Teste2',
            'email': user.email,
            'password': 'mynewpassword',
        },
    )
    assert response_create.status_code == HTTPStatus.BAD_REQUEST
    assert response_create.json() == {'detail': 'Email already exists'}
