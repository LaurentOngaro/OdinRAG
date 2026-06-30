# Public Odin gists and snippets

> 24 gists from the Odin community, curated via awesome-odin. All public, all MIT-style licensed.

## Sources

- [awesome-odin](https://github.com/jakubtomsu/awesome-odin)
- [Gist: jakubtomsu](https://gist.github.com/jakubtomsu) -- collision, curves, SDF, fontstash
- [Gist: karl-zylinski](https://gist.github.com/karl-zylinski) -- minimal Raylib, Box2D+Raylib, rect-cut, windows API
- [Gist: gingerBill](https://gist.github.com/gingerBill) -- Metal, MicroUI, D3D11, SDL2, OpenGL, WASM4
- [Gist: laytan](https://gist.github.com/laytan) -- UUID, Vulkan boilerplate, Raylib logger, LLDB visualization
- [Gist: others](https://gist.github.com) -- SorenSaket, cshenton, terickson001, Lperlind, p1xelHer0

## Download

```bash
python _Helpers/download_gists.py
```

## Catalogue

| Local file                          | Topic                                                                    | Author        | Source                                                                         |
| ----------------------------------- | ------------------------------------------------------------------------ | ------------- | ------------------------------------------------------------------------------ |
| `raylib-minimal.odin`               | Minimal Raylib entrypoint                                                | Karl Zylinski | [gist](https://gist.github.com/karl-zylinski/003bfb669d5a3050816e6d019e43fd97) |
| `box2d-raylib.odin`                 | 2D physics with Box2D + Raylib                                           | Karl Zylinski | [gist](https://gist.github.com/karl-zylinski/5ef25b68281b899acb1dd7774f035177) |
| `glfw-opengl-tutorial.odin`         | GLFW and OpenGL example with verbose comments and doc links              | SorenSaket    | [gist](https://gist.github.com/SorenSaket/155afe1ec11a79def63341c588ade329)    |
| `metal-in-odin.odin`                | Using Metal in Odin natively                                             | Ginger Bill   | [gist](https://gist.github.com/gingerBill/e1270f60a1739c266934599c2bee46f5)    |
| `3d-collision-raylib.odin`          | 3D FPS player movement with triangle collision                           | Jakub Tomsu   | [gist](https://gist.github.com/jakubtomsu/9cae5298f86d2b9d2aed48641a1a3dbd)    |
| `block-allocator-gpu.odin`          | GPU heap suballocator based on Sebastian Aaltonen's Offset Allocator     | cshenton      | [gist](https://gist.github.com/cshenton/d8db9bded49706ed4b28adb9bd937fcb)      |
| `octahedral-mapping.odin`           | Sphere and Hemisphere Octahedral mapping visualization                   | Jakub Tomsu   | [gist](https://gist.github.com/jakubtomsu/e614bf152a7147c4519149270b9266b6)    |
| `microui-sdl2-demo.odin`            | MicroUI + SDL2 demo                                                      | Ginger Bill   | [gist](https://gist.github.com/gingerBill/5bbcca224bf8d9dcd09dde38b2567d10)    |
| `microui-raylib-demo.odin`          | MicroUI + Raylib demo                                                    | Ginger Bill   | [gist](https://gist.github.com/gingerBill/c7a91318bd7b3be96d63d428b24d19ea)    |
| `sdl2-opengl-demo.odin`             | Simple SDL2 + OpenGL demo                                                | Ginger Bill   | [gist](https://gist.github.com/gingerBill/b03c2ea6ed693034a609e56076fda3dc)    |
| `d3d11-in-odin.odin`                | Simple D3D11 example                                                     | Ginger Bill   | [gist](https://gist.github.com/gingerBill/b7b75772f92c5511a9cd3ca2e28eca37)    |
| `vulkan-example.odin`               | Vulkan-tutorial example in Odin                                          | terickson001  | [gist](https://gist.github.com/terickson001/bdaa52ce621a6c7f4120abba8959ffe6)  |
| `minimal-metal-window.odin`         | Minimal Cocoa Window with Metal API                                      | Lperlind      | [gist](https://gist.github.com/Lperlind/1bb993a1c0f1acdd49080fd4852f95c5)      |
| `d3d12-triangle.odin`               | Single-procedure D3D12 triangle example                                  | Jakub Tomsu   | [gist](https://gist.github.com/jakubtomsu/ecd83e61976d974c7730f9d7ad3e1fd0)    |
| `uuid-v4.odin`                      | UUID v4 Generator                                                        | laytan        | [gist](https://gist.github.com/laytan/9053ea979bdbc5ebb4bf66d4caf5c402)        |
| `wasm4-bindings.odin`               | WASM-4 Bindings for Odin                                                 | Ginger Bill   | [gist](https://gist.github.com/gingerBill/9a6c0a6f0a34a147ff82e9f6047db2ac)    |
| `raylib-odin-logger.odin`           | Raylib logging callback to Odin logger                                   | laytan        | [gist](https://gist.github.com/laytan/e411288bc622eaf09832e752b31c9bc8)        |
| `glfw-vulkan-boilerplate.odin`      | GLFW & Vulkan boilerplate for Drawing a Triangle                         | laytan        | [gist](https://gist.github.com/laytan/ba57af3e5a59ab5cb2fca9e25bcfe262)        |
| `lldb-visualization.odin`           | Python script for slice, map, and string formatting in LLDB              | laytan        | [gist](https://gist.github.com/laytan/a94c323a84cef7bcfbdf6d21987fd5a9)        |
| `realtime-collision-detection.odin` | Port of 3D collision procedures from 'Realtime Collision Detection' book | Jakub Tomsu   | [gist](https://gist.github.com/jakubtomsu/2acd84731d3c2613c91e40c2e064ffe6)    |
| `windows-api-open-window.odin`      | Minimal example of opening a window using core:sys/windows               | Karl Zylinski | [gist](https://gist.github.com/karl-zylinski/f8761856593776014c9de3368437e790) |
| `rect-cut.odin`                     | Procedures for cutting up a rect, useful for IMGUI layouting             | Karl Zylinski | [gist](https://gist.github.com/karl-zylinski/ffccda0babb7e05b0657bf0acd3f1a99) |
| `sdl-sokol-d3d11.odin`              | Minimal D3D11 + swapchain setup with SDL and sokol_gfx                   | Jakub Tomsu   | [gist](https://gist.github.com/jakubtomsu/470e33d477936ba9c772e2395f661b5f)    |
| `cubic-curves.odin`                 | Sample of various cubic curves (bezier, hermite, catmull-rom, b-spline)  | Jakub Tomsu   | [gist](https://gist.github.com/jakubtomsu/577f2375aad587e09c2d75e085fef87f)    |
| `miniaudio-playback.odin`           | Play audio files from memory with Odin #load                             | p1xelHer0     | [gist](https://gist.github.com/p1xelHer0/abed4728096ea3a88af7802cbe46cf08)     |
