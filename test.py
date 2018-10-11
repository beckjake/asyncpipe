import asyncio
from unittest import TestCase

import asyncpipe

class AsyncPipeTest:
    def test_pipeline(self):
        pipe = self.pipe.chain(
            'echo', '-e', 'foo\nbar\nbaz'
        ).chain(
            'grep', '^b'
        ).chain(
            'wc', '-l'
        )
        results = self.run_cmd(pipe)
        self.assertEqual(results[-1].stdout.decode('utf-8').strip(), '2')

    def test_pipeline_pipes(self):
        pipeline = self.pipe | 'echo -e "foo\nbar\nbaz"' | 'grep ^b' | 'wc -l'
        results = self.run_cmd(pipeline)
        self.assertEqual(results[-1].stdout.decode('utf-8').strip(), '2')

    def test_pipeline_mixed(self):
        pipeline = self.pipe.chain('echo', '-e', 'foo\nbar\nbaz') | 'grep ^b' | ['wc', '-l']
        results = self.run_cmd(pipeline)
        self.assertEqual(results[-1].stdout.decode('utf-8').strip(), '2')


# a basic test on unix systems
class TestAsync(TestCase, AsyncPipeTest):
    def setUp(self):
        super(TestAsync, self).setUp()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.pipe = asyncpipe.PipeBuilder(loop=self.loop)

    def tearDown(self):
        super(TestAsync, self).tearDown()
        # handle a gross 3.5 issue
        self.loop.close()
        asyncio.set_event_loop(None)

    def run_cmd(self, pipe):
        return self.loop.run_until_complete(pipe.call_async())


class TestSync(TestCase, AsyncPipeTest):
    def setUp(self):
        self.pipe = asyncpipe.PipeBuilder()

    def run_cmd(self, pipe):
        return pipe.call()
