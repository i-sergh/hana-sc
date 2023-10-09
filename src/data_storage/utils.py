
try:
    from storage_pgdb import engine
    from data_storage.models_create import StoragePgBase
except:
    # remove on releace
    import sys
    sys.path.append('../')
    from storage_pgdb import engine
    from data_storage.models_create import StoragePgBase




# https://stackoverflow.com/questions/68230481/sqlalchemy-attributeerror-asyncengine-object-has-no-attribute-run-ddl-visit
async def drop_and_create():
    async with engine.begin()  as session:
        await session.run_sync(StoragePgBase.metadata.drop_all)
        await session.run_sync(StoragePgBase.metadata.create_all)

async def create():
    async with engine.begin()  as session:
        await session.run_sync(StoragePgBase.metadata.create_all)

if __name__ == '__main__':
    import asyncio 
    asyncio.run(drop_and_create())