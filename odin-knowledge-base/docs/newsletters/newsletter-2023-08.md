## Package Updates [#](#package-updates)

`laytan` has been implementing Non-Blocking IO into [odin-http](https://github.com/laytan/odin-http/commit/64b8627bbe35c10f166988c7f1e9c99ca90c0402). Here is what he shared on our [Discord](https://discord.gg/vafXTdubwr).

```odin
Just merged the non-blocking IO branch into odin-http for faster and less resource intensive IO.
Darwin uses kqueue
Linux uses io_uring
Windows uses a thread pool (IOCP in the future but I am out of juice and wanted it merged)
All in a nice event-loop based abstraction.
```odin
## Blog Posts [#](#blog-posts)

Discord User `Charlie` has uploaded a [blog](https://cshenton.com/posts/2022-proto-topple/) on their 2022 prototypes done in odin. It looks like a good showcase of Physics and also shows SIMD usage.

## New Bindings / Ports [#](#new-bindings--ports)

- [shm\_queue](https://github.com/0xULT/shm_queue) Thread safe Queue port from go - `0xULT`
- [lmdb](https://github.com/Skytrias/lmdb) Bindings to [LMDB](https://www.symas.com/lmdb) - `Skytrias`
- [bass](https://github.com/elvodqa/bass-odin) Bindings to BASS audio - `elvodqa`
- [ufbx](https://github.com/cshenton/odin-ufbx/blob/master/example/example.odin) Bindings to ufbx - `Charlie`

## New Packages [#](#new-packages)

- [obacktracing](https://github.com/laytan/obacktracing) An abstraction around the libc backtrace API for Odin providing manual backtraces and a tracking allocator that keeps backtraces. - `laytan`
- [journey\_ecs](https://github.com/KDahir247/Odin-Journey/blob/dev/journey/journey_ecs.odin) Sparse set ecs - `Raigon`
- [metal\_window](https://gist.github.com/Lperlind/1bb993a1c0f1acdd49080fd4852f95c5) Odin Minimal Metal Window - `Perlind`
- [ClOdin](https://github.com/SjVer/ClOdin) simple command-line argument parsing package - `∆V`

## Categories [#](#categories)

This month we’ll try sorting showcase material by categories. Let us know how you like it.

- Game Development
- Tools & UI
- Graphic
- Miscellaneous

### Game Development [#](#game-development)

[](https://cdn.discordapp.com/attachments/568871319425515531/1136528605220982844/neon_shooter_01.mp4)

Tween stick shooter prototype running on Steam Deck - varomix

![...](https://cdn.discordapp.com/attachments/568871319425515531/1138763275207725066/image.png)

Navigation with navigation meshes and A star - Francis\_the\_cat

[](https://cdn.discordapp.com/attachments/568871319425515531/1139658973402906644/pfind_demo.mp4)

pathfinding demo: implemented A\* on a block chunk generator - sandwichman
[Github](https://github.com/spsandwichman/pathfinder)

[](https://cdn.discordapp.com/attachments/568871319425515531/1142118533178863667/2023-08-18_10-27-17.mp4)

I just started working on AI for my racing game and it's kinda hilarious how bad it is right now 😂 - CasualKyle

[](https://cdn.discordapp.com/attachments/568871319425515531/1144623943546851478/2023-08-25_15-23-10.mp4)

Cat game progress! animated friendly waterfall and liftoff sequence - karl\_zylinski

[](https://cdn.discordapp.com/attachments/568871319425515531/1142173388287258644/2023-08-18_20-57-50.mp4)

raylib FPS player controller example with triangle collision - jakubtomsu (Jacob)
[Gist](https://gist.github.com/jakubtomsu/9cae5298f86d2b9d2aed48641a1a3dbd)

[](https://cdn.discordapp.com/attachments/568871319425515531/1146821625942134795/camera_and_selection_area.mp4)

Starting on a level editor for a new game project. Just got camera controls and area selection working - \_brian

### Tools & UI [#](#tools--ui)

[](https://cdn.discordapp.com/attachments/568871319425515531/1136513460704923648/codin.mp4)

Working on multiline text widgets turned into a code editor - markersniffen

[](https://cdn.discordapp.com/attachments/568871319425515531/1140762067134062592/new16.mp4)

(M)SDF atlas exporting + json output 🎉 - Skytrias

[](https://cdn.discordapp.com/attachments/568871319425515531/1146517023204048957/20230828_012500.mp4)

visualization of exp(z) for an arbitrary complex number z that I made in my Desmos adjacent graphing app written in Odin and embedding luajit - master jonsie

### Graphics [#](#graphics)

[](https://cdn.discordapp.com/attachments/568871319425515531/1136753036392419379/PIQnNbpFyK.mp4)

OpenGL bindings generator similar to glad.sh - The Lua Whisperer
[Github](https://github.com/DragosPopse/glgen)

[](https://cdn.discordapp.com/attachments/568871319425515531/1137551609346408489/contour_wip03.mp4)

Polygon Triangulation so I can add a fill color to shapes 🔺 - varomix

[](https://cdn.discordapp.com/attachments/568871319425515531/1141770415849623672/screen-20230817-181649.mp4)

2D jello crate simulator running on Android - Moritz Falk

### Miscellaneous [#](#miscellaneous)

![...](https://cdn.discordapp.com/attachments/568871319425515531/1136299863210995806/image.png)

HMH - Day 213. 12k lines of Odin - V/A

[](https://cdn.discordapp.com/attachments/568871319425515531/1137150762745602078/Untitled.mov)

First time kqueue doesn't segfault trying to do non blocking IO in odin-http 🎊

![...](https://cdn.discordapp.com/attachments/568871319425515531/1143313794953658449/2023-08-21T184006300544227-0400.png)

After a little bit of linking headache, working bindings for Cyber!!! - Scoobery Doobery

>Source: https://odin-lang.org/news/newsletter-2023-08
