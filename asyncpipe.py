import asyncio
import os
import shlex
import subprocess
from collections import namedtuple


PopenResult = namedtuple('PopenResult', 'returncode stdout stderr')


async def get_popen_result_async(popen):
    stdout, stderr = await popen.communicate()
    return PopenResult(popen.returncode, stdout, stderr)


def get_popen_result(popen):
    stdout, stderr = popen.communicate()
    return PopenResult(popen.returncode, stdout, stderr)


class PipeBuilder:
    def __init__(self, *args, loop=None):
        self._argspecs = []
        self.loop = loop
        if args:
            self.chain(*args)

    def chain(self, *args):
        """Add a command to the chain of commands to be pipelined"""
        self._argspecs.append(args)
        return self

    def __or__(self, args):
        if isinstance(args, str):
            args = shlex.split(args)
        self._argspecs.append(args)
        return self

    def _arg_iterator(self, stdin=None, stdout=None, stderr=None):
        if stdout is None:
            stdout = asyncio.subprocess.PIPE
        if stderr is None:
            stderr = asyncio.subprocess.PIPE

        argspecs = iter(self._argspecs)
        # get the first arguments
        try:
            args = next(argspecs)
        except StopIteration:
            # no commands
            return

        reader = stdin
        while True:
            try:
                next_args = next(argspecs)
            except StopIteration:
                # at the end of the loop! stdout is pipe
                yield args, reader, stdout, stderr
                os.close(reader)
                return

            # our next command will need a pipe!
            next_reader, writer = os.pipe()
            yield args, reader, writer, asyncio.subprocess.PIPE
            if reader is not stdin:
                os.close(reader)
            os.close(writer)
            reader = next_reader
            args = next_args

    async def call_async(self, stdin=None, stdout=None, stderr=None):
        """Call the commands attached to the event loop, chaining stdout/stdin
        together.

        See the documentation on asyncio.subprocess.create_subprocess_exec for
        more details on these parameters.

        :param stdin: The stdin to use for the initial command in the pipeline.
        :param stdout: The stdout to use for the final command in the pipeline.
        :param stderr: The stderr to use for the final command in the pipeline.
        :returns: A list of PopenResult tuples. For all but the last command,
            the `stdout` attribute will be None and the `stderr` attribute will
            be bytes.
        """
        commands = []
        for args, sin, sout, serr in self._arg_iterator(stdin, stdout, stderr):
            commands.append(await asyncio.subprocess.create_subprocess_exec(
                *args,
                stdin=sin,
                stdout=sout,
                stderr=serr,
                loop=self.loop,
            ))
        results = [get_popen_result_async(c) for c in commands]
        return await asyncio.gather(*results)

    def call(self, stdin=None, stdout=None, stderr=None):
        """Call the commands, chaining stdout/stdin together.

        See the documentation on asyncio.subprocess.create_subprocess_exec for
        more details on these parameters.

        :param stdin: The stdin to use for the initial command in the pipeline.
        :param stdout: The stdout to use for the final command in the pipeline.
        :param stderr: The stderr to use for the final command in the pipeline.
        :returns: A list of PopenResult tuples. For all but the last command,
            the `stdout` attribute will be None and the `stderr` attribute will
            be bytes.
        """
        commands = []
        for args, sin, sout, serr in self._arg_iterator(stdin, stdout, stderr):
            commands.append(
                subprocess.Popen(args, stdin=sin, stdout=sout, stderr=serr)
            )
        return [get_popen_result(c) for c in commands]
