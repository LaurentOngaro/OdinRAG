A [Quine](https://wikipedia.org/wiki/Quine_(computing)) in [Odin](/):

```odin
package quine

import "core:fmt"

main :: proc() {
	fmt.printf("%s%c%s%c;\n", s, 0x60, s, 0x60)
}

s := `package quine

import "core:fmt"

main :: proc() {
	fmt.printf("%s%c%s%c;\n", s, 0x60, s, 0x60)
}

s := `;
```

>Source: https://odin-lang.org/news/quine-in-odin
