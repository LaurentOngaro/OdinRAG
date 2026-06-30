// <PROJECT_NAME> - entry point
//
// Compile and test with:
// odin run .
//
// Style notes:
// - 2 spaces for indentation (see odinfmt.json)
// - PascalCase for types, snake_case for procs
// - ctx: ^Context = default context.allocator (never nil)

package main

import "core:fmt"
import "core:os"

main :: proc() {
    fmt.println("Hello, Odin!")
    os.exit(0)
}
