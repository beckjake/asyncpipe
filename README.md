## asyncpipe

This is a little module to help you chain together subprocess pipelines, a bit
more nicely than python natively lets you. The key element here is the support
for asyncio.

### OS Compatibility

This will only work on versions of python that support async/await syntax
I've only tested this on Linux. I don't see any reason why it wouldn't work on
OSX/BSD, but it's possible. I doubt this works on Windows at all.

### Python compatibility

This requires 'async' and 'await' keywords, so Python 3.5+ only.

#### Motivation

When you use a `PIPE` for stdout in the native asyncio.subprocess module, you
don't get back a value that can be passed to another Popen like you do in the
subprocess module. Instead you get a wrapper. Sometimes you can resolve that by
just using the 'shell' execution model, but sometimes that's not a great fit.

The solution is to do an error-prone set of operations with os.pipe and linking
up various subprocesses stdin/stdout. This gets especially ugly when you've got
a chain of 3+ shell commands.


### Use

#### Synchronous

The synchronous form is pretty straightforward:

	import asyncpipe
	pipe = asyncpipe.PipeBuilder('ls')
	# you can chain it
	pipe.chain('grep', '^S')
	# or use the 'or' operator
	pipe | 'wc -l'
	results = pipe.call()
	matches = int(results[-1].stdout.strip())

All of those return the underlying object, and the starting arguments are
optional, so this is equivalent:

	import asyncpipe
	pipe = asyncpipe.PipeBuilder().chain('ls') | 'grep ^s' | ['wc' '-l']
	results = pipe.call()
	matches = int(results[-1].stdout.strip())


#### Asyncronous

Async code is similar, except you need to pass the event loop as the 'loop'
value to the PipeBuilder, or set it any time before calling `call_async()`:

	import asyncpipe
	import asyncio
    loop = asyncio.new_event_loop()
    # if you don't do this, you will get errors from asyncio 
    asyncio.set_event_loop(loop)
	pipe = asyncpipe.PipeBuilder(loop=loop)
	pipe.chain('ls') | 'grep ^s' | ['wc' '-l']
	results = loop.run_until_complete(pipe.call_async())
	matches = int(results[-1].stdout.strip())

If you were doing more in your event loop, you would of course just
`await pipe.call_async()`!







