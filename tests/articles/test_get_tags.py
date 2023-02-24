import pytest
import uuid


def make_get_tags_url() -> str:
    return "/tags"


@pytest.mark.asyncio
async def test_should_return_200(
    app,
    faker,
    create_user_and_decode,
    create_article_and_decode,
):
    client = app.test_client()

    author1 = await create_user_and_decode()
    author2 = await create_user_and_decode()

    tag1 = f"c-{str(uuid.uuid4())}"
    tag2 = f"a-{str(uuid.uuid4())}"
    tag3 = f"b-{str(uuid.uuid4())}"

    await create_article_and_decode(author_token=author1.token, tags=[tag1])
    await create_article_and_decode(author_token=author2.token, tags=[tag2])
    await create_article_and_decode(author_token=author1.token, tags=[tag3])

    response = await client.get(
        make_get_tags_url(),
    )

    assert response.status_code == 200

    response_data = await response.json

    tags = response_data["tags"]

    tag1_index = tags.index(tag1)
    tag2_index = tags.index(tag2)
    tag3_index = tags.index(tag3)

    assert tag2_index > -1
    assert tag2_index < tag3_index
    assert tag3_index < tag1_index
