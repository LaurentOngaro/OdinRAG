# A Quine in Odin

2019-03-10

A [Quine](https://wikipedia.org/wiki/Quine_(computing)) in [Odin](/odin):

```odin
package quine

import "core:fmt"

main :: proc() {
	fmt.printf("%s%c%s%c;\n", s, 0x60, s, 0x60);
}

s := `package quine

import "core:fmt"

main :: proc() {
	fmt.printf("%s%c%s%c;\n", s, 0x60, s, 0x60);
}

s := `;
```

>Source: https://www.gingerbill.org/article/2019/03/10/quine-in-odin
