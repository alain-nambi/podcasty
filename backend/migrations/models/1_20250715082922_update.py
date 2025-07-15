from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "category" RENAME TO "categories";
        ALTER TABLE "tag" RENAME TO "tags";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "tags" RENAME TO "tag";
        ALTER TABLE "categories" RENAME TO "category";"""
