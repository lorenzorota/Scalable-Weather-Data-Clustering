import asyncio

class Sleep:
    """ source: https://code.luasoftware.com/tutorials/python/asyncio-graceful-shutdown/ """
    def __init__(self):
        self.tasks = set()

    async def sleep(self, delay, result=None):
        task = asyncio.create_task(asyncio.sleep(delay, result))
        self.tasks.add(task)
        try:
            return await task
        except asyncio.CancelledError:
            return result
        finally:
            self.tasks.remove(task)

    def cancel_all(self):
        for _task in self.tasks:
            _task.cancel()