## What’s been going on in July [#](#whats-been-going-on-in-july)

Work has officially started on the new custom backend for Odin using [Tilde](https://github.com/RealNeGate/Cuik/tree/master/tb). This will be an alternative to the current LLVM backend, and not a replacement to it. In case you didn’t know, Odin’s compilation speed is actually quite quick, but LLVM slows down everything. Around ~90% of the compilation time is spent on LLVM.

Tilde is estimated to reduce Odin compile times by an order of magnitude at a minimum, aiding with the quick development of your programming in Odin.

Try out the compiler flags `-show-timings` or `-show-more-timings` to get details on your compilation times - you’ll find that LLVM usually takes up most time. Why optimize other stages of the compilation when LLVM will bog down everything by ~90%?

[Yasser Arguelles Snape (NeGate)](https://github.com/RealNeGate) has been working on his own custom backend to replace LLVM. They have been developing a `C` compiler along with it, to better grasp the shortcomings of his custom backend.

GingerBill has been streaming some code sessions on [Twitch](https://www.twitch.tv/ginger_bill) - with backups being uploaded on [YouTube](https://www.youtube.com/c/GingerGames).

## New Bindings / Packages [#](#new-bindings--packages)

- [ldtk](https://github.com/jakubtomsu/odin-ldtk) bindings - `jakubtomsu (Jacob)`
- [jo](https://github.com/pJotoro/jo) “A stupidly easy to use library” - `pJotoro`
- [oui](https://github.com/Skytrias/oui) OUI Semi-Immediate UI port - `Skytrias`

## Showcase [#](#showcase)

Response to the ***Showcase*** section has been astonishing, so let’s continue in the same fashion.

We have a total of ***21*** videos / images to share this month, we’ll try splitting up by weeks to give a sense of *time*.

### Week 1 [#](#week-1)

Waterfall Spectrum Analyzer for the Adalm-Pluto Software Defined Radio - Stvff
Github

### Week 2 [#](#week-2)

[](https://cdn.discordapp.com/attachments/568871319425515531/1126634151060181022/2023-07-06_18-53-40.mp4)

Applying shaders to nodes & caching properly - brda

[](https://cdn.discordapp.com/attachments/585072899250192404/1132778914494812262/tankers_recording.mov)

&amp;lt;a href=https://ncharlie.itch.io/tankers&amp;gt;Tankers by ncharlie&amp;lt;/a&amp;gt;

[](https://cdn.discordapp.com/attachments/585072899250192404/1131330584485036082/2023-07-19_22-55-41.mp4)

&amp;lt;a href=https://rehkitzdev.itch.io/dont-break&amp;gt;Don't break by rehkitzdev&amp;lt;/a&amp;gt;

[](https://cdn.discordapp.com/attachments/568871319425515531/1128552523771428924/simplescreenrecorder-2023-07-11_23.02.30.mp4)

GPU accelerated fractal binary tree with rotation & scale - ElegantBeef

![...](https://cdn.discordapp.com/attachments/568871319425515531/1129105832215326750/image.png)

"After a day of frustration and tears, here we have functional multi mesh rendering with Assimp, OpenGL and SDL2" - Akuspel

![...](https://cdn.discordapp.com/attachments/568871319425515531/1129387863033778176/image.png)

Object transforms, 3D gizmo, multiple shaders - Akuspel

### Week 3 [#](#week-3)

![...](https://cdn.discordapp.com/attachments/568871319425515531/1130852733117812796/ohyeah.jpg)

Quixel scanned mesh import works now - Jesse

[](https://cdn.discordapp.com/attachments/568871319425515531/1131990006693625906/dialogue_and_editor.mp4)

Cat game progress - NPCs, Custom Objects, Editor Work Undo/Redo - karl\_zylinski

![...](https://cdn.discordapp.com/attachments/568871319425515531/1132501150847991839/image.png)

Vulkan Triangle using a custom platform layer - OrigamiPete

[](https://cdn.discordapp.com/attachments/568871319425515531/1132752374587457626/20230723_205046.mp4)

&amp;lt;a href=https://coedoo.itch.io/gold-and-stone&amp;gt;Gold and Stone by Coedoo&amp;lt;/a&amp;gt;

### Week 4 [#](#week-4)

![...](https://cdn.discordapp.com/attachments/568871319425515531/1130852733117812796/ohyeah.jpg)

Who needs Nanite when you've got parallax mapping - Jesse

![...](https://media.discordapp.net/attachments/568871319425515531/1132974873145253949/image.png)

Tilde Hellope! - gingerBill

[](https://cdn.discordapp.com/attachments/568871319425515531/1134716807136153630/contour_wip02.mp4)

Vector Editing App - varomix

![...](https://media.discordapp.net/attachments/568871319425515531/1134904460708155492/image.png?width=1130&height=552)

writing a UE save format reader for fun - Jeroen

[](https://cdn.discordapp.com/attachments/585072899250192404/1135989264723755168/Piano_Thing.mp4)

Keyboard Midi Visualizer with raylib - HitchH1k3r

[](https://cdn.discordapp.com/attachments/568871319425515531/1134974738851184792/hot_reloading.mp4)

Hot Level Reloading - CasualKyle

![...](https://cdn.discordapp.com/attachments/568871319425515531/1135304074322006106/image.png)

Procedural Generation of levels - Francis\_the\_cat

[](https://cdn.discordapp.com/attachments/568871319425515531/1135617784949252236/new6.mp4)

Vector -> (M)SDF Generation Tool - Skytrias

>Source: https://odin-lang.org/news/newsletter-2023-07
