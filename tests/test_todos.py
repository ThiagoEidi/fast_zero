from http import HTTPStatus

import factory.fuzzy
import pytest

from fast_zero.models import Todo, TodoState


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


def test_create_todo_endpoint(client, token, mock_db_time):
    with mock_db_time(model=Todo) as time:
        response = client.post(
            '/todos/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Todo1',
                'description': 'Todo description',
                'state': 'draft',
            },
        )
    assert response.json() == {
        'id': 1,
        'title': 'Todo1',
        'description': 'Todo description',
        'state': 'draft',
        'created_at': time.isoformat(),
        'updated_at': time.isoformat(),
    }


def test_create_todo_endpoint_not_authorization(client, token):
    response = client.post(
        '/todos/',
        json={
            'title': 'Test todo',
            'description': 'Test todo description',
            'state': 'draft',
        },
    )
    assert response.json() == {'detail': 'Not authenticated'}


@pytest.mark.asyncio
async def test_list_todos_filter_combined_should_return_5_todos(
    session, user, client, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            5,
            user_id=user.id,
            title='Test todo combined',
            description='combined description',
            state=TodoState.done,
        )
    )

    session.add_all(
        TodoFactory.create_batch(
            3,
            user_id=user.id,
            title='Other title',
            description='other description',
            state=TodoState.todo,
        )
    )
    await session.commit()

    response = client.get(
        '/todos/?title=Test todo combined&description=combined&state=done',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_with_pagination(session, client, user, token):
    expected_todos = 2
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/?offset=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_per_title(session, user, client, token):
    expected_todos = 4
    session.add_all(
        TodoFactory.create_batch(4, user_id=user.id, title='Qualquer Titulo')
    )
    await session.commit()

    response = client.get(
        '/todos/?title=Qualquer Titulo',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_per_description(session, user, client, token):
    expected_todos = 4
    session.add_all(
        TodoFactory.create_batch(4, user_id=user.id, description='Qualquer')
    )
    await session.commit()

    response = client.get(
        '/todos/?description=Qualquer',
        headers={
            'Authorization': f'Bearer {token}',
        },
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_per_states(session, client, user, token):
    expected_todos = 4
    session.add_all(
        TodoFactory.create_batch(4, user_id=user.id, state=TodoState.doing)
    )
    await session.commit()

    response = client.get(
        '/todos/?state=doing',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_with_all_filters(session, user, client, token):
    expected_todos = 2
    session.add_all(
        TodoFactory.create_batch(
            2,
            user_id=user.id,
            title='title',
            description='description',
            state=TodoState.doing,
        )
    )
    session.add_all(
        TodoFactory.create_batch(
            5,
            user_id=user.id,
            title='other title',
            description='pther description',
            state=TodoState.todo,
        )
    )
    await session.commit()

    response = client.get(
        '/todos/?title=title&description=description&state=doing',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


def test_patch_todo_erro(client, token):
    response = client.patch(
        '/todos/10',
        json={},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json() == {'detail': 'Task not found.'}
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_patch_todo(client, user, token, session):
    session.add_all(
        TodoFactory.create_batch(
            2,
            user_id=user.id,
            title='title',
            description='description',
            state=TodoState.doing,
        )
    )
    await session.commit()

    response = client.patch(
        f'/todos/{user.id}',
        json={'description': 'other description'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['description'] == 'other description'


def test_error_delete_todo(client, token):
    response = client.delete(
        '/todos/10',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}


@pytest.mark.asyncio
async def test_delete_todo(user, client, session, token):
    session.add_all(
        TodoFactory.create_batch(
            2,
            user_id=user.id,
            title='title',
            description='description',
            state=TodoState.doing,
        )
    )
    await session.commit()

    response = client.delete(
        f'/todos/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'message': 'Task has been deleted successfully.'
    }


@pytest.mark.asyncio
async def test_list_todos_exercicio_aula_9(
    session, client, user, token, mock_db_time
):
    with mock_db_time(model=Todo) as time:
        todo = TodoFactory.create(user_id=user.id)
        session.add(todo)
        await session.commit()

    await session.refresh(todo)
    response = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json()['todos'] == [
        {
            'created_at': time.isoformat(),
            'updated_at': time.isoformat(),
            'description': todo.description,
            'id': todo.id,
            'state': todo.state,
            'title': todo.title,
        }
    ]
