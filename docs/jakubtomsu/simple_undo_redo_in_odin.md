# Simple Undo/Redo System in Odin

2024-05-28

This is a short blog post about something I’ve had to implement recently: editor undo/redo functionality.

A few weeks ago I started working on a new project, it’s a 3D FPS game inspired by Quake and other ’90s shooters.
The world is a 16x16x16 uniform grid of blocks, and it loops infinitely. Here is a clip of the game prototype:

> This is a small boomer shooter prototype I've been working on lately. The world is 16x16x16 blocks and it infinitely repeats itself.[#gamedev](https://twitter.com/hashtag/gamedev?src=hash&ref_src=twsrc%5Etfw) [pic.twitter.com/ONrkzmf5t2](https://t.co/ONrkzmf5t2)
>
> — Jakub Tomšů (@jakubtomsu\_) [May 24, 2024](https://twitter.com/jakubtomsu_/status/1794059547146936800?ref_src=twsrc%5Etfw)

This clip uses procedurally generated levels. Those are cool, but don’t have that much structure and interesting stuff going on. So I quickly decided I need to hand-craft levels for them to reach the full potential.

So I wrote a simple level editor. It was surprisingly quick, I had all of the basic functionality implemented within a few hours. One of the problems I had to solve was undo/redo system, which seems very challenging but doesn’t have to be. I found a very simple way to structure the code to make the implementation trivial.

My implementation is inspired by rxi’s [Simple Undo System](https://rxi.github.io/a_simple_undo_system.html) and Dennis Gustaffson’s [Undo for Lazy Programmers](https://blog.voxagon.se/2018/07/10/undo-for-lazy-programmers.html)

## Level Representation

First, let’s define the data for our level. In my case it’s very simple, but it’s easy to extend if necessary.

```odin
 1Level :: struct {
 2    using info:   Level_Info,
 3    cells:        Level_Cells,
 4    detail_cells: Level_Detail_Cells,
 5}
 6
 7Level_Cells :: [LEVEL_BOUNDS_X][LEVEL_BOUNDS_Y][LEVEL_BOUNDS_Z]Cell // Cell is a u8 enum
 8
 9Level_Detail_Cells :: [LEVEL_BOUNDS_X][LEVEL_BOUNDS_Y][LEVEL_BOUNDS_Z]Detail_Cell
10
11Level_Info :: struct {
12    size:      IVec3,
13    fog_color: Vec3,
14}
```odin
The goal here is to organize the level representation into a bunch of “chunks” (mostly by size and importance). All miscellaneous level metadata goes into `Level_Info` but other big chunks of data are a separate member.

Note: this assumes all of your level data is statically allocated and trivially copyable. I do this for *all* of my data anyway, I think there isn’t a reason to use any dynamic allocation for the use cases I care about. I might write a blog about this another time, it’s a very useful way to think about data and not many people talk about it. It’s always borrow checker/RAII/Arenas/Custom Allocators…

## Save Points

Now, let’s define a way to store a single “change” to the data. This acts as a save point the user can go back to.

```odin
1Editor_Undo_Item :: union {
2    Level_Info,
3    Level_Cells,
4    Level_Detail_Cells,
5}
```odin
This stores a change to a part of a level. It’s a [tagged union](https://odin-lang.org/docs/overview/#unions), so the total size is the size of the largest item.

This allows me to easily store a change to any part of a level. That’s why I separated the level into chunks in the previous step, it makes it easier to organize changes into groups. In theory you *could* save the entire level on every change. But this is almost as simple and can save a lot of memory.

This way every change takes up memory for the “worst-case”, which might seem bad at first but it’s actually completely fine. In my case one undo item is 4 kilobytes, which is almost nothing these days. This system also scales really well in cases where you modify *most or all* of the cells, and doesn’t create unexpected spikes. But the reasons for focusing on worst-case computation is a big topic, let’s leave that for another blog post :)

## History Buffers

Let’s define a way to store the actual edits within our editor state.

```odin
1Editor :: struct {
2    level: Level, // current level data
3    undo:  Queue(2048, Editor_Undo_Item),
4    redo:  Queue(2048, Editor_Undo_Item),
5    // other editor state...
6}
```odin
The editor stores two queues (ring buffers) of edits, one for Undo and one for Redo. The reason why I use a queue is to have the ability to “force push” an edit at the end. If I used a regular array/stack, I would need to shift all other items down by one slot. The queue I use comes from my own small library for static datastructures, but you could use something like `core:container/queue` as well.

```odin
1editor_undo_push :: proc(ed: ^Editor, item: Editor_Undo_Item) {
2    // Makes sure the item is always pushed back into the queue, even if it's full.
3    queue_push_back_force(&ed.undo, item)
4}
```odin
This is the procedure for pushing save points before any edits. I pass the state which will be changed, and then perform the change. Here is an example of placing wall blocks on a mouse click:

```odin
1if input_pressed(.Mouse_Left) {
2    editor_undo_push(ed, ed.level.cells)
3    // Do any modifications to level.cells...
4    ed.level.cells[cursor.x][cursor.y][cursor.z] = .Wall
5}
```odin
## Ctrl+Z and Ctrl+Shift+Z

This is all I need to implement the actual undo/redo functionality. This logic is the same as in rxi’s article. Pop from one buffer, and before applying the data push the current state to the other buffer.

```odin
 1block: if input_pressed(inp, .Z) || input_repeated(inp, .Z) {
 2    modifiers: bit_set[Input_Modifier] = input_modifiers_down(inp)
 3
 4    // Pop the data from a change buffer depending on the operation
 5    // Breaks out of this entire scope if it's empty
 6    change: Editor_Undo_Item
 7    switch modifiers {
 8    case {.Left_Control}:
 9        change = queue_pop_back_safe(&ed.undo) or_break block
10    case {.Left_Control, .Left_Shift}:
11        change = queue_pop_back_safe(&ed.redo) or_break block
12    case:
13        break block
14    }
15
16    // Prepare a save point for the current data
17    // Write the change to the current state
18    prev: Editor_Undo_Item
19    switch v in change {
20    case Level_Info:
21        prev = ed.level.info
22        ed.level.info = v
23    case Level_Cells:
24        prev = ed.level.cells
25        ed.level.cells = v
26    case Level_Detail_Cells
27        prev = ed.level.detail_cells
28        ed.level.detail_cells = v
29    }
30
31    // Push the current data into the _other_ buffer
32    switch modifiers {
33    case {.Left_Control}:
34        queue_push_back_force(&ed.redo, prev)
35    case {.Left_Control, .Left_Shift}:
36        queue_push_back_force(&ed.undo, prev)
37    }
38}
```odin
And that’s it! Turns out this entire system is not many lines of code at all, and is efficient even when you use worst-case-sized statically allocated data structures. That said, it’s not a one-size-fits-all method. If you have gigantic scenes you probably need to look into other approaches (maybe XOR and RLE compressed delta states? LZ4? idk).

But this is fine for basically anything an indie developer might need in 99% of cases. Hope this helps, thank you for reading!

>Source: https://jakubtomsu.github.io/posts/simple_undo_redo_in_odin
