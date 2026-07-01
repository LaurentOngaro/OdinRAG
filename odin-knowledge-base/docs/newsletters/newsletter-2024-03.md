Read up on the compiler changes in the [monthly release](https://github.com/odin-lang/Odin/releases/tag/dev-2024-03) notes.

GingerBill has been featured on a podcast from [Mike Shah](https://www.youtube.com/@MikeShah) this month

## Projects shared this month [#](#projects-shared-this-month)

| Project Name | Description |
| --- | --- |
| [jolt](https://gitlab.com/raygarner13/jolt) | Jolt bindings |
| [libpq](https://github.com/laytan/odin-postgresql) | PostgreSQL/libpq bindings |
| [odin-xinput](https://github.com/lordhippo/odin-xinput) | Xinput bindings |
| [odin-tray](https://github.com/lordhippo/odin-tray) | Tray library port |
| [odin-bivector](https://github.com/softmonkey/odin-bivector) | Geometric Algebra |
| [odin-protobuf](https://github.com/lordhippo/odin-protobuf) | Protobuf |
| [odin-tilengine](https://github.com/akuspel/odin-tilengine) | Tilengine bindings |
| [GameNetworkingSockets](https://github.com/Smilex/GameNetworkingSockets-Odin) | Valve’s GameNetworkingSocket bindings |
| [odin-psapi](https://github.com/iansimonson/odin-psapi) | Windows PSAPI bindings |

## Project Showcase [#](#project-showcase)

We’re trying something new this month, let us know what you think! We’ll focus on ***4*** projects that have been worked on. Each author tells you something about their project.

## Homeshift [#](#homeshift)

Homeshift (title in progress) is a 2D-platformer inspired by games such as Kye by Colin Garbutt and Super Meat Boy. Its main goals are, firstly, to provide challenging platforming with simple to grasp controls, and more importantly, to be easily moddable. This has been achieved with the help of Tilengine – an open source retro graphics library written in C.

### Level editing and easy modding [#](#level-editing-and-easy-modding)

![](/images/news/2024-03-Akuspel1.png)

Tilengine has made handling levels and rendering rather painless. It has built in support for loading .tmx files from Tiled, as well as out of the box parallax layers and other graphical effects, such as CRT- and per scanline filters.

[](/images/news/2024-03-Akuspel2.mp4)
As seen on video, levels are configured with .json files and loaded at runtime. This makes iteration fast, and opens the door for easy modification by players.

### Why Odin and Tilengine? [#](#why-odin-and-tilengine)

The biggest pain point with Tilengine has been its at times lacking documentation. However, it has for the most part been a very pleasant library to use. The best part of development so far, though, has been Odin and the wonderful community surrounding it. The language feels very well suited for game development, with built in vector support improving life quality by at least 10%. Figuring out memory management and such has been a breeze with the help of Karl Zylinski and other lovely Odin gamedev folk.

[](/images/news/2024-03-Akuspel3.mp4)

Some of Tilengine’s graphical features on display
Parallax layers and sprite animations. Featuring my favourite level and a cute looking, yet dangerous, ghost.

For anyone interested, my Tilengine bindings for Odin are available at [Github](https://github.com/akuspel/odin-tilengine)

---

## Cat & Onion [#](#cat--onion)

CAT & ONION is a whimsical cat adventure game. It’s written in Odin and uses Raylib for graphics, audio and input. The game is a short story that plays like an adventure game combined with a 2D side-scroller: Talk to the beings of the forest, find items and progress a strange story. The game will take you places where no cat has ever gone before!

### Why Odin? [#](#why-odin)

Odin was chosen because it was “low level with a high level feeling”, meaning that it was possible to do all the low stuff one would normally do in C while also empowering creative gameplay programming through Odin’s modern features.

![](/images/news/2024-03-karl1.png)

### Rapid prototyping with Hot Reload [#](#rapid-prototyping-with-hot-reload)

During the development hot reload of the Odin code has been used to quickly iterate on gameplay. It was easy to implement using the `dynlib` package in Odin’s core library. Karl has written a blog post about his hot reloading setup [here](http://zylinski.se/posts/hot-reload-gameplay-code/).

### Odin and Raylib works well together! [#](#odin-and-raylib-works-well-together)

Raylib suits Odin well due to its simple C API. But when you use it with Odin you get added benefits such as no name collisions, thanks to Odin’s package system. Raylib allowed Karl to quickly prototype graphics and gameplay, while it has enough features to actually also ship a game.

![](/images/news/2024-03-karl2.png)

### Release on March 12 [#](#release-on-march-12)

The game will release March 12 on Steam. It will be the first game released on Steam to use Odin. It is possible to wishlist it here: <https://store.steampowered.com/app/2781210/CAT__ONION/>

---

## Solar Storm [#](#solar-storm)

![](/images/news/2024-03-jakub1.gif)

Solar Storm is an upcoming tactical sci-fi artillery game. It’s a solo project I’ve been writing in a custom engine for the last ~4 months. It’s inspired by local multiplayer games from the 90s like Scorched Earth (1991) and Worms (1995). The entire game is written from scratch in the [Odin programming language](https://odin-lang.org).

The game engine is built with the help of [Sokol](https://github.com/floooh/sokol). It’s a set of STB-style cross-platform libraries for C/C++, with an official support for Odin as well as some other languages. In particular, I use sokol\_app for windowing and interfacing with the OS, and sokol\_gfx as an rendering API abstraction.

[Play Solar Storm on Steam](https://store.steampowered.com/app/2754920/Solar_Storm/) and [Join our Discord!](https://discord.com/invite/wn5jMMMYe4)

### Shaders [#](#shaders)

The shaders are written in Sokol’s flavor of GLSL, which has a cross-platform shader compiler called sokol-shdc. Usually writing shaders for multiple rendering APIs is a lot of pain. But sokol-shdc uses libraries like GLSLang, SPIRV-Tools, SPIRV-Cross to transpile them for the appropriate platform.

Another nice aspect is that the compiler can generate source code and boilerplate for any language supported by Sokol.

### World pass [#](#world-pass)

The terrain is drawn as a single quad. A shader which reads from the terrain SDF texture and a color texture and does the shading. Explaining the terrain in-depth is out of scope for this article, let’s do that another time…

![](/images/news/2024-03-jakub2.png)

All world-space elements are rendered into a custom render target. It’s a texture with single channel per pixel in the R8\_UNORM format. This pass also uses a depth buffer for odrdering objects instead of sorting. It’s essentially free on modern hardware and it makes things easier.

### Shapes [#](#shapes)

All of the other things in the game are rendered using primitive shapes. Every frame, the game pushes shape instances to instance buffers, which then get uploaded to the GPU memory once it’s time to render them. This uses an immediate API in the form of `draw_shape` procedure.

There is one instance buffer per shape type. It’s a simple fixed array of a shape instance struct, which has a memory layout the GPU can feed to the vertex shader in the form of per-instance parameters.

More complex shapes like tanks are made up of multiple shapes.
![](/images/news/2024-03-jakub3.png)

All shapes of certain type are rendered using GPU instancing, this means it takes only about 6 drawcalls to render all shapes in the worst case.

That’s it for the world render pass, here is the result so far:

![](/images/news/2024-03-jakub4.png)

### Full Article [#](#full-article)

After the world pass comes post processing and a screenspace pass.

If you’re curious about the entire rendering process and want to know more implementation details, I have an [extended version of this article](https://jakubtomsu.github.io/posts/solar_storm_renderer/) on my website.

---

## 2Deez [#](#2deez)

2Deez is a fleshed out minimal fighting game condensing the essence 3D fighting games like Virtua Fighter and Tekken.

There’s a pre-release netplay build available on the 2Deez discord <https://discord.gg/EZABxnrV5J>

### GGPO Netplay [#](#ggpo-netplay)

Here’s a short set I played with the composer for 2Deez.

### “Customization” [#](#customization)

As you could see from the set, we had custom colours. You can make custom palettes to. There’s extensive palettised customization options, as well as HATS.

[](/images/news/2024-03-krzyszto1.mp4)

### Training Mode [#](#training-mode)

The training mode is heavily fleshed out with advanced features not found in other fighting games, designed to help you understand the game deeply and test out scenarios with precision. Here’s one example of being able to frame advance with your chosen inputs, and see the preview of the chosen inputs.

[](/images/news/2024-03-krzyszto2.mp4)

### Why Odin? [#](#why-odin-1)

This game has been my first big and serious programming project, since I only started programming a few years ago. The first iteration of 2Deez I made was called W4f, which I produced in two weeks for WASM4, a webassembly fantasy console ( <https://wasm4.org/play/w4f/> ), and I made it specifically for the purposes of learning Odin. I was making a game in C++, and was looking for alternatives, and decided to take a break to spend two weeks to both learn Odin and make this game. With the help of the Odin discord, I was able to learn the basics of the language and make this game very quickly.

Odin itself has been a pleasure to work in, and 2Deez is made only with the core library, and the SDL and GGPO vendor bindings. It was way easier than trying to make a game with a game engine, since I could understand all of the moving parts myself, and had enough quality of life features to have a very low friction development experience without compromising on performance.

>Source: https://odin-lang.org/news/newsletter-2024-03
