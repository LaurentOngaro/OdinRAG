# Coroutine-less way to visualize iterations

2025-12-26

Let’s say you’re working on a procgen system, or a similar problem where you combine multiple iterative algorithms to get visual results.
It could look something like this:

```odin
 1// Imagine this is for a tile-based 2D game or something
 2generate_level :: proc(some_params: ...) {
 3    some_temp_state_1, some_temp_state_2: int
 4    for i in 0..<N {
 5        // generate land tiles ...
 6    }
 7    for iter in 0..<4 {
 8        // run cellular automata ...
 9    }
10    for x in 0..<SIZE do for y in 0..<SIZE {
11        // spawn entity ...
12    }
13}
```odin
> All the logic being contained within one big procedure (possibly with a few helpers) is quite nice, especially for prototyping.

But, what if something goes wrong, and the debugger, logging or 2D/3D visuals don’t help?

You might want to inspect what the actual ***iterations*** are doing.

## The usual solution

If you’re using a managed language with coroutines, you can just `yield` from the procedure.

In other cases, you likely need to completely refactor your state management, put in a state machine, and split up the code a lot. I really don’t want to do that.

## No-refactoring approach

So here’s my 1-million-IQ solution.

What if you just **re-ran the entire procedure**, stopping at a different point each time? The observable effect is just like with coroutines.

So let’s try that! Here’s a helper proc to mark each “step” of the algorithm:

```odin
1max_iter: int
2curr_iter: int
3
4_iter :: proc(n := 1) -> (ok: bool) {
5    ok = curr_iter < max_iter
6    curr_iter += n
7    return ok
8}
```odin
Now all you need is to instrument your `generate_level` procedure:

```odin
 1generate_level :: proc(some_params: ...) {
 2    some_temp_state_1, some_temp_state_2: int
 3    for i in 0..<N {
 4        // generate land tiles ...
 5        _iter() or_return
 6    }
 7    for iter in 0..<4 {
 8        // run cellular automata ...
 9        _iter() or_return
10    }
11    for x in 0..<SIZE do for y in 0..<SIZE {
12        // spawn entity ...
13        _iter() or_return
14    }
15}
```odin
> In case you’re not using Odin, you can use `if (!_iter()) return` or another equivalent instead of `or_return`

And a way to control `max_iter`:

```odin
1max_iter = 0
2for app_main_loop_running {
3    max_iter += 1
4    generate_level(...)
5    debug_draw_level()
6}
```odin
And that’s it. Of course it works only if `generate_level` is reasonably fast, otherwise you’d have use other methods.

Thanks for reading, I hope it saves you some refactoring time.

>Source: https://jakubtomsu.github.io/posts/iter_debug
