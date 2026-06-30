## Compiler Updates [#](#compiler-updates)

[Monthly Release](https://github.com/odin-lang/Odin/releases/tag/dev-2023-10) including a few new language features and LLVM 17.0.1 support for windows.

- `or_break`
- `or_continue`
- `#relative [^]T` (relative multi-pointers)
  - Replaced `#relative []T` (relative slices)
  - This data type might be removed in the future

---

## Socials [#](#socials)

We’ll split up the different social platforms this time around.

- YouTube

  - [Rickard Andersson](https://www.youtube.com/watch?v=VLcTrUhSdlg&list=PLEQTpgQ9eFCGlQa2z0j_TQTGggHOIF8Z1) (`gonz` on Discord) has been uploading a video series about Odin!
  - [karl\_zylinski](https://www.youtube.com/@karl_zylinski) is working on their cat game, uploading videos and streaming ocassionally.
- Twitter

  - [Charlie](https://twitter.com/charshenton) has been posting lot’s of content on discord but some of his showcase material lands only on his twitter.
- Blogs

  - karl\_zylinski has recently posted a blog on [Hot Reload Gameplay Code](http://zylinski.se/posts/hot-reload-gameplay-code/) in Odin!

---

## Games [#](#games)

[](https://cdn.discordapp.com/attachments/568871319425515531/1155521114722812046/astrodrift.mp4)

Astro Drift is a short roguelike rocket-drifting shooter. Destroy the asteroids to gain score!

&amp;lt;a href=https://jakubtomsu.itch.io/astrodrift&amp;gt;Astro Drift by jakubtomsu, Dylan Seibert, Jammigans&amp;lt;/a&amp;gt;

---

## Editors [#](#editors)

***Sentient Coffee*** has added support for the [focus editor](https://github.com/focus-editor/focus). Check out the discord [link / explanation](https://discord.com/channels/568138951836172421/568871319425515531/1156585773290762341).

---

## New Bindings / Ports [#](#new-bindings--ports)

- [Fractal-Buddhabrot](ttps://github.com/joaocarvalhoopen/Fractal-Buddhabrot-in-Odin) Port of Fractal Buddhabrot - `JoaCarvalho`
  OLD
- [pegasus](https://github.com/dvrd/pegasus) Reimplemented golangs `gpeg` - `dvrd`
- [Moog-Ladder-Filter](https://github.com/joaocarvalhoopen/Moog-Ladder-Filter-in-Odin) Moog Ladder Filter - `JoaoCarvalho`
- [nbio](https://github.com/laytan/odin-http/tree/main/nbio) non-blocking IO - `laytan`
- [Piece-Table](https://github.com/xDahl/Piece-Table) Piece-Table in Odin - `xDahl`

---

## New / Updated Packages [#](#new--updated-packages)

I’ll try posting the comments the authors posted for their packages.

### Odin Dear ImGui - `L4` [#](#odin-dear-imgui---l4)

[odin-imgui](https://gitlab.com/L-4/odin-imgui) Generated Dear ImGui bindings using dear\_bindings

- Generates bindings for both the `master` and `docking` ImGui branches, using [`dear_bindings`](https://github.com/dearimgui/dear_bindings)
- Contains bindings for most of the Dear ImGui implementations
- All backends which exist in `vendor:` have bindings
- These include: `vulkan, sdl2, opengl3, sdlrenderer2, glfw, dx11, dx12, win32, osx, metal`
- Compiles bindings as well as any wanted backends
- Tested on Windows, Linux, and Mac
- Includes several examples which can be used as a reference
- `GLFW + OpenGL, SDL2 + D3D11, SDL2 + Metal, SDL2 + OpenGL, SDL2 + SDL2 Renderer, SDL2 + Vulkan`

### LBP-Serialization - `jakubtomsu (Jacob)` [#](#lbp-serialization---jakubtomsu-jacob)

[LBP-Serialization](https://github.com/jakubtomsu/odin-lbp-serialization) “I made my LBP serialization code open-source, it’s still kinda experimental though.”

Here are the benefits of this method:

- single procedure for both serialization and deserialization
- full backwards compatibility is extremely easy
- good control over the exact data layout if necessary
- no RTTI

This is how easy it is to serialize complex datastructures:

```odin
Foo :: struct {
    a:          i32,
    b:          f32,
    name:       string,
}

Bar :: struct {
    foos: [dynamic]Foo,
    data: map[i32]bit_set[0 ..< 8],
}

serialize_foo :: proc(s: ^Serializer, foo: ^Foo, loc := #caller_location) -> bool {
    serialize(s, &foo.a, loc) or_return
    serialize(s, &foo.b, loc) or_return
    serialize(s, &foo.name, loc) or_return
    return true
}

serialize_bar :: proc(s: ^Serializer, bar: ^Bar, loc := #caller_location) -> bool {
    serialize(s, &bar.foos) or_return
    serialize(s, &bar.data) or_return
    return true
}
```odin
### Getopts - `Pix` [#](#getopts---pix)

[Getopts](https://github.com/Pix-xiP/getopts) A Odin command line argument parser, loosely based on the `getopts_long`.

```odin
opts := init_opts()
defer deinit_opts(&opts)
{ // Scoping for easy scope of using.
  using optarg_opt
  add_arg(&opts, "flag", .NO_ARGUMENT)
  add_arg(&opts, "opt-argument", .OPTIONAL_ARGUMENT)
  add_arg(&opts, "required", .REQUIRED_ARGUMENT)
  add_arg(&opts, "h", .NO_ARGUMENT, "help") // Alternative name // long_opt
  add_arg(&opts, "m", .OPTIONAL_ARGUMENT, "my_flag_here")

}
getopt_long(os.args, &opts)
// Parse opts:
for opt in opts.opts {
  if ! opt.set do continue // allows to skip non set options.
  switch opt.name { // name will always be set, don't have to check both
    case "flag":
      // Something
    case "required":
      // Something else 
    case:
      // default? Usage!
  }  
}
```odin
---

## Categories [#](#categories)

This month we’ll do categories again.

- Game Development
- Graphics
- Tools & UI
- Miscellaneous

### Game Development [#](#game-development)

![...](https://media.discordapp.net/attachments/568871319425515531/1146935058465304606/simulator.png)

Took some time to recreate the Playdate Hello World from the official C\_API examples - Colin Bellino

[](https://cdn.discordapp.com/attachments/568871319425515531/1147571737857376397/write_area_and_handle_edges.mp4)

Writing areas to underlying grid and handling edge-cases - \_brian

[](https://cdn.discordapp.com/attachments/568871319425515531/1149339866463731782/2023-09-07_15-38-21.mp4)

Made a lil spline editor that uses cubic bézier curves :3 - karl\_zylinski

[](https://cdn.discordapp.com/attachments/568871319425515531/1149579299523928134/PlaydateSimulator_87e1JZHaXp.mp4)

Odin-ifing the Playdate bindings, including documentation! - Mungo\_

[](https://cdn.discordapp.com/attachments/568871319425515531/1149735588090609674/QaLCBG63Pl.mp4)

goofing around with postfx in my game/engine. Vignette + scuffed pixelator - The Lua Whisperer

![...](https://cdn.discordapp.com/attachments/568871319425515531/1150961171575353475/image-1.png)

Gonna be transferring my game over to Odin, I really just need a refreshing language, and after using it, felt pretty darn great to write in. - Mezo☆

![...](https://cdn.discordapp.com/attachments/568871319425515531/1155967392564912238/image.png)

Hell, GUI is a pain, got it to be somewhat pleasant to work with now... - Francis\_the\_cat

[](https://cdn.discordapp.com/attachments/568871319425515531/1156153894519447563/trailer_1.mp4)

Latest cat game developments. Lots of new graphics and the interaction system is quite useful now.

[](https://cdn.discordapp.com/attachments/568871319425515531/1156461782903296142/org.cshenton.questodin-20230925-202509.mp4)

Super basic physics demo based off this repo - master jonsie

[](https://cdn.discordapp.com/attachments/568871319425515531/1156882453001162822/trailer_new_comp_12.mp4)

Before vs after comparison of new art style! The new style uses only 8 colors 🎨 - karl\_zylinski

### Graphics [#](#graphics)

[](https://cdn.discordapp.com/attachments/568871319425515531/1147077104920449075/ply_60.mp4)

Been wanting to write a point cloud renderer... but this isn't that, it's just GL\_POINTS. - Charlie

[](https://cdn.discordapp.com/attachments/568871319425515531/1148516683019989052/odin_quest.mp4)

Odin running on the Quest 2 - Charlie
[Github](https://github.com/cshenton/odin-quest)

![...](https://cdn.discordapp.com/attachments/568871319425515531/1149721652804976651/gl.gif)

finally got object parenting working, and playing around with some environment lighting - Akuspel

![...](https://cdn.discordapp.com/attachments/568871319425515531/1150173750784950432/gl.gif)

Some environment lighting and reflections that don't look completely horrible - Akuspel

![...](https://media.discordapp.net/attachments/568871319425515531/1155170232655163482/DiffuseLightingProgress.png)

Made some good progress porting/rewriting my Game in Odin. Here is a diffuse lighting test. - Moritz Falk

![...](https://cdn.discordapp.com/attachments/568871319425515531/1156352276034748526/sm.jpg)

Shadow Maps - Jesse

### Tools & UI [#](#tools--ui)

![...](https://cdn.discordapp.com/attachments/568871319425515531/1147751924372877373/image.png)

Spent today working on writing my own UI system - \_brian

![...](https://cdn.discordapp.com/attachments/568871319425515531/1156073726748655696/2023-09-26_00-34-52.mp4)

Line Input project: focused on making the input responsive, smooth and appealing - Volatus

[](https://cdn.discordapp.com/attachments/568871319425515531/1156741622151774208/Peek_2023-09-28_01-32.mp4)

My project for the Wheel Reinvention Jam is entirely in Odin, and it's been very delightful - Stvff

### Miscellaneous [#](#miscellaneous)

[![...](https://cdn.discordapp.com/attachments/568871319425515531/1156349244282773514/image.png)](https://git.xslendi.xyz/slendi/odin-efi)

Working on implementing UEFI in Odin! & it's open source right now for you to try! - slendi

[gitea](https://git.xslendi.xyz/slendi/odin-efi)

[](https://cdn.discordapp.com/attachments/1059202257175973888/1156650767365718106/2023-09-27_20-56-10.mp4)

added GOP (Graphics Output Protocol) support to UEFI implementation - slendi

>Source: https://odin-lang.org/news/newsletter-2023-09
