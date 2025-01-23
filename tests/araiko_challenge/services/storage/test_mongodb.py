from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from coupon_challenge.models.coupon import Coupon, CouponCreate, CouponUpdate
from coupon_challenge.services.storage import (
    CouponStorageAlreadyExistsError,
    CouponStorageCreateError,
    CouponStorageDeleteError,
    CouponStorageNotFoundError,
)
from coupon_challenge.services.storage.mongodb import MongoDBCouponStorage


@pytest.fixture
def mock_mongo_client():
    with patch(
        "coupon_challenge.services.storage.mongodb.AsyncIOMotorClient"
    ) as mock_client:
        yield mock_client


@pytest.fixture
def mock_mongo_collection(mock_mongo_client):
    mock_client_instance = mock_mongo_client.return_value
    mock_get_all_cursor = MagicMock()
    mock_get_all_cursor.to_list = AsyncMock()
    mock_client_instance["challenge"]["coupons"].find = Mock()
    mock_client_instance["challenge"]["coupons"].find.return_value = mock_get_all_cursor
    mock_client_instance["challenge"]["coupons"].find_one = AsyncMock()
    mock_client_instance["challenge"]["coupons"].insert_one = AsyncMock()
    mock_client_instance["challenge"]["coupons"].update_one = AsyncMock()
    mock_client_instance["challenge"]["coupons"].delete_one = AsyncMock()
    return mock_client_instance["challenge"]["coupons"]


@pytest.fixture
def minimal_coupon() -> Coupon:
    return Coupon(name="coupon_test", discount=10)


@pytest.fixture
def minimal_coupon_create() -> CouponCreate:
    return CouponCreate(name="coupon_test", discount=10)


@pytest.fixture
def minimal_coupon_update() -> CouponUpdate:
    return CouponUpdate(name="coupon_test", discount=90)


@pytest.fixture
def mock_find_one_none(mock_mongo_collection):
    mock_mongo_collection.find_one.return_value = None


@pytest.fixture
def mock_find_one_minimal_coupon(mock_mongo_collection, minimal_coupon):
    mock_mongo_collection.find_one.return_value = minimal_coupon.model_dump()


@pytest.fixture
def mongo_storage(mock_mongo_collection) -> MongoDBCouponStorage:
    return MongoDBCouponStorage(db_uri="fake_db_uri")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("mocked_coupons", "expected_count"),
    [
        ([], 0),
        ([Coupon(name="coupon1", discount=10, is_percent=True)], 1),
        (
            [
                Coupon(name="coupon1", discount=10, is_percent=True),
                Coupon(name="coupon2", discount=20, is_percent=False),
            ],
            2,
        ),
    ],
)
async def test_get_all(
    mock_mongo_collection, mongo_storage, mocked_coupons, expected_count
):
    mock_mongo_collection.find.return_value.to_list.return_value = [
        coupon.model_dump() for coupon in mocked_coupons
    ]

    coupons = await mongo_storage.get_all()
    assert len(coupons) == expected_count


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_find_one_minimal_coupon")
async def test_get(mock_mongo_collection, mongo_storage, minimal_coupon):
    coupon = await mongo_storage.get(minimal_coupon.name)
    mock_mongo_collection.find_one.assert_called_once()

    assert coupon == minimal_coupon


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_find_one_none")
async def test_get__not_found(mongo_storage):
    with pytest.raises(CouponStorageNotFoundError):
        await mongo_storage.get("none")


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_find_one_none")
async def test_create(
    mongo_storage, mock_mongo_collection, minimal_coupon_create
) -> None:
    coupon = await mongo_storage.create(minimal_coupon_create)

    created_dump = minimal_coupon_create.model_dump()

    mock_mongo_collection.insert_one.assert_called_once_with(created_dump)

    assert coupon == Coupon.model_validate(created_dump)


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_find_one_minimal_coupon")
async def test_create__coupon_already_exists(
    mongo_storage, minimal_coupon_create
) -> None:
    with pytest.raises(CouponStorageAlreadyExistsError):
        await mongo_storage.create(minimal_coupon_create)


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_find_one_none")
async def test_create__create_error(
    mongo_storage, mock_mongo_collection, minimal_coupon_create
) -> None:
    errored_insert_result = Mock()
    errored_insert_result.inserted_id = None
    mock_mongo_collection.insert_one.return_value = errored_insert_result

    with pytest.raises(CouponStorageCreateError):
        await mongo_storage.create(minimal_coupon_create)


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_find_one_minimal_coupon")
async def test_update(mongo_storage, minimal_coupon_update) -> None:
    coupon = await mongo_storage.update(minimal_coupon_update)

    assert coupon == Coupon.model_validate(minimal_coupon_update.model_dump())


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_find_one_none")
async def test_update__not_found(mongo_storage, minimal_coupon_update) -> None:
    with pytest.raises(CouponStorageNotFoundError):
        await mongo_storage.update(minimal_coupon_update)


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_find_one_minimal_coupon")
async def test_delete(mongo_storage, mock_mongo_collection, minimal_coupon) -> None:
    succeed_deleted_result = Mock()
    succeed_deleted_result.deleted_count = 1
    mock_mongo_collection.delete_one.return_value = succeed_deleted_result

    await mongo_storage.delete(minimal_coupon.name)

    mock_mongo_collection.delete_one.assert_called_once_with(
        {"name": minimal_coupon.name}
    )


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_find_one_none")
async def test_delete__not_found(mongo_storage, minimal_coupon) -> None:
    with pytest.raises(CouponStorageNotFoundError):
        await mongo_storage.delete(minimal_coupon.name)


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_find_one_minimal_coupon")
async def test_delete__with_error(
    mongo_storage, mock_mongo_collection, minimal_coupon
) -> None:
    errored_deleted_result = Mock()
    errored_deleted_result.deleted_count = 0
    mock_mongo_collection.delete_one.return_value = errored_deleted_result

    with pytest.raises(CouponStorageDeleteError):
        await mongo_storage.delete(minimal_coupon.name)
