## Odin Changes in Detail [#](#odin-changes-in-detail)

### Dynamic Literals are now disallowed [#](#dynamic-literals-are-now-disallowed)

Hidden allocations in Odin are `[dynamic]` arrays and `map` literal declarations. These allocate memory without the user potentially knowing.

An example would be:

```odin
main :: proc() {
    test: map[int]string = {
        0 = "zero",
        1 = "one",
        2 = "two",
        3 = "three",
    }
}
```odin
Now this is not supported anymore and can only be turned on explicitly through the flag `#+feature dynamic-literals` to have backwards compatibility when necessary.

### `map_entry` builtin [#](#map_entry-builtin)

A new builtin to help in cases where you want to lookup if something exists in a map, return a pointer to the value or insert something new + return the final pointer in the map

Here is an example of it being used in the `core:strings` intern library. This is a call which has to be efficient as it may get called many times.
![map-entry-diff](/images/news-2025/Q1-map-entry-diff.png)

### SDL3 Support [#](#sdl3-support)

If you didn’t catch it yet, [SDL3 has been released](https://discourse.libsdl.org/t/announcing-the-sdl-3-official-release/57149).

Odin Vendor packages strive to support the most commonly used libraries, so of course we support SDL3 just like we did SDl2!

Here is the vendor package [vendor:SDL3](https://github.com/odin-lang/Odin/tree/master/vendor/sdl3)

### Further Changes [#](#further-changes)

Catch up on all changes on the [releases page](https://github.com/odin-lang/Odin/releases)

---

## Odin 7 Day Jam [#](#odin-7-day-jam)

Karl Zylinski has held a Game Jame in which the community had to create games with odin in 7 days!

Here are all the entries and the final winners listed on the itch.io page: <https://itch.io/jam/odin-7-day-jam/results>

---

## Community Projects [#](#community-projects)

### Odin C Bindings Generator [#](#odin-c-bindings-generator)

Look there is a new C Bindings generator!
This one does the popular approach which uses clang to output an ASST and then turns it into odin code.

<https://github.com/karl-zylinski/odin-c-bindgen>

### Sokol Hot Reload Template [#](#sokol-hot-reload-template)

Github: <https://github.com/karl-zylinski/odin-sokol-hot-reload-template>

### QRCode Generator [#](#qrcode-generator)

<https://github.com/jon-lipstate/qrcode>

---

## Socials [#](#socials)

### Nadako - Sokol Tutorials [#](#nadako---sokol-tutorials)

### Nadako - SDL3 Tutorials [#](#nadako---sdl3-tutorials)

### Handle Based Arrays Blog [#](#handle-based-arrays-blog)

<https://zylinski.se/posts/handle-based-arrays/>

---

## Community Games (Outside of the Game Jam) [#](#community-games-outside-of-the-game-jam)

&amp;lt;a href=https://jb-frog.itch.io/dont-pop-me-now&amp;gt;Don't Pop Me Now by jb\_frog, felix-u&amp;lt;/a&amp;gt;
&amp;lt;a href=https://igamemaker.itch.io/nuke-the-moon&amp;gt;Nuke The Moon by igamemaker&amp;lt;/a&amp;gt;
&amp;lt;a href=https://midnightmeat.itch.io/devil-raisd-the-storm&amp;gt;the Devil rais'd the storm by the Midnight Meat Society&amp;lt;/a&amp;gt;
&amp;lt;a href=https://nikola-stefanov.itch.io/bogwalker&amp;gt;Bogwalker by nik1oo&amp;lt;/a&amp;gt;

>Source: https://odin-lang.org/news/newsletter-2025-q1
