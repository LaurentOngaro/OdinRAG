---
source: github-releases
repo: odin-lang/Odin
tag: consolidated
date: 2026-11-17
type: changelog
status: active
version: 1.0.0
lastUpdated: "2026-11-17T15:50:56Z"
updatedBy: "MiniMax-M3 (Kilo Code)"
tags: [OdinRAG, kb, source/official, changelog, odin]
---

# Odin Changelog (consolidated, 20 releases)

> Generated from the [odin-lang/Odin releases](https://github.com/odin-lang/Odin/releases) feed on 2026-11-17.
> Re-run `python _Helpers/scripts/scrapers/scrape_odin_changelog.py` to refresh.

## dev-2026-11a - 2026-11-03

**dev-2026-11a hotfix** by Kelimion - <https://github.com/odin-lang/Odin/releases/tag/dev-2026-11a>

Contains [dev-2026-11](https://github.com/odin-lang/Odin/releases/tag/dev-2026-11) release + hotfix addressing an enum clash between BNG + LZ4.

---

## dev-2026-11 - 2026-11-03

**dev-2026-11** by Kelimion - <https://github.com/odin-lang/Odin/releases/tag/dev-2026-11>

## BREAKING Changes

- [#7724] `core:fmt`: Make `fmt` pad widths with spaces unless the 0 flag is given, keeping to C-style `printf` rules

- [#8153] `core:compress`: Deflate compression added, rewritten Inflate, core:compress overhaul.

* Speed (Silesia, 5950X / M4 Pro):

  - Inflate: 2.1-2.2x the old core inflate; 1.26-1.33x / 1.39-1.46x `vendor:zlib` 1.3.2.

  - Deflate L1-9: 1.54-2.43x / 1.18-1.86x zlib 1.3.2, sizes 3% smaller to 1.1% larger than `vendor:zlib`.

  - Level 10 (new `Best`): 0.64% smaller than zlib -9 over the corpus, at about 1.4x the time of level 9. Adds 3-byte matches and cost-based block splitting.

  - `Image.pixels` and `Context.output` are `[dynamic]byte` (was `bytes.Buffer`);

  - `Image` savers take `^[dynamic]byte`.

  - `core:compress/zlib` and `gzip` are `@(deprecated)` wrappers around `core:compress/deflate`.

  - Removed: The old LSB bit-reader helpers in `core:compress`, `COMPRESS_OUTPUT_ALLOCATE_MIN`, and the unused error values `Resize_Failed`, `Payload_Size_Exceeds_Max_Payload`, `Unsupported_Compression_Level` and `Inflate_Error`.

## New Language Features

- [#7809] General Feature Improvements

  - `@(align=N)` for variables: globals, locals, `@(static)`, `@(thread_local)`

  - New intrinsics: `return_address`, `frame_address`, `stack_pointer`, `address_of_return_address`

- [#7816] Rejects atomics that LLVM cannot lower, and checks atomic memory orderings across the whole program (which many C/C++ compilers do not do).

  - `#+analysis`, e.g. `#+analysis escape !atomic`

  - `@(futex=.Wait)` / `@(futex=.Wake)`, marking `core:sync`'s futex procedures, so the analysis checks futex words instead of skipping them.

## New Compiler Improvements

### Speedups

- [#7823] Debug Info Improvements. Both faster to generate and easier to read in debuggers.

  - Each record type is defined once, in one of eight debug types modules generated in parallel; every other module only forward declares it.

  - Debug info is finalized per module in parallel, and work for unused debug info is skipped.

- [#8070] Add a fast path to `for in` over `string` and `string16`

- [#8136] Inline small run-time-length `mem_copy` at `-o:speed`

- [#8146] Drop redundant zeroing of literals and declarations

### High Impact

- [#8006] Add Android support: `core`, `NDK` and `Java` bindings, and `APK`/`AAB` bundling

  - Adds Android as a target: `-subtarget:android` for arm64, arm32, amd64, and i386, at API level 29 or higher.

    - An app starts at `main`, just like on every other platform.

    - `odin bundle android` makes a signed APK or AAB.

  - Android target triples now name a vendor. Without one, LLVM got the ABI wrong (x86 stack alignment, arm64's x18).

  - Links use `--no-undefined`: a symbol newer than the target API level is a link error.

  - `odin bundle android` runs aapt2, adds a prebuilt `classes.dex`, aligns, and signs.

  - `examples/android`: a minimal app, with how to `build`, `bundle`, and `run` it.

  - A CI job that `check`s, `build`s , and `bundle`s it for all four ABIs.

  - (more)

- [#7878] Update Windows' version of LLVM to 22.1.8

- [#7809] General Feature Improvements

  - Matrices now align to the largest power of two dividing their column (row if `#row_major`) stride, capped at 16, still with no padding (e.g. `matrix[4, 4]f32` is 16-byte aligned)

  - Fixed-capacity `[dynamic; N]T` is now padded to its full size when `T` is over-aligned

  - Naming a `@(deprecated)` procedure in a procedure group no longer warns; only a call that selects it does

  - `#const` parameters can now use their default values

- [#7802] Flow-based Escape Analysis of Stack Memory + Show where parapoly procedures and records were instantiated in errors within them

  - Tracks where stack memory can end up

  - Replaces the bodgy syntactic approach that `check_unsafe_return` did previously

  - An explicit `rawptr`/`uintptr` conversion or `transmute` opts out

  - Interprocedural

  - The entry point is skipped for executables

  - Store warnings suggest clearing the store

- [#7816] Rejects atomics that LLVM cannot lower, and checks atomic memory orderings across the whole program (which many C/C++ compilers do not do).

  - Atomic Ordering Analysis. On by default, `-no-atomic-analysis` to disable

  - Warns on `.Release` writes only ever loaded `.Relaxed`, and `.Acquire` reads only ever stored `.Relaxed`, per global, static, or struct field.

  - `-vet-atomic-access` (opt-in) errs on plain reads of what is accessed atomically, outside of `core:sync` locks.

- [#7819] Improved Atomic Analysis: Fences, Weak Compare-Exchange, Futex Wakes, and Volatile Memory Access

  - Fences: Only order what they are reached after `(acquire)` or before `(release)`, including across calls.

  Warnings:

  - Weak compare-exchange with its second result unused.

  - Futex woken before it is written.

  - Atomics on a local nothing else can access; suggests `volatile_*`.

  - `volatile_*` on what is accessed atomically.

  - `atomic_signal_fence` where `atomic_thread_fence` would pair.

  Errors:

  - Atomics on what may be misaligned, e.g. a `u32` converted to `^u64`.

- [#7823] Debug Info Improvements. Both faster to generate and easier to read in debuggers.

  - Procedures and globals are named by package and enclosing procedure (`pkg::proc`, `pkg::[file.odin]::name` for file-private, `proc@line` for literals).

  - Polymorphic instances share one name; exported and custom link names are kept.

  - `typeid` is an enum of the type table, so debuggers show which type it is

  - `bit_set`s are flag enums on DWARF.

  - RAD Debugger views for unions, `string16`, `#soa` and other generated types; big-endian types keep their names in CodeView, and the integer ones are byte-swapped by RAD views.

  - gdb and lldb pretty printers (`base/runtime/odin_debugger.py`) for `map`s, `union`s, strings, slices, dynamic and `#soa` arrays, allocators and `any`. T

    - They load automatically: embedded in `.debug_gdb_scripts` on ELF, copied into the `.dSYM` on macOS.

  - Optimized procedures are marked, and assignment tracking is on unless `-o:none`, so more variables keep a location.

  - DWARF 5 on Darwin and Linux, unique type identifiers, and MD5 file checksums on LLVM 22+.

- [#7828] Atomic analysis: add `@(synchronizes=...)``, wrapper inference, and more atomic memory model checks

  - Fences in callees and callers count; fences in other branch arms don't

  - Error on atomic writes to `@(rodata)`

  - Warn on atomics on an unshared `@(thread_local)`

  - Warn on Dekker-style store/load pairs not ordered by `.Seq_Cst`

  - Warn on mixed-size atomics on one location

  - `-vet-atomic-access`

    - Checks plain writes too

    - `@(synchronizes=<Atomic_Memory_Order>)` and `@(synchronizes_shared=...)` replace the lock-name heuristic

    - Unmarked procedures are inferred from their calls

  - Please read the PR's description for how Odin's atomic memory ordering analysis works

- [#7848] Error Reporting/Recovery Improvements for Editors and External tooling (e.g. OLS)

  - `-overlay:<file>`: Go-style JSON overlays for unsaved buffers

  - `odin check <dir> <dir2>`: Check several packages at once

  - `odin check -export-semantics:<json|cbor> -export-semantics-file:<file>`

  - (more)

- [#7871] Record the enum field an implicit selector picks in `-export-semantics`

- [#7876] General fixes in the odin parser to improve `-export-semantics`

- [#7877] More Type Inference Improvements

- [#7874] Publish the backend's entity names atomically so parallel modules never read a half-written name

- [#7886] Reduce Type and Polymorphic instantiation Memory Usage in the Checker

- [#7887] Reduce Checker Memory Usage

  - `Scope`: 568 -> 104 bytes

  - AST nodes: 40 bytes smaller

  - Fewer constant-value allocations

  - `DeclInfo`: 560 -> 312 bytes

  - `odin check` now totals around 16.5% less memory on large projects, and is also a smidge faster

- [#7905] Bounds Checking Analysis: Leave out bounds checks that are proven to pass

  - Elides bounds checks that are proven will pass by an earlier check, see PR for details

- [#7828] Atomic analysis: add `@(synchronizes=...)``, wrapper inference, and more atomic memory model checks, adds `-vet-atomic-access`

- [#8068] Only add type info for union type assertions when the assertion can panic

- [#8101] Add `enum` support to `#config` and properly check types

- [#8162] Fix Windows i386 executables, DLLs and threading. Add to CI to catch 32-bit cleanliness issues.

### General fixes and improvements

- [#7795] Fixes #7737 and #7727: Regressions caused by temp copy of underaligned values

- [#7796] Parapoly: Fix regression with proc group containing parapoly enumerated array specialization

- [#7800] Make `@(static)` locals visible in the debug info

- [#7761] `LLVMBr` opcode split to `LLVMCondBr` and `LLVMUncondBr` in LLVM >= 23

- [#7068] Fixes `(@fast_math)` plumbing to LLVM

- [#7805] Fix #7798: Sort `link_names` with `Procedures` before `ForeignProcedures`

- [#7804] Make `vendor` collection optional

- [#7807] Upgrade `vendor:zlib` to 1.3.2

- [#7808] Fix #7806: `-lto:thin` / `-lto:thin-files` no longer defaulted to `-linker:lld` on Windows

- [#7814] Update `-vet` flag help message

- [#7821] Fix #7820: Keep only the origins of what a call's flow loads from memory of an unknown type in the escape analysis

- [#7826] Fix debug info printers

- [#7825] Fix LLVM backend bugs:

  - core:simd/x86: replace 35 intrinsics that LLVM has removed (link errors like `undefined reference to llvm.x86.sse41.pmaxsb`) with generic ops, as clang's headers do.

  - core:simd/x86: fix `_mm_cvtsd_ss`, `_mm_cvtss_sd`, `_mm_prefetch` and `__rdtscp` ("Intrinsic has incorrect argument type"), and AVX wrappers that did not compile.

  - A multi-value call in a matrix literal hit an assertion. In a #simd literal it put later values in the wrong lanes.

  - Slicing a `[dynamic; N]T` with constant indices skipped the bounds check against its length.

  - `string16` map keys hashed only half their bytes. `cstring16` keys crashed.

  - Casting an unspecialized polymorphic procedure, e.g. `rawptr(avl.init_cmp)`, is now an error. It used to hang the build or give nil.

  - `rawptr(assert)` with `-disable-assert` failed with "missing procedure 'assert'".

  - `odin test -debug` crashed when build tags exclude every file, e.g. test_issue_7547.odin off Windows.

  - tests/issues/run.sh: pass `-microarch:native` to the two `split_globals` lines, as every other line does. Without it the NetBSD job fails whenever its VM gets a CPU older than x86-64-v2.

- [#7824] Fix the debug info for indirect parameters that get a callee copy

- [#7837] Fix the compiler incorrectly treating the alignment of address storage as the alignment of the address

- [#7841] Enable `evex512` with explicit AVX-512 target features

- [#7829] Fix LLVM asm imm64

- [#7840] Let `%k` registers fill opmask slots in `asm` templates

- [#7845] Merge `@(static)` and `@(thread_local)` locals across modules

- [#7831] Find an `any`'s named type in `lldb` on DWARF

- [#7842] Fix LLVM Objc varargs

- [#7847] Fixes the compiler incorrectly treating the alignment of address storage as the alignment of the address, part 2

- [#7861] Fix escape analysis for init statements of ranged loops

- [#7872] Fix compiler error from alias of named union

- [#7865] Fixes array loads alignment in conversions and matrix-vec multiplication

- [#7879] Fixes alignment of `#packed` field zero stores

- [#7880] Use newer LLVM C API where it helps; exact float constants

- [#7884] Give switch range bounds the type of the switch tag

- [#7893] Fixes #7817: Skip variant checking for a union instantiated with polymorphic operands

- [#7892] Fixes #7889: Compiler panic when indexing or selecting through a swizzle

- [#7891] Fixes #7741: Compiler segfault for `foo :: proc() -> (foo, i32)`

- [#7897] Fixes field access alignment in custom `#align` structs/raw unions

- [#7881] Fixes #7875 + #7471: Hash `matrix` and `#simd` map keys with float elements

- [#7896] Fixes #7781: Test a wide shift amount against the bit width before narrowing it

- [#7900] Never re-check a constant assigned to a union variant (procedure literals within it had their bodies checked twice)

- [#7907] Fix `unreachable` built-in errors

- [#7919] Fixes alignment of `union` variant loads with custom `#align`

- [#7944] Fixes by-reference type switches on custom `#align` unions

- [#7933] Fix TLS segment underalignment in ARM64 Bionic (Android subtarget)

- [#7955] Defer checking asm template bodies and fix target feature checks

- [#7952] Fixes #7948: Asm instruction-form selection

- [#7956] Fixes #7938: Propagate viral state flags through `or_else`, `or_return` and `or_branch`

- [#7988] Fixes #7975 + #7976: Unify the types of constant arguments to `min`, `max` and `clamp`

- [#7981] Fixes #7560: Fix runtime indexing of a global matrix

- [#7984] Fixes #2039: Follow 'using' pointer fields when converting to a subtype

- [#7982] Fixes #7980: Explicitly handle missing receivers in Objective-C selector calls instead of asserting

- [#7974] Fix SIMD shift LLVM error and negative overflow behavior

- [#7994] Fixes transmuting from aggregate types less aligned than the destination type

- [#7842] Fix/llvm objc varargs

- [#8022] Fix iterating over a map index expression with a missing key

- [#8029] Apply sanitizer attributes to procedure literals

- [#8004] Add `@(fast_math)` to polymorphic procs

- [#7997] Debug info: Fix `or_return` debug location of the "continue_block"

- [#7993] Make `min(T) / -1` wrap instead of trapping on x86-64

- [#8048] Track usage of Objective-C frameworks via used methods

- [#8075] Fixes #8074: Do not run the `defer`s again from an exit within a `defer` in the escape analysis

- [#8078] Fixes #8072: Emit `return` cleanup before a `#must_tail` call

- [#8082] Specialize polymorphic procedures passed to `$` procedure parameters

- [#8100] Fix race caused by `thread_pool_queue_push`

- [#8110] Fix wrong code when asm template clobbers overlap pinned operands

- [#8090] Allow MSVC-mangled link names starting with `?` and `@`

- [#8084] Fix the warning that happens when you return `#load`'ed strings

- [#8007] Fixes #7327: codegen not honoring `max_simd_align`

- [#8121] Fix under-aligned addresses passed by pointer and in `any`

- [#8123] Fixes #5335: Fix constant casts to `any`; reject any constants

- [#8122] Copy small indirect params by field to avoid stalls

- [#8127] Enable RVO for `x := call()` and fix sret-ignoring calls

## New Packages

- [#7963] `core:diff`

  - **Inputs:**

    - Slices of any comparable type

    - Slices with your own equality and hash

    - Text by lines, words, or runes

    - Text can ignore carriage returns, trailing whitespace, all whitespace, or case

  - **Algorithms:**

    - `.Myers` (the default, with a cost cap)

    - `.Minimal`

    - `.Histogram`

    - `.Ratcliff_Obershelp`

  (And more. Read PR for more information.)

- [#8172] `core:image/bng`, an implementation of the [BNG](https://bngformat.org) format.

- [#8157] `core:compress/lz4`, a cleanroom implementation of the [LZ4](https://lz4.org) compression algorithm.

## Package Improvements

### Speedups

- [#7860] `core:sync/chan`: Lock-free buffered channels, unbuffered handoff, timeouts

- [#8080] `core:encoding/json` General improvements and speedups.

- [#7885] `core:encoding`, `core:strconv` and others: Simplify `strings` `io` `fmt` `strconv` interactions

- [#8143] `core:hash`: Vectorize Adler-32 using `core:simd`

- [#8148] `core:fmt`: Speed up; fix its byte counts; fix `flush=false`

- [#8128] `core:slice`: Remove redundant zeroing when allocating

- [#8150] `core:hash`: Add hardware-accelerated CRC32

- [#8153] `core:compress`: Deflate compression added, rewritten Inflate, core:compress overhaul.

* Speed (Silesia, 5950X / M4 Pro):

  - Inflate: 2.1-2.2x the old core inflate; 1.26-1.33x / 1.39-1.46x `vendor:zlib` 1.3.2.

  - Deflate L1-9: 1.54-2.43x / 1.18-1.86x zlib 1.3.2, sizes 3% smaller to 1.1% larger than `vendor:zlib`.

  - Level 10 (new `Best`): 0.64% smaller than zlib -9 over the corpus, at about 1.4x the time of level 9. Adds 3-byte matches and cost-based block splitting.

### High Impact

- [#7940] `core:sys/darwin`: Add all of the Objective-C frameworks

  - `NSError**` methods return `(value, err)`

  - Flag enums are `bit_set`s; zero, combined and multi-bit field values are constants (e.g. `UI.ViewAnimationOptions_CurveEaseIn`)

  - C-style prefixes are stripped from enum members (e.g. `kSecPaddingNone` is `.None`)

  - `import NS "vendor:darwin/AppKit"` gives AppKit and Foundation under one `NS`

- [#8050] `vendor:OpenEXRCore`: Update OpenEXRCore to 3.5.2

- [#8051] `vendor:OpenEXRCore`: Add universal macOS binary for OpenEXR 3.5.2

- [#8035] `vendor:curl`: Updated to 8.23.0. Rebuilt to add Windows support for `zlib`, `brotli`, `zstd` and `HTTP/2`

- [#8006] Add `Android` support

  - Fixes for bionic, Android's libc.

  - `core:sys/linux` makes only the system calls Android's seccomp filter allows.

  - `core:net` resolves through netd.

  - `os.args`, the working directory, user directories, `sys/info`'s version, and stdio to logcat get Android defaults.

  - `core:os` reads APK assets under `/android_asset`.

  - `core:sys/android` The NDK's C APIs, generated from its headers.

  - `core:sys/android` `native_app_glue` runs `main` on its own thread, once per process.

  - `core:sys/android` JNI and asset helpers.

  - `core:sys/android` Constants typed as `enum`s, `bit_set`s, and `bit_field`s, here and in `vendor:android`.

- [#8124] `base:runtime`: Use `wmain` on Windows, enforcing `os.args` to be UTF-8

- [#8155] `core:image/png`: Add `PNG` saving and fixes/adds `core:image` helpers

- [#8159] `core:image/jpeg`: Rewrite the decoder (much faster), add progressive JPEG

- [#8179] `core:compress/lz4`: Enforce output limits, bound reservations, bounded growth

### Runtime changes

- [#7789] `base:runtime`: Context-aware bounds check handling

- [#7989] `base:runtime`: Fix #7979: Handle negative reserves for maps and dynamic arrays

- [#7789] `base:runtime`: Context-aware bounds check handling

- [#7989] `base:runtime`: Handle negative reserves for maps and dynamic arrays

- [#7816] `base:intrinsics`: Relaxed orderings which paired with nothing in `core:nbio` mpsc, `core:container/pool`, `Atomic_Cond`, and `futex_wait`'s early load.

- [#7810] `base:runtime`: Fixes #7790: (Re-)Add optional allocator error to 'map_insert'

- [#8077] `base:runtime`: Fixes #8076: `strings.compare` returns `-1` for two equal empty strings

- [#8109] `base:runtime`: Fixed #7675: Add ARM64 no-crt entry point

- [#8111] `base:runtime`: Speed up `udivmod128` and fix its zero-divisor results

- [#8059] `base:runtime`: Add `non_zero_make`

### General fixes and improvements

- [#7801] `core:encoding/hex`: Fix #7779: Behave well on errors

- [#7760] `core:simd/x86`: Implement simd x86 avx2 intrinsics set

- [#7809] `core:sys/llvm`: Fixed the bindings for current LLVM, added the missing ones, and added `f16` variants

- [#7815] `core:sys/llvm`: Adds binding for `llvm.fake.use`

- [#7616] `core:strconv`: Fix #7608: `strconv.parse_int` no longer indicates success on overflow

- [#7883] `core:strconv`: Moves SWAR floats parsing behind the `STRCONV_FAST_FLOAT` `#config`

- [#7818] `core/crypto/_sha3`: Reset `keccak_round_start` in `init`

- [#7811] `core:encoding/base64`: Fix #7763: base64 decoder edge case

- [#7832] `core:text/edit`: Fix "word right" translation

- [#7848] `core:odin/parser`: Error Reporting/Recovery Improvements for Editors and External tooling (e.g. OLS)

- [#7870] `core:math/big`: Fix integer destruction

- [#7898] `core:sys/linux`: Add 'unspecified' linux socket protocol

- [#7904] `core:fmt` Fixes #7903: width specifiers now use rune count as previously documented, not byte count.

- [#7786] `core:simd/arm`: Implement SIMD Arm Neon intrinsics set

- [#7846] `core:simd/x86`: Implement SIMD x86 AVX2 intrinsics set

- [#7922] `core:crypto/_chacha20`: Add explicit `@enable_target_feature` annotations

- [#7925] `core:unicode`: Generate case mapping tables from the UCD

- [#7923] `core:encoding/json`: Fix use after scope

- [#7930] `core:math/rand`: Fixed `choice_enum` not behaving deterministically with set seed

- [#7912] `core:simd/x86`: Implement SIMD x86 AVX2 gather intrinsics

- [#7962] `core:mem`: Fix and improve `resize` in allocators

- [#7977] `core:simd/x86`: Implement SIMD x86 SSE cleanup

- [#8014] `core:encoding/endian`: Add arbitrary-width (multiple of 8 bit) `get` and `put`

- [#8034] `core:math/big`: Fix #8033: Recursive division returned wrong results

- [#8027] `core:encoding/base64`: Fix additional decoder edge cases

- [#8015] `core:strconv`: Fast float formatting with Żmij

- [#8043] `core:encoding/xml`: Fix #8030: Mishandling of CDATA.

- [#8056] `core:sys/windows`: CPU set bindings

- [#8064] `core:sys/info`: Fix handling of empty CPU brand string

- [#8065] `core:os`: Fix #8063: `current_process_info({.Command_Args})` returns no arguments on Windows

- [#8036] `core:debug/trace`: Fixed type of `IMAGEHLP_LINE64.FileName`, and added `IMAGEHLP_LINEW64`

- [#8060] `core:simd/x86`: Implement SIMD x86 SSE2 cleanup

- [#8099] `core:nbio`: Fix Linux timeout crashing entire process

- [#8104] `core:simd/x86`: Implement the rest of SIMD x86 SSE cleanup

- [#8085] `core:unicode/utf8`: Fix `utf8string.at`

- [#8116] `core:strings`: Remove redundant zeroing when allocating

- [#8120] `core:strings`: Fix #8119: `prefix_length` was broken for 2- and 3-byte runes

- [#8126] `core:simd/x86`: Implement SIMD x86 SSE4a

- [#8125] `core:sys/windows`: Add win32 setupapi bindings

- [#8137] `core:encoding/json`: Unprivate marshal procs

- [#8142] `core:text/match`: Fix `%g` in only matching hex digits

- [#8147] `core:testing`: Fix trap and signal handling on Windows

- [#8173] `core:compress/deflate` Further hardening: Enforce output limits, bounded growth, cheaper fixed blocks

### Vendor packages

- [#8006] `vendor:android`: Add `Android` support

  - The other NDK libraries, generated from their headers.

  - `vendor:android/java`, generated from `android.jar`.

  - Vulkan, GLES, AAudio, and miniaudio on Androi

- [#8055] `vendor:box2d`: Update to 3.2.0

- [#7734] `vendor:box3d`: Fix quaternion `RotateVector` and `InvRotateVector` math

- [#8095] `vendor:box3d`: Fix Recording signatures

- [#8131] `vendor:cgltf`: Update to 1.15

- [#8046] `vendor:commonmark`: Update to 0.31.2

- [#7844] `vendor:darwin/Metal`: Fixed link for `NSRunLoop` documentation in Metal package README

- [#8135] `vendor:directx/dxc`: Update to 1.9.2609

- [#8054] `vendor:enet`: Update to 1.3.18

  - Packet sending performance improvements.

  - MTU negotiation fixes.

  - A checksum alignment fix.

  - The checksum table is no longer built by dynamic initialization.

  - A new `ENET_SOCKOPT_TTL` socket option.

- [#8133] `vendor:glfw`: Update to 3.5.1

- [#8053] `vendor:kb_text_shape`: Update to 2.28g

- [#8037] `vendor:lua/*`: Fix lua bindings under wasm

- [#8052] `vendor:miniaudio`: Update to 0.11.25

- [#8130] `vendor:miniaudio`: Update to 0.11.26

- [#8129] `vendor:OpenEXRCore`: Update to 3.5.3

- [#8057] `vendor:portmidi`: Update to 2.0.8

- [#8058] `vendor:sdl2`: update to latest

- [#8058] `vendor:sdl3`: update to latest, add `SDL3_net` and tests

- [#8045] `vendor:stb`: Update `stb_image`

- [#8132] `vendor:raylib`: Update to 6.2, raygui to 5.0

- [#7836] `vendor:wgpu`: Add `BlendOperation.Undefined` to match `webgpu.h`

## Miscellaneous

- [#7797] Adds regression tests for alignment work in #7720

- [#7812] Fix spurious error in `test_issue_7547`

- [#7827] Optimize hot paths that are slow in CI

- [#7859] Improve experience with shell scripts for testing

- [#7894] Make `tests/core/nbio/net.odin` poll test more reliable

- [#7895] Make downloading test assets skippable

- [#8026] Fixes #8024: Update `bin\lld-link.exe` to match LLMV-C's version

- [#8044] Allow CI to exercise `vendor:stb` tests on the BSDs

- [#8041] CI test suite reliability fixes

- [#8069] CI stability fixes 2

- [#8066] Upgrade Lua CI test to 5.5

- [#8154] Add `SDL3_TTF` to `LFS`, overlooked earlier

- [#8158] Add digests for upcoming extended `JPEG` test suite

- [#8176] Fix CI issues

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2026-10...dev-2026-11

---

## dev-2026-10 - 2026-10-06

**dev-2026-10** by Kelimion - <https://github.com/odin-lang/Odin/releases/tag/dev-2026-10>

## New Language Features

- [#7664]: Allow `bit_set` to be backed by arrays of integers

## New Compiler Improvements

### Speedups

- [#7720]: LLVM Backend Performance Improvements to Reduce Compile Times Part 1

- [#7729]: LLVM Backend Performance Improvements to Reduce Compile Times Part 2

- [#7747]: Compiler Performance Improvements to Reduce Compile Times Part 3

- [#7685]: Complete Parapoly Rewrite + Race condition fixes

- [#7694]: Make global checking codegen order-independent

- [#7686]: Parse integer literals without allocating per digit and reject non digits in their exponent

- [#7739]: Make `radlink` default linker on Windows

- [#7701]: Multithread The Entire Semantic Checker

- [#7728]: `map` performance improvements

### General fixes and improvements

- [#7654]: Experimental support for cross-linking Windows executables

- [#7788]: Add the new `-windows-sdk-root` to the `odin help build` command

- [#7497]: Fix #7488: `-vet` error in `core_builtin_soa.odin` when appending multiple empty structs to `#soa[dynamic]`

- [#7500]: Fix #5851: Detect and error on chained `offset_of` expressions

- [#7505]: Apply mojibake magic to test runner, too

- [#7509]: Fix #7499: Add ctrl-c handler to `run_subprocess`

- [#7070]: Fix `vendor:ENet.Buffer` data/length ordering issue

- [#7524]: Fix alias `nullptr` ICE

- [#7528]: `intrinsics.type_elem_type()` added case for `Type_FixedCapacityDynamicArray`

- [#7531]: Improve error message for constant indexing

- [#7530]: `simd_abs` codegen improvement + fix for unsigned integers

- [#7545]: Fix #6917: LLVM IR `va_arg` instruction uses wrong stride for C varargs on Windows

- [#7548]: Fixes `simd_approx_recip` and `simd_approx_recip_sqrt`

- [#7549]: Fixes `simd_select` and `simd_runtime_swizzle` operand construction

- [#7574]: Fix #7573: Check Enumerations iota fits explicit base type

- [#7570]: Fix #7544: Constant `bit_field` field access returning zero value

- [#7568]: Fix `side_effects` vs `volatile` typo in error message

- [#7561]: Fixes #6888: SIMD gather/scatter and masked load/store randomly crashing the compiler

- [#7550]: Fix syntax error type with `-json-errors`

- [#7577]: Fix `#location` in global variable initializers

- [#7582]: Fix #7581: Compiler crash when checking code with swizzled SOA fields

- [#7605]: Fix #7604: Allow building at `/`

- [#7607]: Fix #7598: Keep entity iteration valid across a scope map rehash

- [#7623]: Add `-file` suggestion when `main` is duplicated or package names differ

- [#7628]: Fix quadratic type checking case: don't cache polymorphic record specializations

- [#7631]: Fix record instantiated poly proc on selector when used as a proc value

- [#7629]: Fix #7596 and #7511

- [#7621]: Fixes the attributes of the context parameter in dummy procedures

- [#7641]: Fix field sorting for `bit_field` literals

- [#7656]: Fix #7609: Emit union constants for non-constantable unions

- [#7658]: Fixes `#must_tail` on WASM targets

- [#7652]: Fix #6951 and #5214: `$` procedure arguments matching the wrong instantiation

- [#7639]: Fix #6302: Broadcasting arrays of matrices and matrices

- [#7661]: Fix #7587: Full length swizzles through a pointer keeping the pointer type

- [#7594]: Fix #7583: `-strict-style` requires comma before newline after proc parameters which have a default value

- [#7588]: Fix #7427 and #7193: Error on OOB tuple element in compound literals

- [#7668]: Fix #5318: Procedures passed to `$` parameters share an instantiation's name

- [#7666]: Add `ExactValue_Rational` to improve precision on compiler float computation

- [#7602]: Adds lifetime markers for named locals

- [#7674]: Fix #5105 and #5569: Deferred call in short circuits causes LLVM codegen failure

- [#7682]: Fixes the `nocapture` attribute on LLVM >= 21

- [#7679]: Fix #7477 and #7506: Casts between nested arrays of the same depth

- [#7697]: Fix compound literals of array backed `bit_fields`

- [#7692]: Disallows the "odin" calling convention with `#must_tail`

- [#7706]: Fix #7430: Fixed capacity dynamic array literals lose their length

- [#7709]: Fix #7708: Compare a polymorphic record's constant parameters by value in `subst_unify`

- [#7711]: Fix #7700: Constant `#soa` field access yields the per-element field array; compare and canonicalize `typeid` constants

- [#7716]: Fix `intrinsics.procedure_of` with parapoly specializations

- [#7714]: Fixes #3995, #4337, #5950, #7197, and #7640: Handle globals initialized with the address of a non constant literal

- [#7718]: Fix #7490: Preserve zero-initialized arrays in `intrinsics.concatenate`

- [#7722]: Use a response file for `MSVC`-style linkers (`link.exe` and `radlink.exe`) when the command line exceeds the `CreateProcess` limit of 32KiB

- [#7723]: Fix mark a generated polymorphic procedure before publishing it to other threads

- [#7520]: Fix `#soa` pointer field access through `using`

- [#7743]: Allow `using` on `#soa` pointers, and make the fields a `using` `#soa` pointer parameter promotes assignable

- [#7746]: Fix `-linker:radlink` being rejected on Windows

- [#7740]: Fix #7689: Incorrect debug source location at the end of if/else chains

## New Packages

- [#7523]: `asm`: Generalize memory operand syntax to a flat term list

## Package Improvements

### Speedups

- [#7630]: `core:strconv`: Ported Eisel-Lemire's fast float algorithm to Odin

- [#7672]: `core:strconv`: Second part of the Fast Float port (SWAR based scanning)

- [#7725]: `core:strconv`: Adds a `#config` to opt out of fast float (and its table)

- [#7726]: `core:hash/xxhash`: Add a few more `#no_bounds_check` to `XXH3`

- [#7728]: `base:runtime`: `map` performance improvements

### General fixes and improvements

- [#7496]: `core:sys/windows`: Add bindings for advanced mouse/pointer/pen manipulation

- [#7508]: `vendor:windows/wasapi`: Fixes

- [#7516]: `core:mem`: Revert #6476, which misunderstood the `mem.Scratch` allocator's semantics

- [#7517]: `core:mem`: Implement tests for the `mem.Scratch` allocator

- [#7489]: `core:simd/arm`: Implement SIMD Arm Neon shift left

- [#6787]: `core:fmt`: Improved `fmt_os` documentation

- [#7527]: `core:simd/x86`: Fixed typo in `avx.odin`

- [#7539]: `vendor:curl` (Linux): Remove import declarations for crypto libraries that differ by distro

- [#7532]: `core:sys/windows`: Add line-drawing functions in `gdi32.odin`

- [#7563]: `core:simd/arm`: Implement SIMD Arm Neon shift right

- [#7576]: `vendor:sdl3/ttf`: Use `[^]byte` rather than `cstring` and add `ExpandString` wrapper

- [#7572]: `vendor:libc-shim`: Replace `mem_zero` with null termination in `strncpy`

- [#7565]: `core:sys/windows`: Add performance counter `PSAPI` bindings

- [#7553]: `vendor:box2d`: Add missing `GetVersion` binding

- [#7546]: `vendor/box3d`: Support `BOX3D_SHARED` on Windows

- [#7543]: `vendor:egl`: Bind more procedures and constants

- [#7599]: `core:os`: Fix the 0th env var being duplicated on Linux

- [#7600]: `vendor:OpenEXRCore` Fixes

- [#7536]: `core:odin`: Fix #7526: Handle triple quote/tick string

- [#7603]: `core:simd/arm`: Implement SIMD Arm Neon zip unzip extract

- [#7615]: `base:runtime`: Fix #7562: Windows AMD64 no-CRT stack probe support

- [#7620]: `core:dynlib`: Improvements and explanations in example

- [#7622]: `core:strconv`: Fixes three bugs in hex float parsing

- [#7624]: `core:math/big`: Fix squaring path writing the denominator into the numerator

- [#7633]: `core:encoding/json`: Size the unquote buffer for replaced invalid `UTF-8`

- [#6722]: `core:sys/linux`: Fix `Time_Val` precision comment

- [#7634]: `core:crypto/_fiat`: Fix P-256 `fe_sqrt` addition chain, unblocking compressed SEC1 point decoding

- [#7627]: `core:rexcode`: Add 512bit `vmovntdq(a)`

- [#7659]: `core:encoding/base64`: Add strict decoding options

- [#7663]: `core:simd/x86`: Implement simd x86 avx2 avx512 shift logical

- [#7632]: `core:simd/arm`: Implement simd arm neon transpose reverse

- [#7579]: `core:c`: Fixes #7540: fastX type widths

- [#7584]: `core:sys/windows`: Extend Win32 common dialog bindings

- [#7610]: `core:sys/windows`: Fix #7547: Double-null-terminate path in `SHFileOperationW`

- [#7665]: `core:container/bit_array`: Add `create_from_enum` helper. Improve documentation, fix examples.

- [#7671]: `core:container/xar`: Fix chunk slot count capping `Array` capacity

- [#7484]: `core:sort`: Document all public procedures and Interface types

- [#7676]: `core:crypto/aegis`: Minor documentation cleanups

- [#7673]: `core:encoding/json`: Removes `@(private)` from `unmarshal_value` for use in user unmarshalers

- [#7590]: `core:os`: Allocate the long-path buffer in the caller's allocator

- [#7320]: `vendor:sdl3`: WASM foreign import library configurable

- [#7684]: `core:rexcode`: Changed `append` to `append_elem` for a sizable improvement

- [#7683]: `core:simd/x86`: Implement simd x86 avx512 evex512

- [#7690]: `core:encoding/base64`: Add unpadded base64 encoding

- [#7695]: `core:simd/x86`: Implement simd x86 avx512 typo fix

- [#7703]: `core:encoding/csv`: Preserve final CSV records in multiline mode

- [#7704]: `core:encoding/cbor`: Fix `bit_set` byte order

- [#7643]: `vendor:sdl2`: Add `RenderSetVSync`

- [#7721]: `core:sync/chan`: Accept `.Recv` channels in `chan.recv` and `chan.try_recv`

- [#7733]: `core:odin`: Fix parser assert with invalid for-in stmt

- [#7731]: `core:time/timezone`: Preserve fractional timestamps in timezone conversions

- [#7738]: `core:math/linalg/glsl`: Fix `mix_vec4` and `mix_dvec4` implementations

- [#7753]: `core:fmt`: Fix incorrect number of bytes written returned when formatting floats with `h`/`H`

- [#7751]: `core:simd/x86`: Implement simd x86 sse2 `_mm_insert_epi16` fix

- [#7755]: `core:sys/windows`: Add `GetCursor` and `GetDpiForSystem`

- [#7756]: `vendor:box3d`: Fixing typo from `userMateriald` to `userMaterialId`

## Miscellaneous

- [#7495]: macOS Intel removed from CI tests and releases, due to general flakiness of the CI. Odin can still be built from source on Intel Macs.

- [#7569]: Fix #7525: Add test coverage for inline-asm label definitions on AMD64

- [#7670]: Update NetBSD CI from 2026Q1 -> 2026Q3

- [#7707]: Adjust doc comments that misrender as CommonMark

- [#7754]: Upgrade Ubuntu CI to LLVM 22

- [#7744]: Update `test_core_runtime.odin`

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2026-09...dev-2026-10

---

## dev-2026-09 - 2026-09-01

**dev-2026-09** by Kelimion - <https://github.com/odin-lang/Odin/releases/tag/dev-2026-09>

## New Language Features

- Experimental: Inline `asm` templates for x86/x64, ARM and RISC-V in #7271, #7406 and #7465

- Documentation: https://odin-lang.org/docs/inline-asm/

- \`\`\` and """ strings to declare multi-line string literals that normalize indentation up to the closing quotation marks.

## New Compiler Improvements

- Use `posix_spawnp` instead of `system()` when invoking the linker in #7485

- Fix default linker timing label on non-Windows platforms in #7240

- Fix `odin doc -doc-format` aborting on any package that imports another package in #7242

- Fix bigint negative printing in #7243

- Fix constant `transmute` from unsigned to signed wrapping one value too many in #7244

- Handle `#soa` fixed compound literals for vars in #7239

- Validate floating-point array counts as integers in #7251

- Fix typo in enumerated array in #7252

- Make redeclaration diagnostics stable under threading in #7253

- Improve procedure group overload scoring in #7227

- Fix #7012 - a type isn't its own specialization in #7257

- Fixes swizzles on array elements in soa containers in #7259

- Fix Name Canonicalization Rotate Left typo in #7267

- Fix constant `string16` carrying UTF-8, and inverted slice indices reaching `substring` in #7268

- Fixes chain indexing for array elements in `#soa` containers in #7270

- Fixes range loop over array elements in `#soa` containers in #7277

- Fix riscv64 ABI classification for padded, over-aligned, and pointer-bearing structs in #7282

- i386: Pass aggregate arguments by value on the stack in #7283

- i386: Return aggregates through the hidden pointer on System V targets in #7284

- Use enum value init expression instead of numeric value in doc format in #7289

- Remove dead `simd_rem` in #7269

- Fix duplicated name for temporary `.ll` files in #7291

- Don't clear the operand value on the simd success path in #7315

- Fix #7281, apply `#max_field_align` in #7314

- Add diagnostic for missing field name to `type_field_bit_offset` + `type_field_bit_size` in #7293

- Fix byte swap on untyped int-like untyped types in #7294

- Bound constant arguments before range-checking them in #7295

- `type_is_comparable`: false for an unspecialized polymorphic record in #7296

- Fix guards combining two required conditions with `&&` in #7297

- Correct the endianness guard messages in #7301

- Make the three endianness predicates partition in #7307

- `simd_extract_lsbs`/`simd_extract_msbs` Reject a lane count that exceeds the `bit_set` limit in #7308

- Clarify `type_has_shared_fields` behavior in code doc in #7309

- Matrix: enforce the element limit on multiplication and on overflowing dimensions in #7310

- Hoist `if` stmt in enumerated_array in #7311

- Check enumerated array length in #7312

- `check_matrix_type_hint`: Require the element type and layout to match in #7313

- Fixes `f32` to 64-bit `int`/`uint` conversion in #7319

- Fixes `float` to 128-bit `int`/`uint` conversion in #7321

- Classify amd64/arm64 aggregates from the source type in #7292

- Fix `long` -> `int64_t` for win64 in #7324

- Fix `bit_field` intrinsic by @kalsprite in https://github.com/odin-lang/Odin/pull/7325

- Fix out of bounds for zero arg `#load_directory` in #7329

- Fix compilation error when using the fixed-point write procedure and `-vet-unused` in #7330

- Fix backend support for `#unroll` on `[dynamic]T` in #7337

- Fix `bit_set` upper endpoint representability check in #7340

- fix `bit_set` subset/superset constant folding in #7346

- Fix three faults in `&~` constant folding in #7345

- Enforce the `#simd` construction rules and stop two crashes in #7344

- `intrinsics.type_integer_to_unsigned(rune)` returns `f16` in #7343

- `quaternion` and `complex` nan cmp & accessors in #7342

- Improved stable sort, from `insertion_sort` to `merge_rotate` in #7349

- Set console codepage to utf-8 (on Windows), and restore old one on exit in #7351

- Reenables `LLVMSetUnnamedAddress` for global constants merging in #7333

- Range-check a constant passed to an `#any_int` parameter in #7360

- Add the missing `break` in `add_min_dep_type_info` in #7359

- riscv64: Read a flattened aggregate's members from their real offsets in #7334

- Fix eol diagnostic in #7358

- Fixes the `%%` operator in #7353

- Fix SIGBUS/segfault when compiling recursive `#soa` slice/dynamic array types in #7361

- ABI Conformance harness + fixes in #7327

- Fix `c_va_start` guard and `c_va_arg` format mismatch in #7367

- riscv64: use a slice for the coerce offsets + missed arm in riscv ABI in #7368

- Reject a built-in procedure assigned to in #7369

- Do not register map runtime dependencies under bedrock in #7371

- Range-check the constant `abs` folds in #7372

- Fix #7377 in #7378

- Let FreeBSD use default `gb_copy_file` path in #7381

- Add AVX-512 VNNI VPDPWSSD support to inline assembly in #7380

- A base prefix with only digit separators has no digits in #7370

- A `bit_fìeld` constant is range-checked only while it is untyped in #7385

- A self-referential `bit_field` hangs the compiler in #7390

- Codegen worker must not exit process with running siblings in #7391

- Multi-instruction asm template computed with one operand twice in #7393

- `extend` family emits mnemonic that doesn't exist in #7392

- Let compiler check error() fmt strings + fixes in #7395

- Peel union constant to its variant in #7396

- `complex` and `quaternion` take their type from their arguments in #7399

- A union constant in a ternary or builds an ill-typed phi #7397

- Implement fixes for constant unions in #7087

- Only reuse a compound literal's storage for a variable of its type in #7400

- Fix `or_else` diverging with single return value in #7394

- Remove the `os.Error == 0` compatibility hack in #7403

- Restore the `Did you want 'nil'?` diagnostic everywhere in #7405

- Address `printf` format warning in #7404

- Better hints when assigning or comparing to `0` when it is not allowed in #7407

- Fix reordered compound literal comparison in #7409

- Fix compiler panic on a selector into `#branch_location` in #7415

- Fix compiler segfault on `distinct` of a type alias that cycles back in #7416

- Fix segfault comparing two foreign declarations of the same symbol in #7417

- Fix compiler segfault on a bare `..` in a type position call in #7418

- Asm cast guard in #7437

- Reject asm operands in slots only a named hardware register can fill in #7431

- Diagnose in an asm template instead of aborting with SIGILL in #7434

- Fix `-no-crt` on Windows in #7426

- Fixes `-o:size` in #7440

- `string_split_iterator` fix in #7445

- Big endian bool cmp in #7448

- Fix `min(T) % -1` kills the process with SIGFPE, at every hardware width in #7450

- Fix canonical names for types in procedure literals in #7439

- Inline `asm` templates - CFG based analysis in #7444

- Normalize bool cmp in #7449

- Reject a non-constant argument to an asm template's immediate in #7432

- Add missing `i128le`, `i128be` to endian switch in #7459

- Convert constants before narrowing to `i64` in the remaining checker sites in #7460

- Delete dead code that crashed the checker on an `asm` template group with no parameters in #7435

- Fix a swizzle target in a multi-assignment reading an already-written source in #7458

- Broadcast a constant into every array level in #7457

- Give asm templates a documentation category instead of a blank header and a null `%s` in #7438

- Do not deduplicate cases in tagless switches in #7468

## New Packages

-

## Package Improvements

- [core:unicode/utf8] Fix truncated text for grapheme clusters in #7003

- [core:thread] Clarify completed task handling in thread pools in #7247

- [core:simd] Fix grammar in #7203

- [core:bytes] Optimize `index_any` with a byte bitset in #7255

- [core:simd/arm] Implement simd arm neon table lookup in #7256

- [core:odin/tokenizer] Fix broken double-checked lock in `init` in #7258

- [core:sys/windows] Add `UnregisterHotKey` in #7264

- [core:odin/parser] Fix unparenthesized attributes missing end position in its AST node in #7265

- [vendor:box3d] Add Box3D support for WebAssembly in #7266

- [core:simd/arm] Fix simd arm neon table lookup on big endian in #7273

- [core:unicode/utf8] + [core:text/edit] Add `text` field to `utf8.Grapheme`, fix caret translation by grapheme in #7274

- [base:runtime] Fixes `non_zero_append_elem_fixed_capacity_string` in #7317

- [base:runtime] Adds the `pop` family of procedures for `#soa` arrays in #7290

- [core:simd/arm] Implement simd arm neon extended table lookup in #7275

- [core:simd/arm] Implement simd arm neon logical in #7332

- [core:encoding/hex] Add non-allocating `decode_into_buffer` in #7347

- [base:runtime] Fix #7262. Do not free the original block on a failed heap resize in #7328

- [core:os] Fix #7350 in #7352

- [core:mem] Keep `Dynamic_Arena` allocations aligned after reset in #7355

- [core:slice] Fix `slice.get` doing unnecessary bounds check in #7363

- [core:slice] Fix `slice.simple_equal` misbehaviour on empty slice with non-nil data in #7364

- [core:image/tga] Fix `.alpha_add_if_missing` for TGA in #7366

- [core:sys/windows] Fix `FILE_NOTIFY_INFORMATION` struct member casing in #7374

- [core:odin] Remove `inline` and `no_inline` keywords in #7375

- [core:sys/wasm/js] Support shared WebAssembly memory in browser APIs in #7272

- [core:container/handle_map] Nicer organization, fix broken test, add test in #7383

- [core:rexcode/x86] Merge tables in #7384

- [core:thread] An exiting worker must not leave published in #7388

- [core:rexcode] Improvements in #7362

- [core:image/jpeg] Fixed negative read bug in #7410

- [core:hash] Add murmur3 implementation in #7419

- [core:nbio] Fix use-after-free, spurious poll readiness, and double completion on Windows in #7401

- [vendor:raylib] Fixed typo in `raylib.odin` in #7451

- [core:os] Fix simple typo in `process.odin` in #7454

- [core:fmt] Fill left-justified field with spaces in #7461

- [core:sys/darwin/Foundation] Skip Cocoa import on iOS in #7424

- [vendor:libc-shim] Fix typo in `sched.odin` in #7456

- [core:fmt] Fix justified printing of `0` producing all spaces in #7463

- [core:unicode/utf8] Fix #5939 grapheme cluster width in #7462

- [core:debug/trace] Remove `os`, `fmt`, `slice`, and `strconv` imports in #7408

- [core:os] add `device` to `File_Info` by @laytan in https://github.com/odin-lang/Odin/pull/7466

- [core:odin/parser] Improve parsing field docs and comments in #7481

- [core:net] Use explicitly passed allocators in #7480

- [core:encoding/json] Fix leak of key and value of a malformed object in #7487

## Miscellaneous

- Explicitly specify all required LLVM components on Linux build in #7338

- Remove faulty tests in #7446

- Remove `-microarch:native` from 3 Windows tests and tweak Win test runner in #7455

- Add regression test for #7336 in #7428

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2026-08...dev-2026-09

---

## dev-2026-08 - 2026-08-06

**dev-2026-08** by Kelimion - <https://github.com/odin-lang/Odin/releases/tag/dev-2026-08>

## New Language Features

- Allow custom `-collection`s to be used for `foreign import`s in #6999

## New Compiler Improvements

- Disallow proc group assignment to blank identifier in #6996

- Increase stack size for threads in #6997

- Reject chained deferred procedures in #7013

- Fix arm64 ABI: '#simd' vectors and vector aggregates not passed in registers (#7010) by in #7015

- Fix darwin arm64 argument passing abi in #7030

- Fix playdate `-subtarget` issue where floats were incorrectly compiled in #7026

- Make object and assembly file extensions user-changeable again in #7041

- Fix subtype comparisons (#6151, #3689, #7020 and #4734) in #7039

- Fix constant aggregate rebuild in #7046

- Keep polymorphic probes read-only in #7052

- Fix `switch` fallthrough in `lb_emit_struct_ev` (#7050) in #7051

- Fix arm64 argument alignment abi for composite type of size <= 16 bytes in #7045

- Preserve recursive struct aliases in #7042

- Compare `mmap` result to `MAP_FAILED` rather than `nullptr` (#7053) in #7065

- Stricter type coercions in `convert_to_typed` in #7056

- Fix backend deadlock where `func_raw_types_mutex` and `types_mutex` were waiting on each other by in #7060

- Add `typeid` constant case to `check_comparison` (#7027) in #7064

- Fixes compile time equality comparison for `string16` in #7071

- Allow fixed-capacity arrays in constant unions (#7089) in #7090

- Fixes spurious `#no_alias` compile errors during polymorphic overload resolution in #7116

- Reject the use of labels as expressions (#5830 and #7108) in #7130

- Fix hang for poly procs with default proc literal params in #7146

- Fix `expand_values` panic on type expressions in #7157

- Handle spaces in args for 'odin run . -- <args>' on Windows in #7162

- Don't assert on `-define:` values with an exponent in #7164

- Fix error hint for vet tag in #7132

- RISC-V fixes/improvements in #7144

- Fix LLVM codegen for matching on `nil` for `union{}` in #7139

- Allow `#caller_expression` on constant parameters which are procedures in #7119

- Fixes compile error due to `#no_alias` shifting position in procs with indirect return in #7214

- Fixes a compiler segfault with zero sized parameters on targets that ignore these in the LLVM signature in #7215

- Fix every named argument in "Given argument types" being labelled with the first argument's name in #7217

- Fix `levenstein_distance` in #7218

- Fix signed Int Constants being permitted to exceed size in #7220

- Fix `string16` oob in #7221

- Fix new line suppression by @kalsprite in #7222

- Improve grammar on import name error in #7223

- Fix matrix col error message that said rows instead in #7224

- Minor typos in #7225

- Fix crash on poly in #7226

- Fix `-vet-packages` not working in certain cases in #7210

- Pack tuple results into variadic arguments (#7167) in #7185

- Polymorphic procedures resolving to `nil` (#6753 and #) in #7208

## New Packages

- `[core:crypto/rsa]` Add RSA support in #6857

- `[core:encoding/asn1]` Add strict DER + `[core:crypto/x509]` (X.509 v3) in #6838

- `[core:crypto/turboshake]` Add TurboSHAKE in #7043

- `[core:rexcode]` Add rexcode, a high-performance multi-architecture instruction encoder/decoder/printer package in #6839

- `[core:debug/trace]` Replaced with a much improved implementation in #7141

## Package Improvements

- `[core:container/rbtree]` Match `find_or_insert` semantics with AVL in #6988

- `[core:container/rbtree]` Add `upsert` in #7002

- `[vendor:box3d]` Fix missing return value of `*_GetUserData` functions in #7006

- `[core:sys/windows]` Add additional bindings in #7022

- `[vendor:raylib]` Update `rlgl` bindings to raylib 6 in #7023 and #7028

- `[core:strings]` Add `@(require_results)` where useful in #7038

- `[core:log]` Make multi logger use all loggers instead of breaking on first non match in #7057

- `[core:encoding/csv]` Update example to use the new `core:os` in #7076

- `[base:runtime]` Fix markdown table in docs in #7077

- `[base:runtime]` Fix map reporting incorrect capacity after shrinking in #7097

- `[core:os]` Fixes file open emulation of posix open behavior on mode/perm mismatch on Windows in #7098

- `[base:runtime]` Fixes SoA dynamic arrays not zeroing all elements after shrink + grow in #7103

- `[core:odin/tokenizer]` Set token kind to float for hex floats in #7117

- `[vendor:sdl3]` Fix `(S/G)etDefaultTextureScaleMode` in #7133

- `[core:unicode]` Fix duplicated entries within `unicode_spaces` and `space_ranges` in #7142

- `[base:runtime]` Fixes growth check for SoA dynamic arrays in #7145

- `[core:debug/trace]` Sync tracking allocator with `core:mem` in #7147

- `[core:debug/trace]` Sync allocator with `core:mem` in #7200

- `[core:sys/windows]` Fix `LoadLibraryEx_Flags` off-by-one in #7151

- `[core:mem/virtual]` Close dangling handle in `map` implementation on Windows in #7159

- `[core:testing]` Respect `TERM=dumb` in test runner to prevent ANSI sequences, color in #7160

- `[core:thread]` Add `get_name` and `set_name` in #5464

- `[base:runtime]` Shrink `map` to minimum capacity with `shrink` in #7152

- `[core:text/scanner]` Fix #7153 and add a test in #7165

- `[core:rexcode/x86]` Label addressing for RIP-relative disp and movabs imm in #7168

- `[core:simd/arm]` Implement simd arm crc32 in #7174

- `[core:compress/gzip]` Fix example code in #7178

- `[core:simd/arm]` Implement simd arm pmull in #7184

- `[base:runtime]` Follow up fix of `shrink_map` #7182

- `[core:odin/parser]` Correct end position for fields with a specialization in #7180

- `[core:text/scanner]` Fix octal escape parsing in #7176

- `[core:os]` Update stale `os.flags` file doc in #7187

- `[core:mem]` Zero `tracking_allocator.allocation_map` and `tracking_allocator.bad_free_array` in `destroy` in #7195

- `[base:runtime]` Make soa builtins go vroom in #7196

- `[base:runtime]` Cleans up obsolete comments in `_append_soa_elems` in #7204

- `[base:runtime]` Annotates the array parameter of dynamic array builtins with `#no_alias` in #7149

- `[core:simd/arm]` Impl fix simd arm SHA in #7205

- `[core:os]` Fix `glob` not cloning pattern when no meta characters present in #7206

- `[core:crypto/_fiat]` Fix conditional in `ensure` in #7211

- `[vendor:box3d]` Update box3d (#7177) to https://github.com/erincatto/box3d/commit/3fc20f5b453ba9e14cdf54ecafa87a2a4bcdf53c in #7212 + #7231

- `[core:crypto]` Minor fixes in #7228

- `[core:os]` Resolve relative path before `SHFileOperationW` in `_remove_all` in #7230

- `[core:net]` Fix percent encoding for bytes < 0x10 (#7109) in #7234

- `[core:simd/arm]` Implement simd arm neon bit manipulation in #7216

- Various typo fixes across the packages

## Miscellaneous

- `[vendor:*]` Replace makefiles in with shell scripts in #7034

- CI: Update NetBSD to `10_2026Q1` in #7085

- Improve build scripts portabability and make them `pwd` independent in #7084

- CI: Make NetBSD CI less prone to breaking when scheduled on old CPUs

## What's Changed

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2026-07a...dev-2026-08

---

## dev-2026-07a - 2026-07-10

**dev-2026-07a** by Kelimion - <https://github.com/odin-lang/Odin/releases/tag/dev-2026-07a>

## What's Changed

- Add pull request policy to `vendor/README.md`

- Fix `vendor:raylib` 6.0 bindings

- Update `vendor:box3d` to latest commit in #6986

- Fix for `@(objc_implement)` being broken in `dev-2026-07` release in #6990

- Ensure identical types have same hash by in #6974

- Prevent git output with signature information in #6973

- Update wgpu.js in #6975

- Fix parser failing on comments inside ternary expressions in #6968

- fix `assign_at_elems_fixed_capacity_dynamic_array` in #6993

- Fix #6979 in #6987

- Remove `default` help option for stack protector in #6984

- Update `kb_text_shape` to v2.21 in #6944

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2026-07...dev-2026-07a

---

## dev-2026-07 - 2026-07-06

**dev-2026-07** by Kelimion - <https://github.com/odin-lang/Odin/releases/tag/dev-2026-07>

## New Language Features

- Add restricted Odin subset mode `-bedrock` in #6654

- Add [Playdate](https://play.date) support as a `-subtarget` of `-target:freestanding_arm32` in #6900

- Support `q.xyz` on quaternion*

## New Compiler Improvements

- New Feature: Stack canaries #6830

- Change default settings to enable pie and full relro on Linux in #6790

- Make the type hash 63-bit to not crash OMG JIT in WebKit under WASM in #6829

- Add suggestion to use 'typeid_of(type)' when trying to do `typeid(type)` in #6846

- `@(test)` procs in `#+private` files are now processed in #6844

- Reject transitive `#subtype-only` implicit conversion in checker in #6845

- Fix initialization of global `any`s #6849

- Fix: tuples are not handled properly in struct literals in #6859

- Move away from `system` for `odin run` in #6848

- Raise child process error signal if `odin run` child gets terminated #6870

- Flush accumulated errors before printing assert in #5508

- Fix #6874 in #6880

- Fix #6885 in #6886

- Resolve panic on 64-bit constant overflow in #6904

- Fix constant union stuff against tests in #6905

- Report range type correctly on out-of-bounds in #6906

- Add more constant type cases in #6913

- Use `lb_add_values_to_array` for `cvarargs` in #6908

- Only allow direct `CVarArg` usage in `c_va_start` in #6916

- Add ways to diff anon procs with same signature in #6920

- Fix compiler segmentation fault when field names start with '.' in #6928

- Fix UTF-8 decode error check in #6930

- Improve custom output location (`-out`) support for LLVM-IR, OBJ + ASM in #6932

- Fix typo in union error in #6929

- Make checking of untyped to union conversions more strict in #6925

- Allow casts to change mode for array programming in #6921

- Avoid code regeneration for fns in unroll in #6939

- Make diverging `or_else` inherit `#load` lhs type in #6934

- Add diverging (`!`), `#optional_ok` to proc canon name in #6935

- Fix misuse of `lb_emit_(min|max)` in `simd_(min|max)` in #6924

- Remove support for LLVM 14, suggest apt.llvm.org if `llvm-config-14` can't be found in #6918

- Use specific format to make `f64` strings canonical in #6949

- Disallow types in `#any_int` params in #6950

- Convert poly const int to `f64` when needed in #6948

## New Packages

- [core:raylib] Raylib 6.0 in #6940

- [vendor:box3d] Box3D bindings in #6933

## Package Improvements

- [core:terminal/ansi] Add Alternate Screen Buffer in #6813

- [core:nbio] Fix UAF op `op.l` in cross-thread exec in #6819

- [core:slice] Fix wrong variable name in `slice.rotate` in * fixed wrong variable name in #6828

- [vendor:vulkan] Update Vulkan in #6824

- [core:container/pool] Fix ABA race in the free list in #6822

- [core:bufio] Improve `reader_read_slice`'s documentation using the power of punctuation in #6463

- [base:runtime] Added optional allocator error to `map_insert` in #6836

- [core:odin] Correct divergence from C++ parser with expr levels, causing failures in #6861

- [vendor:stb/truetype] Amend `PackFontRanges` types in #5662

- [core:mem] Rename `DEFAULT_PAGE_SIZE` to `PAGE_SIZE` in #6471

- [core:os] Improve consistency in `os.read_entire_file_from_file` in #6671

- [core:flags] Improve `bit_set` support in #6435

- [vendor:x11/xlib] Update `Xlib` documentation link to current PDF in #6875

- [core:text/regex] Improve regex compiler performance in #6873

- [core:mem] Fix `mem.Dynamic_Arena` alignment in #6878

- [core:crypto/wycheproof] Update the tests to match recent changes in #6887

- [vendor:sdl3] Remove non-exported `joystick_lock` symbol in #6893

- [vendor:windows/GameInput] Remove `GameInput` prefix from interface type names in #6903

- [core:encoding/entity] Fix whitespace normalization in #6914

- [core:container/handle_map] Remove unused `base:builtin` import in #6931

- [vendor:wgpu] Update to v29.0.1.1 in #6947

- [core:encoding/cbor] Fix segfault decoding map/big.int nested in slice elements in #6945

- [core:encoding/cbor] Fix data corruption in #6954

- [vendor:wgpu] Update to v29.0.1.1

- [core:container/xar] Forward caller location to make in `array_push_back_*` in #6958

## Miscellaneous

- Fix nightly static Linux build in #6808

- Added missing `LDFLAGS` for `OpenBSD` in #6728

- Deduplicate macOS and Linux nightly builds in #6812

- Remove dependency on `mbedx509`, `mbedcrypto` for Darwin in #6842

## What's Changed

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2026-06...dev-2027-07

---

## dev-2026-06 - 2026-06-10

**dev-2026-06** by Kelimion - <https://github.com/odin-lang/Odin/releases/tag/dev-2026-06>

## New Language Features

- Add `@(fast_math)` attribute (PR #6676)

- Support `**` as `expand_values` operator: `**x` == `expand_values(x)` (PR #6731)

## New Compiler Improvements

- Better error reporting for unary `++`/`--` (PR #6649)

- Removed Haiku from supported targets (PR #6631)

- Better SIMD generation for square matrix multiplication and `intrinsics.transpose` (PR #6676)

- Fix `deferred_return` and segfault in docs writer (PR #6668)

- Fix issue #6429, `odin doc` handling of Fixed Capacity Dynamic Arrays in `write_expr_to_string` (PR #6670)

- Add duplicates checking in type switches by @Creativty (PR #6702)

- Fix `nil` typing for procedure call arguments (PR #6701)

- Fix issue #6096, honor `-no-thread-local` for variables declared at procedure scope (PR #6696)

- Improve `simd.runtime_swizzle` and its documentation (PR #6712)

- Improve thoroughness of generic procedure type detection (PR #6711)

- Fix race condition relating to type specialization (PR #6716)

- Fix issue 6692, `using` on bit fields (PR #6742)

- Fix error pos style environment variable overwriting commandline argument (PR #6741)

- Properly check `#any_int` param operands (PR #6740)

- Fix assertion failure when comparing array-backed `bit_field`s (PR #6773)

- Disallow `*` and `/` for `bit_set`s (PR #6777)

- `AArch64` assembly support for `foreign import` (PR #6784)

- Fix error message "`do` not on the same line as `for`" (PR #6794)

## New Packages

- Add ML-KEM (FIPS 203) post-quantum key encapsulation support (PR #6635)

- Add ML-DSA (FIPS 204) post-quantum digital signature support (PR #6695)

- Add intial PEM support (PR #6755)

## Package Improvements

- Improve consistency between platforms for `os.copy_directory_all` (PR #6651)

- Use `context.assertion_failure_proc` in tracking allocator bad free callback (PR #6659)

- Add `DefSubclassProc` binding (PR #6664)

- Make `make_aligned` and `new_aligned` builtins (PR #6677)

- Handle invalid utf8 when parsing json (PR #6669)

- Fix xlib binding signatures (PR #6680)

- Add unicode mapping between 'ẞ' <-> 'ß' (PR #6672)

- Fix missing `only_if_exists` parameter in `x11.XInternAtoms` (PR #6684)

- Convert `(f)stat` calls to `statx` in Linux `core:os` implementation (PR #6683)

- Additional xlib binding changes (PR #6687)

- Fix `read_slice` typo in `core:io/utils` (PR #6697)

- Document `strconv.parse_int` and `strconv.parse_uint` (PR #6706)

- `core:math/linalg`: Add Gram-Schmidt orthonormalize (PR #6707)

- `vendor:wgpu`: Fix incorrect proc signatures (PR #6661, PR #6724)

- Add support to unmarshal the new fixed capacity dynamic arrays (PR #6713)

- `core:encoding/base64`: Misc fixes and improvements (PR #6733)

- `core:strconv`: Fix upper bound of Decimal in `round_shortest` (PR #6734)

- `vendor:directx/d3d12`: Add `IDevice10` interface (PR #6602)

- `vendor/README.md` fix inverted SDL2 and SDL3 (PR #6749)

- Swap `panic_contextless` and `unimplemented_contexless` documentation (PR #6758)

- `core:sys/linux`: Remove parapoly from `rt_sigaction` (PR #6756)

- `core:slice`: Fix `rotate_left` crash on empty array (PR #6771)

- `core:sys.info`: Prefer mem info from `/proc/meminfo` over `sysinfo()` (PR #6765)

- `core:mem` / `core:testing`: Fix buffer overflow when running a test which shrinks a dynamic array (PR #6791)

## Miscellaneous

- Add `/src` as safe directory for nightly linux arm workflow (PR #6658)

- Link against `libstdc++exp` for backtrace support (PR #6732)

## Full Change Log

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2026-05...dev-2026-06

---

## dev-2026-05 - 2026-05-04

**dev-2026-05** by Kelimion - <https://github.com/odin-lang/Odin/releases/tag/dev-2026-05>

## New Language Features

- Native Array Casting Semantics, e.g. `cast([4]f32)4x_u32` (PR #6605)

- Increase `matrix` limit from 16 to 64 elements, allowing for up to `matrix[8, 8]T`

## New Compiler Improvements

- Add -debug default behavior usage docs (PR #6511)

- Fix output of filename when outputting docs with the `-in-source-order` option (PR #6536)

- Fix `#no_bounds_check` regression (PR #6541)

- Fix target feature lookup, canonicalize `target_features_set` (PR #6544)

- Fix (Issue #6344) - Field-first index writes on `#soa[dynamic]T` and `#soa[]T` (PR #6539)

- Fix `aligned_alloc` not defined on Android/Bionic (PR #6519)

- Fix `break`/`continue` being allowed in a nested unrolled range loop (PR #6521)

- `SROA` and simplification passes on `-o:minimal` (PR #6553)

- Fix array counts for floats that are exactly representable as integers e.g. `[1.1e4]int` (PR #6583)

- Prevent coredump when child process gets killed by signal (PR #6586)

- Support multiple return values within compound literal elements (PR #6596)

- Fix (Issue #5422) - Make `@(rodata)` on constants yield "not supported" message (PR #6601)

- Fix (Issue #6594) - Report cycle when assigning variable to itself (PR #6599)

- Fix (Issue #6621) - Report cycle for `type_of` (PR #6624)

- Removed moribund `Essence` OS from supported targets (PR #6623)

- Add `intrinsics.c_va_*` (PR #6629)

- Fix type info not being generated for types only used in `[]typeid` literals (PR #6630)

- Fix compiler warning on Linux (PR #6638)

## New Packages

- [core:crypto/noise] Add Noise implementation (PR #6573)

## Package Improvements

- [core:os] Add `dir` procedure (PR #6517, PR #6528)

- [base:runtime] Native simd width (PR #6545)

- [core:os] Fix `_volume_name_len` to handle paths of purely path separators (PR #6547)

- [core:math/linalg] Faster `dot`, `cross3`, `floor`, `ceil`, and add `trunc` (PR #6549)

- [core:math/linalg] More matrix related calls: `pseudo_inverse`, `inverse_lu_decomposition`, `matrix_inverse_gauss_jordan`

- [core:mem/virtual] Fix arena overcommit bug (PR #6552)

- [core:sys/linux] Fix missing argument in `adjtimex` syscall (PR #6502)

- [vendor:wgpu] Update to v29.0.0.0 (PR #6551)

- [core:sys/freebsd] Add `ioctl` and `stdio` `FILENO` constants (PR #6537)

- [core:nbio] Handle `EOF` in poll on Posix (PR #6556)

- [core:container/xar] Fix a typo in example (PR #6559)

- [core:testing] Ensure `make_*` style bounds traps are handled in test runner `expect_signal` on Windows (PR #6563)

- [core:sys/windows] Add I/O Ring API bindings (PR #6562)

- [vendor:directx/d3d12] Fix `D3D12_BARRIER_SUBRESOURCE_RANGE` struct (PR #6557)

- [core:testing] Fix stop reason being wrong for OOB on Windows (PR #6570)

- [core:fmt] Remove redundant 'defer bufio.writer_flush' from `fprint` procs (PR #6567)

- [vendor:zlib] Fix signature of `inflateInit_` (PR #6566)

- [vendor:sdl3] Mixer: Removed `#by_ptr` from args that are valid as `nil` (PR #6576)

- [core:mem/virtual] Fix `map_file` usage example (PR #6577)

- [core:mem/virtual] Add `address_hint` to `reserve` (PR #6558)

- [core:os] Fix `stem` on empty path (PR #6579)

- [core:path/filepath] Create wrappers for allocating procedures (PR #6575)

- [core:fmt] Omit value when formatting `map[T]struct{}` sets (PR #6581)

- [vendor:vulkan] Add version macros (PR #6565)

- [core:sys/windows] Add Registry Association API (PR #6525)

- [core:sys/windows] Fix `LockFileEx` and `UnlockFileEx` (PR #6625)

- [core:math/linalg] Fix negated quaternions in `angle_from_quaternion` (PR #6607)

- [core:sys/linux] Emulate `dup2` better on arm64 and riscv (PR #6632)

## Full Change Log

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2026-04...dev-2026-05

---

## dev-2026-04 - 2026-04-03

**dev-2026-04** by Kelimion - <https://github.com/odin-lang/Odin/releases/tag/dev-2026-04>

## New Language Features

- [Fixed Capacity Dynamic Arrays](https://github.com/odin-lang/Odin/pull/6406), adds `[dynamic; N]T`

## New Compiler Improvements

- Limit maximum exponent of integer literals to avoid unnecessary work

- Add `-in-source-order` option to `odin doc` to show docs in source order within each file

- Support clang-style `+`/`-` prefixes in target features

- Fix #6396: handle full-width `bit_field` literal masks

- Fix #6401: generic cycle deadlock in struct layout

- Add support for other Android architectures

- Fix #5602: "Internal Compiler Error: Type_Info for 'x' could not be found" for poly procs with named parameters

- Continuous Compiler Improvements

- Add initial LLVM 22 support on non-Windows platforms

- More accurate `-march:native` feature selection

- Allow pointers to types which have subtype fields at offset 0 to be assignable in proc parameters.

- `offset_of(some_bit_field)` now raises a proper error

- Add `intrinsics.type_field_bit_offset(typeid, string)` to get a compile-time `bit_field` field offset in bits

- Add `intrinsics.type_field_bit_size(typeid, string)` to get a compile-time `bit_field` field size in bits (the value after `|`)

- Fix #6407: Global unions do not get initialized correctly

- Fix `>=` comparison `base:runtime` dependencies for `string` and `cstring` types

- Fix `GB_PANIC` format string in `lb_emit_conv` invalid subtype cast

- Fix `[^]u16` to `cstring16` transmute condition in `lb_emit_conv`

- Remove `Tilde` backend

- Fix #6484: Two `when` blocks which evaluate to `true` in a `foreign` block misses following decls

- Fix declaration order bug #6506: False-positive `where`-clause failures in recursive polymorphic subtype cases

- Fix declaration order bugs #5572 and #5961: Incorrectly rejecting valid in-progress/forward union references

## New Packages

- `core:crypto/argon2id` initial import

- `vendor:windows/wasapi`

- `vendor:sdl3/mixer`

## Package Improvements

- Add more JS to `examples/all`

- Update Unicode database to newer version

- Fix modular exponentiation in `core:math/big`

- Fix `assign_at` documentation

- `core:fmt` now formats `time.Duration` with a space between duration and unit when using `% v`

- Correct SIMD `shr` example documention

- Fix `sync.Auto_Reset_Event` signal deadlock

- `core:sys/darwin/Foundation`: fix `NSTimer` binding

- Partial 1.619.x d3d12 bindings

- `core:mem/virtual`: Fix for virtual arena overcommit bug #5821

- `core:crypto`: Add ARM AES hardware acceleration

- `core:crypto`: Add ARM SHA256 hardware acceleration

- `core:fmt`: Improve `core:container/small_array` formatting

- `vendor:stb/vorbis`: Add WASM support

- `core:encoding/cbor`: Fix order-dependent partial unmarshals

- `core:encoding/json`: Fix user unmarshaler example

- Fix possible OOM in `core:os.get_working_directory()` on Linux

- Fix #6455: `core:mem/virtual.map_file_from_path` ignores flags

- Fix for corner case in the `core:mem` scratch allocator.

- Minor cleanup in `base:runtime` and `core:mem`

- Fix #6495: Handle starting separator during name comparison in `core:os`

- Improved `delete_key` documentation to mention it's safe to delete keys while iterating a map as long as no resizes take place

- Fix source size check in `core:crypto/aes` ECB encrypt/decrypt

## Full Change Log

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2026-03...dev-2026-04

---

## dev-2026-03 - 2026-03-04

**dev-2026-03** by Kelimion - <https://github.com/odin-lang/Odin/releases/tag/dev-2026-03>

## BREAKING Changes

- `core:os` has been replaced with our newly improved and rewritten v2, previously available at `core:os/os2`. The old `core:os` implementation will remain available at `core:os/old` until sometime in Q3 of 2026.

  - Article on [Moving Towards a New `"core:os"`](https://odin-lang.org/news/moving-towards-a-new-core-os/)

- `core:sys/info` previously retrieved all information before `main` was entered, using `@(init)`, and exposed everything via globals. It now gathers more information on demand, and returns everything via accessors for a consistent API. Where practical - like cpu name + features - those values will be cached.

## New Language Features

- `for init; x in y {}` style loops

## New Compiler Improvements

- Stop silently ignoring unknown directives on an inline `asm` expression

- Do not allow duplicated `#partial` directives on switch statements

- Add broadcasting to strings (Fix #1837)

- Improve LLVM version picking

- Fix name canonicalization for typed ranges in `bit_set`

- Fix `bit_set` parapoly specialization

- Fix separating of diverging procedure types from block statements

- Update `Type_Info_Bit_Set` to always record underlying type. Add `runtime.type_info_underlying`

- Fix #6347

- Fix #6270

## New Packages

- `core:crypto/ecdsa`: Add ECDSA support

## Package Improvements

- [BREAKING] `core:os/os2` -> `core:os` integration

- [BREAKING] `core:sys/info`: Change API from globals to calls. Do as little work in `@(init)` as practical.

- Allow test names to be specified as a command line option for tests executable

- `vendor:x11/xlib`: Fix signature of XChangeWindowAttributes

- `vendor:directx/d3d12`: Added `IGraphicsCommandList7` and fix access violation errors

- Minimize some internal depencies in the `core` packages, e.g. don't import `core:mem` just for `mem.Allocator_Error`

- `vendor:box2d`: Fix and try Git LFS

- `core:log`: Add support for `js/wasm`

- `core:container/xar`: Fixes and improvements

- `core:container/pool`: Fix parapoly type inference around address sanitization when using multiple Pool types

- `core:container/handle_map`: Improvement

- `demo.odin` Fix `cross_3d` typo

- `core:encoding/hex`: Add uppercase encoding

- `core:bytes`: Update comment on `compare`; add additional caller location propagation

- `core:math/big`: Clean up

- `core:os`: Fix silent failure in `os.replace_path_separators` if the separator was multi-byte

- Add additional tests

- `core:sys/es`: Fix build errors

- `core:unicode/utf8`: Fix utf-8 validation

- Vendor Wycheproof cryptographic tests under `tests/core/`

- Propagate allocator errors from certain unicode functions

- Fix some tools and examples after `core:os` update and `using-stmt` feature

- Fix typo in `atomic.odin` documentation

- `core:os`: Remove `process_close` and add `process_terminate`

- `core:time`: Correct 12-hour clock string

- Update Unicode specification

- `vendor:curl`: Fix `what` argument for `url_set`

- Small optimization for dynamic arrays

- `vendor:miniaudio`: Upgrade to 0.11.24

- `core:container/priority_queue`: Add example and tests

- `core:text/regex`: Fix `\b` handling in iterator

- `vendor:sdl3`: Update to 3.4.2

- Add bindings to allow custom hardware cursors

- `core:nbio`: Fix op reuse

- `core:strings`: Fix `substring` not returning end of range

- `core:sys/windows`: Add more `win32` API bindings

- `core:sys/windows`: Fix incorrect `PVOID`/`VOID` use in some signatures

- `core:sys/windows`: Tighten up `MultiByteToWideChar` usage in `utf8_to_wstring_buf`

- `vendor:stb/vorbis`: Remove unnecessary `core:c/libc` import

- `vendor:wasm/WebGL`: Add bindings, fix `Tex*Image*D`

- `core:os`: Return `.Permission_Denied` for `.EACCES` in Posix and Linux

- `core:crypto/_blake2`: Fix final blocks call with partial block

- Kill deprecated file tags and fix assignment of package docs

## Full Change Log

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2026-02...dev-2026-03

---

## dev-2026-02 - 2026-02-04

**dev-2026-02** by gingerBill - <https://github.com/odin-lang/Odin/releases/tag/dev-2026-02>

## New Language Features

- `#+feature using-stmt`

  - `using` as a statement and procedure parameter modifier is now an opt-in feature on a per-file basis rather than on by default

  - `using` on struct fields still works

- `struct #simple`

  - force a struct to use simple comparison if all of the fields "nearly simply comparable"

  - This is a niche solution to a niche problem

  - "simply comparable" are types which can be compared with the equivalent of C's `memcmp` directly (e.g. integers, booleans, aggregates of them)

  - "nearly simply comparable" include the simply comparable types and floats, since floats have different rules for `+0`, `-0`, and `NaN`, and are NEARLY simply comparable if you don't care about those edge cases

  - This struct directive will force a struct to be "simply comparable" even if its fields would make it "nearly simply comparable"

## New Compiler Improvements

- Link-Time Optimization Support

  - `-lto:thin` and `-lto:thin-files`

- `#must_tail` directive and `preserve/none`/`preserve/most`/`preserve/all` calling conventions

  - Enables the ability to state how optimize for tail calls

- `-disable-unwind`

- Improvements to the constant conversion checks

- `intrinsics.count_leading_ones` and `intrinsics.count_trailing_ones`

- Show `-target` flag usage example in help

- Numerous debug info fixes

- Static linking on non-Windows platforms

- Add warning for `size_of(&x)` as it will always be `size_of(rawptr)` and probably a typo

- `-target:freestanding_amd64_mingw`

  - Allowing for linking to MinGW on Windows but for freestanding purposes (not general)

- Fix `string16` issues on Mac and Linux

- Fix `in`/`not_in` on constant `bit_set`s

- Allow `#+vet` tags always work in addition to command line flag

- General fixes to `-vet`

- Type assertions now use the same `context.assertion_failure_proc` as `assert` and `panic` where possible

- `#+feature force-type-assert` which overrides `-no-type-assert` on a per-file basis

- Fix numerous data races in the compiler frontend

- Fix numerous threading bugs in the compiler frontend

## New Packages

- `core:nbio`

  - Non-Blocking IO

- `core:container/handle_map`

  - Utilizing `core:container/xar` for stable backing data

## Package Improvements

- `core:thread`

  - Add `init` and `fini` callback procedures to thread pools

- `core:crypto`

  - Add initial support for short Weierstrass curves

  - General improvements and additions

- `core:testing`

  - Use Windows API for SIG handling on Windows

- `core:image`

  - Fix TGA header detections

  - `.do_not_expand_grayscale` for TGA

- `core:os`/`core:os/os2`

  - Fix `lookup_env_buf`

  - Fix truncate-clamp op order when determining to_read size

- `core:encoding/base64`

  - Add support URL variant

- `core:encoding/entity`

  - Update handling of 2-codepoint based entities

- `core:encoding/xml`

  - Correct how comment handling and entities

- `core:strings`

  - Add `loc := #caller_location` to allocating procedures that would benefit for it

- `core:sys/windows`

  - add a few procedure bindings

  - sync barriers

  - procedure-based "macros" for RawInput

- `core:text/regex`

  - Pass given allocator on in `create_iterator`

- `vendor:x11/xlib`

  - Binding fixes, correcting incorrect signatures

- `vendor:directx`

  - Improve string type uses in DirectX bindings

- `vendor:compress/lz4`

  - Fix linking on non-Windows platforms

- `vendor:curl`

  - Fix linking on all unix-like OSes

- `vendor:sdl3`

  - Add missing procedures `GetGpueDeviceProperties`

  - Fix signature of `RenderTextureRotated`

- `vendor:sdl3/image`

  - Update to 3.4.0

- Move `vendor:libc` to `vendor:libc-shim`

  - This is to clarify that it exists as a "shim" rather than a proper replacement

- Update Orca bindings

- General additions and improvements to `core:sys/linux`

- Bulk-write to a slice in xoshiro/pcg_random_generator_proc

- Fixes to darwin/Foundation bindings

## Full Change Log

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2026-01...dev-2026-02

---

## dev-2026-01 - 2026-01-05

**dev-2026-01** by Kelimion - <https://github.com/odin-lang/Odin/releases/tag/dev-2026-01>

## New Language Features

-

## New Compiler Improvements

- Undetected type declaration cycles work-around

- Fix misleading error messages for `init`, `fini` and `test` attributes

- Fix automatic `objc_msgSend` on static methods via selector expression not resolving aliased types

- Fix `#packed #all_or_none`

- Fix auto `objc_msgSend` incorrectly treating certain class methods as instance methods.

- Fix handling of `#force_inline`

- Fix literal endianness

## New Packages

- `core:container/xar`, an Odin-native implementation of an [Exponential Array](https://azmr.uk/dyn/#exponential-arrayxar)

## Package Improvements

- Fix duplicate `jpeg.load` on JS

- Added more `NSApplication` and `NSWindow` bindings

- Update `kb_text_shape` to v2.03

- Fix default temp allocator underflow bug

- SDL2: Use multi-pointer so you can pass array

- Fix function signature for memmove in `vendor:libc`

- Freebsd: Fixed 'write' syscall to cause 'ESPIPE' on the pipe fd

- Update `Box2d` to 3.1.1

- Fix `core:debug/trace` example

- Make `linux.IO_Vec.base` a multipointer

- Ensure libc is linked on Windows for `vendor:compress/lz4`

- Change Return Type of `sdl2.GetWindowFlags` from `u32` to Existing `WindowFlags` `bit_set`

- Fix minor issues within `curl` bindings

- `core:time/timezone` added additional search paths to match musl

- More bindings for Darwin

- Add `@builtin` to missing builtin procedure group procs

- os/os2: fix stale errors on windows when reading from console

- os/os2: better fix for the stale errors

- Fix `runtime.print_i64` using an OOB index when `min(i64)` is given.

- os/os2: use ReadFile for Console reads too, at least for now

- core:sys/linux Add timerfd syscall wrappers

- Fix `nfds_t` alias for Linux

- `core:io/utils`: fix buffer size in `write_*` procs

- `core:net` docs: recv of 0 bytes with no error is a graceful close

- `core:math/rand` small documentation fix

- Address issue identifying CDATA in XML file

- encoding/base32: Fix padding validation for malformed input

- Fix standard json parsing / unmarshalling issue for pure arrays

- Add user32 scroll bar related bindings, and FrameRect

- Add missing 'caller_location' to several procedures in 'slice' package

- Update `letter.odin`

- WebGL binding additions

- Add JSON5/SJSON Comments When Marshalling

- Fix Unicode Output When Marshalling JSON

- Allow Unmarshalling to rune

- Custom json (un)marshalling, similar to `core:fmt`'s custom formatters

- Fix `net.map_to_ip6` offset

- [vendor/sdl3] update to sdl 3.4.0

## Other

- Fix NetBSD CI by @krnowak in https://github.com/odin-lang/Odin/pull/6080

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2025-12a...dev-2026-01

---

## dev-2025-12a - 2025-12-04

**dev-2025-12a** by Kelimion - <https://github.com/odin-lang/Odin/releases/tag/dev-2025-12a>

## New Language Features

-

## New Compiler Improvements

- Fix duplicate code emission in type assertions.

## New Packages

-

## Package Improvements

- `core:os/os2`: Fix [#5873](https://github.com/odin-lang/Odin/issues/5873)

- Replace cURL library for Windows with one built against msvcrt

- Update cURL bindings to 8.17

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2025-12...dev-2025-12a

---

## dev-2025-12 - 2025-12-02

**dev-2025-12** by Kelimion - <https://github.com/odin-lang/Odin/releases/tag/dev-2025-12>

## Breaking changes

- BREAKING: Use `chacha8rand` as the default RNG.

The old default generator is available under `core:math/rand` in `rand_pcg.odin` in case you require a seed to return the same sequence as before.

## New Language Features

- Introduce `#all_or_none` for structs, which requires that struct literals have all or none of the fields set

## New Compiler Improvements

- Use SIP hash as name canonicalization hash

- Moved checking of `-vet-unused-procedures` and `-vet-packages` flags to after all flags are parsed

- Fixes for 32 bit with regards to typeid

- Fix [#5894](https://github.com/odin-lang/Odin/issues/5894)

- Remove `#no_copy`

- Don't check proc signature similarity for imported Objective-C methods

- Ubuntu arm ci and posix fixes

- Fix allocation of anonymous globals

- Fix [#5967](https://github.com/odin-lang/Odin/issues/5967): Incorrect stack overflow warning for by ref switches over unions

- Skip collision panic when package names aren't unique

## New Packages

- Add `vendor:curl`

## Package Improvements

- Improve docs for stable sort procedures

- Fix: `linalg.quaternion_from_forward_and_up`

- Clone unquoted strings in `encoding/json`

- Add missing `SetLayeredWindowAttributes`

- Add io uring API

- Add `FreeLibraryAndExitThread` in kernel32. Add `EnumProcessModules` in psapi

- Fix typo in `NS.String_initWithCString`

- Remove the Darwin-specific paths from `thread_unix`

- Fix `thread_act_t` size

- Fix: make `choice_bit_set` respect `bit_set` domain

- `math/rand`: Add range-based number generation procedures

- Fix `is_pointer_internally` not handling Named Types

- Faster `big.itoa`

- Add Xoshiro256 RNG

- Add `LockFileEx`/`UnlockFileEx` and related flags

- Fix `vendor:stb/image` resize `alpha_channel` parameter type to `c.int`

- Move some OS `General_Error` values to `io.Error`

- Fix out of bounds access when parsing end_pos

- Add `WSASendTo` and `WSARecvFrom`

- Update `d3d12` bindings for `D3D12_FEATURE_D3D12_TIGHT_ALIGNMENT`

- Add `NSWindow` coordinate space conversion bindings

- Don't build log allocator file on freestanding targets

- Adjust docs links for satellite SDL libraries

- Increase `base64` decoding table size to 256, preventing out of bounds reads

- `vendor/xlib`: a few more IM-related procedures and constants

- add `math.sign` and `math.sign_bit` overloads for int types

- Implement more Linux syscalls

- Add `SIO_UDP_CONNRESET` winsock constant

- `os2.File_Stream`

## Other

- Fix up macOS CI

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2025-11...dev-2025-12

---

## dev-2025-11 - 2025-11-04

**dev-2025-11** by gingerBill - <https://github.com/odin-lang/Odin/releases/tag/dev-2025-11>

## Licensing Changes

- Change Odin's LICENSE to zlib from BSD 3-clause

## New Language Features

- `intrinsics.concatenate`

  - Concatentation of constant slices, strings, and some arrays at compile time

- `intrinsics.objc_super` & `@(objc_superclass=<type>)`

## New Compiler Improvements

- Objective-C interface improvements

  - `intrinsics.objc_super` and automatically emit `objc_msgSend` calls where necessary for `@(objc_superclass)` attribute

  - Fix block symbols naming conflict across modules

- LLVM backend fixes

  - `#simd` vector only uses bit cast when elements are not pointers

  - Fix bitcasting `context` pointer to prevent compilation errors on LLVM-14

  - Numerous constant union improvements

  - Prefer the `Type *` ver `LLVMTypeRef` when looking up `struct_field_remapping` due to lack of uniqueness

- Default parameter exclusion counting improvement for procedure groups

- Improved `-target-features` flag by allow the user to disable a target feature

  - `-target-features:-sse,-sse2,-avx`

- `-export-linked-libs-file:<string>` flag to export the linked libraries to a file

- Fix a few compiler hangs on macOS.

- LLVM 21 support for non-Windows platforms

- Fix: `#load` alignment bug

  - set minimum alignment to 16-bytes

- Fix orca linking path

- Add `#subtype`/`using` to name canonicalization rules

- Numerous frontend bugs fixed

## New Packages

-

## Package Improvements

- More documentation improvements across the core library

- General improvements and more documentation for `core:os/os2`

- Add `inject_at_soa` and `append_nothing_soa`

- `vendor:wgpu` update to 27.0.2.0

- `core:unicode/utf8`: Add `Grapheme_Iterator`

- New `slice.sort` implementation to allow for better code generation and general API

- Deprecate the C style procedures in `strconv` (e.g. `iota`, `atoi`, etc`)

- WASM: Fix odin.js undefined `this.mem`

- Fix sRGB <-> linear RGB conversion

- `core:encoding/json` fixes

  - Fix `null` parsing in certain cases

- `core:encoding/cbor`: Fix epoch tag with small values

- `core:container/rbtree` add `find_or_insert`

- Fix bindings generator for `vendor:vulkan` for extensions and `~0` style constants

- Disable bounds checking where appropriate for Unicode and UTF-8 procedures

- `vendor:fontstash`: Fix crash with `.TTC` files

- `core:simd` : Fix incorrectly named calls in `bit_not`

- `vendor:sdl3`: Add `PointInRectFloat`

- `vendor/egl`

  - add a few more procedures and constants

  - Fix `GetPlatformDisplay` and `CreatePlatformWindowSurface` to use `int` instead of `i32`

- `vendor:box2d`

  - fixes to bindings mismatches

  - Add `targetAngle` to `RevoluteJoint` struct/procs

- `core:odin/parser`

  - fixes for `end_pos`

  - parse empty identifiers after selector as a selector expression with an empty field

- `core:hash`: add CCITT CRC-16

- Make packed conditional on `EPoll_Event` to match kernel

- `core:math/linalg/hlsl`: support `half` types

- `core:math/ease`: Add inverse ease procedures

- `vendor:raylib`: add `MAX_MATERIAL_MAPS` constant

- `core:sys/darwin/Foundation`: add additional AppKit bindings

- `core:text/scanner` allow for octal prefix style parsing for C-style ints

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2025-10...dev-2025-11

---

## dev-2025-10 - 2025-10-05

**dev-2025-10** by Kelimion - <https://github.com/odin-lang/Odin/releases/tag/dev-2025-10>

## New Language Features

-

## New Compiler Improvements

- Improve type inferencing of literals when calling proc groups

- Windows i386 support

- Fix Darwin `addObserver` methods and add support for new `Objc_Block`

- Fix segfault involving `string_to_string16` on Linux

- Improve OSX threading performance

- Basic support for constant union literals

- Add `-build-diagnostics`

- Prevent returning a struct containing compound literal slice

- Relax `signature_parameter_similar_enough` on struct params and fix various foreign signatures

- Preempt field checking on `signature_parameter_similar_enough` with a type ptr equality check

- Remove stray debug printf

## New Packages

- [core/image]: Add baseline JPEG support

## Package Improvements

- Use `.Image_Dimensions_Too_Large` in `core:image`

- `tick_now`: Use `f64` (was `f32`) as a return type of `odin_env.tick_now()`

- Allow missing trailing comma with proc groups in `core:odin` parser

- Fix incorrect json encoding for control characters < 32

- Initializing `big.Int` constants is now `"contextless"`

- Add `CancelIoEx` and other overlapped I/O functions.

- Add missing caller location param to append in `strings.Builder`

- Add "contextless" to small_array `get_safe` and `get_ptr_safe`

- Zero `small_array` resize

- Unify `filepath.join` return between Unix/Windows

- Fix out-of-band allocations in dynamic arenas by

- Fix for `temp_file` name prefix being deallocated before being used

- Add `runtime.conditional_mem_zero` to improve `heap_allocator` performance on non-Windows systems

- Add `digit_to_int` to `core:strconv`

- Remove inaccurate tprint comment

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2025-09...dev-2025-10

---

## dev-2025-09 - 2025-09-08

**dev-2025-09** by gingerBill - <https://github.com/odin-lang/Odin/releases/tag/dev-2025-09>

## New Language Features

- Native support for UTF-16 strings: `string16` and `cstring16`

  - Mostly for interfacing with Windows code, and other foreign code

- Define Integer Division By Zero https://github.com/odin-lang/Odin/pull/5556

## New Compiler Improvements

- `@(init)` and `@(fini)` must be `proc "contextless" ()`

- Implement `intrinsics.objc_block` @harold-b in https://github.com/odin-lang/Odin/pull/5547

  - Implements the Apple block ABI.2010.3.16 natively

- Improve deference missing suggestion message

- Do not check for explicit allocators when determining proc in proc group by @janga-perlind in https://github.com/odin-lang/Odin/pull/5564

- Skip errors on polymorphic procs when in a proc group with other options

- Fix compiler segfault when trying to use proc at type level or trying to use `()` as a type

## New Packages

-

## Package Improvements

- Fixes to `vendor:darwin/Metal`

- Numerous minor fixes to `base:runtime`

- Improvements to `base:runtime` docs

- Fixes to `vendor:wasm/WebGL` bindings

- Cleanup in `math/rand` and `runtime/random_generator`

- Add missing xlib functions for getting and setting text properties

- `vendor:OpenGL` fix misnamed parameter by

- Make D3D12_FEATURE_DATA_D3D12_OPTIONS.MinPrecisionSupport a bitset

- Fix buddy allocator assert

- Check for EOF when scanning file tags

- Fix stride in `memory_equal/compare_zero` giving false positves

- Split SDL_ttf bindings to group with and without require_results

- Propogate `#caller_location` to core:container/queue procs

- Support using allocator resize in `_reserve_soa`

- Zero existing memory when using `resize_soa`

- Add `add/remove_document_event_listener()` to `core:sys/wasm/js`

- Fixed and added obj-c methods for `NSWindow`

- fix typo in `CLSIDFromProgIDEx` signature

- Fix broken `wglUseFontBitmaps` binding

- Add `LPFN_GETACCEPTEXSOCKADDRS` to ws2_32.odin

- Specify `%m` and `%M `as verbs for integer formatting in `core:fmt`

- Add `@(require_results)` attribute to procs returning an allocator

- Handle allocator error when appending in `read_entire_file_from_file`

- `vendor:box2d` fix `CreateMotorJoint` procedure signature

- Add build tags to `posix/spawn.odin`

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2025-08...dev-2025-09

---

## dev-2025-08 - 2025-08-05

**dev-2025-08** by gingerBill - <https://github.com/odin-lang/Odin/releases/tag/dev-2025-08>

## New Language Features

-

## New Compiler Improvements

- General compiler bug fixes

- `intrinsics.type_enum_is_contiguous`

- `intrinsics.simd_runtime_swizzle`

- Add iOS and iPhoneSimulator subtargets for `-target:darwin`

- Fix `@(objc_implement)` methods not respecting `@(objc_is_class_method)`

- `@(objc_name)` attribute be inferrable

- Add `Did you mean?` for `card`/`len`

- `#+vet explicit-allocators`

- Saner stack linker flags for WASM

- Fix macos amd64 builds

- amd64 ABI fixes regarding certain types of SIMD vectors

## New Packages

-

## Package Improvements

- Update `core:prof/spall` to version 3

  - Adds @(no_instrumentation) to spall buffer and SCOPED operations

- `core:hash/xxhash`: Static SIMD Support for XXH3

- Minor fixes to `core:mem/virtual` edge cases

- Unix build script for `kb_text_shape`

- Add `IUnknown` UUID for win32 related code

- `crypto/hash`: hash_bytes_to_buffer slice result to digest size

- Minor fix to `-default-to-nil-allocator`

- Disable filepath/match.odin and filepath/walk.odin compilation on js targets

- Minor fixes to `SDL_image` save procedure that should return a boolean

- Mach Process Control

- Fix amd64 no-crt entry assembly

- Add cgltf filter type and wrap mode enums

- SDL2 - AudioAllowChangeFlags bit_set

- `core:thread` - set stack size to rlimit for \*nix platforms

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2025-07...dev-2025-08

---

## dev-2025-07 - 2025-07-09

**dev-2025-07** by Kelimion - <https://github.com/odin-lang/Odin/releases/tag/dev-2025-07>

## New Language Features

- Add `intrinsics.type_is_bit_field`

- Add `@(no_sanitize_memory)` with additions to `base:sanitizer`

## New Compiler Improvements

- Correct spelling in `odin doc -help` output

- Let `-test-all-packages` work with `-build-mode:test`

- Fix package docs

- Fix `swizzle` in `for in` statement

- Fix `divti3` not being exported

- Fix scope attribute proc grouping

- Forbid multiple uses of `-sanitize`

- `-vet-style`: Be strict with type switch case column alignment

- Let compound literal array be broadcast to a struct field of arrays

- Packages with `.odin` in the name no longer attempt to parse as odin files

- Let `-no-entry-point` work for Windows DLLs

- Guard against invalid proc types in parameter list

- Push `context` onto stack before evaluating procedure parameters

- Consider custom `#align` when determining union tag size

- Ensure `volatile` status for all atomic operations

- Fix WASM C ABI for raw unions

- Fix invalid selector for acceleration structure

- Fix `check_shift`

- Forbid nested declaration of instrumentation procedures

- Fix bug where compiler treated `uint` enums as `int`s

- Fix load type panic because front-end allows a deref of a type

- Added options to show, obfuscate, trim, and hide source code locations

- Various fixes

## New Packages

- `vendor/kb_text_shape`

## Package Improvements

- Add examples/all/sdl3 for all sdl3 dependant packages

- Rewrite `Atomic_RW_Mutex`

- Add overlapped I/O bindings for Windows

- Allow `odin check examples/all` for `js_wasm` target

- Guard against negative `index` in `inject_at`

- Print timings to stderr instead of stdout

- Change `os2.user_*` on Windows to use `SHGetKnownFolderPath`

- Add `core:os/os2` user dirs helper to retrieve common paths like Downloads, Videos, et al

- Clarify `strconv.append_*` to `strconv.write_*`

- Remove old @(deprecated) things.

- DXC: Fixed broken bindings of `ICompiler` and `ICompiler2`

- Fix GMT+/- timezone handling

- Clarify `core:flags` variadic behaviors

- Move `core:math/bìg` tests over to `core:testing` instead of using Python3 as an oracle

- Add initial tests for big rationals

- Sync chan refactor

- Replace `core:posix` usage in `core:os/os2`

- compat allocator improvements

- Fix `pool_join` hangs if no threads are started

- Fix early `join` after start

- Expose `getpeername` in `core:net` package as `peer_endpoint`

- Let tests expect assertion failures and signals raised

- Get env buffer

- Allow `core:net` to be imported with `-default-to-panic-allocator`

- Update vendor:sdl3 from 3.2.10 to 3.2.16, and vendor:sdl3/image from 3.2.0 to 3.2.4

- More `Buddy_Allocator` safeguards

- Fix RegEx docs

- Added TIOCGWINSZ to darwin, linux and freebsd

- Escape object file paths properly during linker_stage

- Fix `try_send` and `send`

- Added `IS_SUPPORTED` to `core:sys/posix`

- Fix issue parsing `vendor/stb/image` with the `core:odin/parser` parser

- Fix memory leak in `core:math/big.internal_rat_norm`

- raylib: Refer to Odin-style enum over original C enum

- sys/linux: Unify `IPC_Flags` and `IPC_Mode` bit_sets

- testing: Make test state changes its own feature

- Add `slice.suffix_length`

- Various fixes

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2025-06...dev-2025-07

---
