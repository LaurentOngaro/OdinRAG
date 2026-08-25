---
source: github-releases
repo: odin-lang/Odin
tag: consolidated
date: 2026-08-25
type: changelog
status: active
version: 1.0.0
lastUpdated: "2026-08-25T10:35:50Z"
updatedBy: "MiniMax-M3 (Kilo Code)"
tags: [OdinRAG, kb, source/official, changelog, odin]
---
# Odin Changelog (consolidated, 20 releases)

> Generated from the [odin-lang/Odin releases](https://github.com/odin-lang/Odin/releases) feed on 2026-08-25.
> Re-run `python _Helpers/scripts/scrapers/scrape_odin_changelog.py` to refresh.

## dev-2026-08 - 2026-08-06

**dev-2026-08** by Kelimion - <https://github.com/odin-lang/Odin/releases/tag/dev-2026-08>

## New Language Features
* Allow custom `-collection`s to be used for `foreign import`s in #6999

## New Compiler Improvements
* Disallow proc group assignment to blank identifier in #6996
* Increase stack size for threads in #6997
* Reject chained deferred procedures in #7013
* Fix arm64 ABI: '#simd' vectors and vector aggregates not passed in registers (#7010) by in #7015
* Fix darwin arm64 argument passing abi in #7030
* Fix playdate `-subtarget` issue where floats were incorrectly compiled in #7026
* Make object and assembly file extensions user-changeable again in #7041
* Fix subtype comparisons (#6151, #3689, #7020 and #4734) in #7039
* Fix constant aggregate rebuild in #7046
* Keep polymorphic probes read-only in #7052
* Fix `switch` fallthrough in `lb_emit_struct_ev` (#7050) in #7051
* Fix arm64 argument alignment abi for composite type of size <= 16 bytes in #7045
* Preserve recursive struct aliases in #7042
* Compare `mmap` result to `MAP_FAILED` rather than `nullptr` (#7053) in #7065
* Stricter type coercions in `convert_to_typed` in #7056
* Fix backend deadlock where `func_raw_types_mutex` and `types_mutex` were waiting on each other by in #7060
* Add `typeid` constant case to `check_comparison` (#7027) in #7064
* Fixes compile time equality comparison for `string16` in #7071
* Allow fixed-capacity arrays in constant unions (#7089) in #7090
* Fixes spurious `#no_alias` compile errors during polymorphic overload resolution in #7116
* Reject the use of labels as expressions (#5830 and #7108) in #7130
* Fix hang for poly procs with default proc literal params in #7146
* Fix `expand_values` panic on type expressions in #7157
* Handle spaces in args for 'odin run . -- <args>' on Windows in #7162
* Don't assert on `-define:` values with an exponent in #7164
* Fix error hint for vet tag in #7132
* RISC-V fixes/improvements in #7144
* Fix LLVM codegen for matching on `nil` for `union{}` in #7139
* Allow `#caller_expression` on constant parameters which are procedures in #7119
* Fixes compile error due to `#no_alias` shifting position in procs with indirect return in #7214
* Fixes a compiler segfault with zero sized parameters on targets that ignore these in the LLVM signature in #7215
* Fix every named argument in "Given argument types" being labelled with the first argument's name in #7217
* Fix `levenstein_distance` in #7218
* Fix signed Int Constants being permitted to exceed size in #7220
* Fix `string16` oob in #7221
* Fix new line suppression by @kalsprite in #7222
* Improve grammar on import name error in #7223
* Fix matrix col error message that said rows instead in #7224
* Minor typos in #7225
* Fix crash on poly in #7226
* Fix `-vet-packages` not working in certain cases in #7210
* Pack tuple results into variadic arguments (#7167) in #7185
* Polymorphic procedures resolving to `nil` (#6753 and #) in #7208

## New Packages
* `[core:crypto/rsa]` Add RSA support in #6857
* `[core:encoding/asn1]` Add strict DER + `[core:crypto/x509]` (X.509 v3) in #6838
* `[core:crypto/turboshake]` Add TurboSHAKE in #7043
* `[core:rexcode]` Add rexcode, a high-performance multi-architecture instruction encoder/decoder/printer package in #6839
* `[core:debug/trace]` Replaced with a much improved implementation in #7141

## Package Improvements
* `[core:container/rbtree]` Match `find_or_insert` semantics with AVL in #6988
* `[core:container/rbtree]` Add `upsert` in #7002
* `[vendor:box3d]` Fix missing return value of `*_GetUserData` functions in #7006
* `[core:sys/windows]` Add additional bindings in #7022
* `[vendor:raylib]` Update `rlgl` bindings to raylib 6 in #7023 and #7028
* `[core:strings]` Add `@(require_results)` where useful in #7038
* `[core:log]` Make multi logger use all loggers instead of breaking on first non match in #7057
* `[core:encoding/csv]` Update example to use the new `core:os` in #7076
* `[base:runtime]` Fix markdown table in docs in #7077
* `[base:runtime]` Fix map reporting incorrect capacity after shrinking in #7097
* `[core:os]` Fixes file open emulation of posix open behavior on mode/perm mismatch on Windows in #7098
* `[base:runtime]` Fixes SoA dynamic arrays not zeroing all elements after shrink + grow in #7103
* `[core:odin/tokenizer]` Set token kind to float for hex floats in #7117
* `[vendor:sdl3]` Fix `(S/G)etDefaultTextureScaleMode` in #7133
* `[core:unicode]` Fix duplicated entries within `unicode_spaces` and `space_ranges` in #7142
* `[base:runtime]` Fixes growth check for SoA dynamic arrays in #7145
* `[core:debug/trace]` Sync tracking allocator with `core:mem` in #7147
* `[core:debug/trace]` Sync allocator with `core:mem` in #7200
* `[core:sys/windows]` Fix `LoadLibraryEx_Flags` off-by-one in #7151
* `[core:mem/virtual]` Close dangling handle in `map` implementation on Windows in #7159
* `[core:testing]` Respect `TERM=dumb` in test runner to prevent ANSI sequences, color in #7160
* `[core:thread]` Add `get_name` and `set_name` in #5464
* `[base:runtime]` Shrink `map` to minimum capacity with `shrink` in #7152
* `[core:text/scanner]` Fix #7153 and add a test in #7165
* `[core:rexcode/x86]` Label addressing for RIP-relative disp and movabs imm in #7168
* `[core:simd/arm]` Implement simd arm crc32 in #7174
* `[core:compress/gzip]` Fix example code in #7178
* `[core:simd/arm]` Implement simd arm pmull in #7184
* `[base:runtime]` Follow up fix of `shrink_map` #7182
* `[core:odin/parser]` Correct end position for fields with a specialization in #7180
* `[core:text/scanner]` Fix octal escape parsing in #7176
* `[core:os]` Update stale `os.flags` file doc in #7187
* `[core:mem]` Zero `tracking_allocator.allocation_map` and `tracking_allocator.bad_free_array` in `destroy` in #7195
* `[base:runtime]` Make soa builtins go vroom in #7196
* `[base:runtime]` Cleans up obsolete comments in `_append_soa_elems` in #7204
* `[base:runtime]` Annotates the array parameter of dynamic array builtins with `#no_alias` in #7149
* `[core:simd/arm]` Impl fix simd arm SHA in #7205
* `[core:os]` Fix `glob` not cloning pattern when no meta characters present in #7206
* `[core:crypto/_fiat]` Fix conditional in `ensure` in #7211
* `[vendor:box3d]` Update box3d (#7177) to https://github.com/erincatto/box3d/commit/3fc20f5b453ba9e14cdf54ecafa87a2a4bcdf53c in #7212 + #7231
* `[core:crypto]` Minor fixes in #7228
* `[core:os]` Resolve relative path before `SHFileOperationW` in `_remove_all` in #7230
* `[core:net]` Fix percent encoding for bytes < 0x10 (#7109) in #7234
* `[core:simd/arm]` Implement simd arm neon bit manipulation in #7216

* Various typo fixes across the packages

## Miscellaneous
* `[vendor:*]` Replace makefiles in with shell scripts in #7034
* CI: Update NetBSD to `10_2026Q1` in #7085
* Improve build scripts portabability and make them `pwd` independent in #7084
* CI: Make NetBSD CI less prone to breaking when scheduled on old CPUs

## What's Changed

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2026-07a...dev-2026-08

---

## dev-2026-07a - 2026-07-10

**dev-2026-07a** by Kelimion - <https://github.com/odin-lang/Odin/releases/tag/dev-2026-07a>

## What's Changed
* Add pull request policy to `vendor/README.md`
* Fix `vendor:raylib` 6.0 bindings
* Update `vendor:box3d` to latest commit in #6986
* Fix for `@(objc_implement)` being broken in `dev-2026-07` release in #6990
* Ensure identical types have same hash by in #6974
* Prevent git output with signature information in #6973
* Update wgpu.js in #6975
* Fix parser failing on comments inside ternary expressions in #6968
* fix `assign_at_elems_fixed_capacity_dynamic_array` in #6993
* Fix #6979 in #6987
* Remove `default` help option for stack protector in #6984
* Update `kb_text_shape` to v2.21 in #6944

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2026-07...dev-2026-07a

---

## dev-2026-07 - 2026-07-06

**dev-2026-07** by Kelimion - <https://github.com/odin-lang/Odin/releases/tag/dev-2026-07>

## New Language Features
* Add restricted Odin subset mode `-bedrock` in #6654
* Add [Playdate](https://play.date) support as a `-subtarget` of `-target:freestanding_arm32` in #6900
* Support `q.xyz` on quaternion*

## New Compiler Improvements
* New Feature: Stack canaries #6830
* Change default settings to enable pie and full relro on Linux in #6790
* Make the type hash 63-bit to not crash OMG JIT in WebKit under WASM in #6829
* Add suggestion to use 'typeid_of(type)' when trying to do `typeid(type)` in #6846
* `@(test)` procs in `#+private` files are now processed in #6844
* Reject transitive `#subtype-only` implicit conversion in checker in #6845
* Fix initialization of global `any`s #6849
* Fix: tuples are not handled properly in struct literals in #6859
* Move away from `system` for `odin run` in #6848
* Raise child process error signal if `odin run` child gets terminated #6870
* Flush accumulated errors before printing assert in #5508
* Fix #6874 in #6880
* Fix #6885 in #6886
* Resolve panic on 64-bit constant overflow in #6904
* Fix constant union stuff against tests in #6905
* Report range type correctly on out-of-bounds in #6906
* Add more constant type cases in #6913
* Use `lb_add_values_to_array` for `cvarargs` in #6908
* Only allow direct `CVarArg` usage in `c_va_start` in #6916
* Add ways to diff anon procs with same signature in #6920
* Fix compiler segmentation fault when field names start with '.' in #6928
* Fix UTF-8 decode error check in #6930
* Improve custom output location (`-out`) support for LLVM-IR, OBJ + ASM in #6932
* Fix typo in union error in #6929
* Make checking of untyped to union conversions more strict in #6925
* Allow casts to change mode for array programming in #6921
* Avoid code regeneration for fns in unroll in #6939
* Make diverging `or_else` inherit `#load` lhs type in #6934
* Add diverging (`!`), `#optional_ok` to proc canon name in #6935
* Fix misuse of `lb_emit_(min|max)` in `simd_(min|max)` in #6924
* Remove support for LLVM 14, suggest apt.llvm.org if `llvm-config-14` can't be found in #6918
* Use specific format to make `f64` strings canonical in #6949
* Disallow types in `#any_int` params in  #6950
* Convert poly const int to `f64` when needed in #6948


## New Packages
* [core:raylib] Raylib 6.0 in #6940
* [vendor:box3d] Box3D bindings in #6933

## Package Improvements
* [core:terminal/ansi] Add Alternate Screen Buffer in #6813
* [core:nbio] Fix UAF op `op.l` in cross-thread exec in #6819
* [core:slice] Fix wrong variable name in `slice.rotate` in * fixed wrong variable name in #6828
* [vendor:vulkan] Update Vulkan in #6824
* [core:container/pool] Fix ABA race in the free list in #6822
* [core:bufio] Improve `reader_read_slice`'s documentation using the power of punctuation in #6463
* [base:runtime] Added optional allocator error to `map_insert` in #6836
* [core:odin] Correct divergence from C++ parser with expr levels, causing failures in #6861
* [vendor:stb/truetype] Amend `PackFontRanges` types in #5662
* [core:mem] Rename `DEFAULT_PAGE_SIZE` to `PAGE_SIZE` in #6471
* [core:os] Improve consistency in `os.read_entire_file_from_file` in #6671
* [core:flags] Improve `bit_set` support in #6435
* [vendor:x11/xlib] Update `Xlib` documentation link to current PDF in #6875
* [core:text/regex] Improve regex compiler performance in #6873
* [core:mem] Fix `mem.Dynamic_Arena` alignment in #6878
* [core:crypto/wycheproof] Update the tests to match recent changes in #6887
* [vendor:sdl3] Remove non-exported `joystick_lock` symbol in #6893
* [vendor:windows/GameInput] Remove `GameInput` prefix from interface type names in #6903
* [core:encoding/entity] Fix whitespace normalization in #6914
* [core:container/handle_map] Remove unused `base:builtin` import in #6931
* [vendor:wgpu] Update to v29.0.1.1 in #6947
* [core:encoding/cbor] Fix segfault decoding map/big.int nested in slice elements in #6945
* [core:encoding/cbor] Fix data corruption in #6954
* [vendor:wgpu] Update to v29.0.1.1
* [core:container/xar] Forward caller location to make in `array_push_back_*` in #6958

## Miscellaneous
* Fix nightly static Linux build in #6808
* Added missing `LDFLAGS` for `OpenBSD` in #6728
* Deduplicate macOS and Linux nightly builds in #6812
* Remove dependency on `mbedx509`, `mbedcrypto` for Darwin in #6842

## What's Changed

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2026-06...dev-2027-07

---

## dev-2026-06 - 2026-06-10

**dev-2026-06** by Kelimion - <https://github.com/odin-lang/Odin/releases/tag/dev-2026-06>

## New Language Features
* Add `@(fast_math)` attribute (PR #6676)
* Support `**` as `expand_values` operator: `**x` == `expand_values(x)` (PR #6731)

## New Compiler Improvements
* Better error reporting for unary `++`/`--` (PR #6649)
* Removed Haiku from supported targets (PR #6631)
* Better SIMD generation for square matrix multiplication and `intrinsics.transpose` (PR #6676)
* Fix `deferred_return` and segfault in docs writer (PR #6668)
* Fix issue #6429, `odin doc` handling of Fixed Capacity Dynamic Arrays in `write_expr_to_string` (PR #6670)
* Add duplicates checking in type switches by @Creativty (PR #6702)
* Fix `nil` typing for procedure call arguments (PR #6701)
* Fix issue #6096, honor `-no-thread-local` for variables declared at procedure scope (PR #6696)
* Improve `simd.runtime_swizzle` and its documentation (PR #6712)
* Improve thoroughness of generic procedure type detection (PR #6711)
* Fix race condition relating to type specialization (PR #6716)
* Fix issue 6692, `using` on bit fields (PR #6742)
* Fix error pos style environment variable overwriting commandline argument (PR #6741)
* Properly check `#any_int` param operands (PR #6740)
* Fix assertion failure when comparing array-backed `bit_field`s (PR #6773)
* Disallow `*` and `/` for `bit_set`s (PR #6777)
* `AArch64` assembly support for `foreign import` (PR #6784)
* Fix error message "`do` not on the same line as `for`" (PR #6794)

## New Packages
* Add ML-KEM (FIPS 203) post-quantum key encapsulation support (PR #6635)
* Add ML-DSA (FIPS 204) post-quantum digital signature support (PR #6695)
* Add intial PEM support (PR #6755)

## Package Improvements
* Improve consistency between platforms for `os.copy_directory_all` (PR #6651)
* Use `context.assertion_failure_proc` in tracking allocator bad free callback (PR #6659)
* Add `DefSubclassProc` binding (PR #6664)
* Make `make_aligned` and `new_aligned` builtins (PR #6677)
* Handle invalid utf8 when parsing json (PR #6669)
* Fix xlib binding signatures (PR #6680)
* Add unicode mapping between 'ẞ' <-> 'ß' (PR #6672)
* Fix missing `only_if_exists` parameter in `x11.XInternAtoms` (PR #6684)
* Convert `(f)stat` calls to `statx` in Linux `core:os` implementation (PR #6683)
* Additional xlib binding changes (PR #6687)
* Fix `read_slice` typo in `core:io/utils` (PR #6697)
* Document `strconv.parse_int` and `strconv.parse_uint` (PR #6706)
* `core:math/linalg`: Add Gram-Schmidt orthonormalize (PR #6707)
* `vendor:wgpu`: Fix incorrect proc signatures (PR #6661, PR #6724)
* Add support to unmarshal the new fixed capacity dynamic arrays (PR #6713)
* `core:encoding/base64`: Misc fixes and improvements (PR #6733)
* `core:strconv`: Fix upper bound of Decimal in `round_shortest` (PR #6734)
* `vendor:directx/d3d12`: Add `IDevice10` interface (PR #6602)
* `vendor/README.md` fix inverted SDL2 and SDL3 (PR #6749)
* Swap `panic_contextless` and `unimplemented_contexless` documentation (PR #6758)
* `core:sys/linux`: Remove parapoly from `rt_sigaction` (PR #6756)
* `core:slice`: Fix `rotate_left` crash on empty array (PR #6771)
* `core:sys.info`: Prefer mem info from `/proc/meminfo` over `sysinfo()` (PR #6765)
* `core:mem` / `core:testing`: Fix buffer overflow when running a test which shrinks a dynamic array (PR #6791)

## Miscellaneous
* Add `/src` as safe directory for nightly linux arm workflow (PR #6658)
* Link against `libstdc++exp` for backtrace support (PR #6732)

## Full Change Log
**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2026-05...dev-2026-06

---

## dev-2026-05 - 2026-05-04

**dev-2026-05** by Kelimion - <https://github.com/odin-lang/Odin/releases/tag/dev-2026-05>

## New Language Features
* Native Array Casting Semantics, e.g. `cast([4]f32)4x_u32` (PR #6605)
* Increase `matrix` limit from 16 to 64 elements, allowing for up to `matrix[8, 8]T`

## New Compiler Improvements
* Add -debug default behavior usage docs (PR #6511)
* Fix output of filename when outputting docs with the `-in-source-order` option (PR #6536)
* Fix `#no_bounds_check` regression (PR #6541)
* Fix target feature lookup, canonicalize `target_features_set` (PR #6544)
* Fix (Issue #6344) - Field-first index writes on `#soa[dynamic]T` and `#soa[]T` (PR #6539)
* Fix `aligned_alloc` not defined on Android/Bionic (PR #6519)
* Fix `break`/`continue` being allowed in a nested unrolled range loop (PR #6521)
* `SROA` and simplification passes on `-o:minimal` (PR #6553)
* Fix array counts for floats that are exactly representable as integers e.g. `[1.1e4]int` (PR #6583)
* Prevent coredump when child process gets killed by signal (PR #6586)
* Support multiple return values within compound literal elements (PR #6596)
* Fix (Issue #5422) - Make `@(rodata)` on constants yield "not supported" message (PR #6601)
* Fix (Issue #6594) - Report cycle when assigning variable to itself (PR #6599)
* Fix (Issue #6621) - Report cycle for `type_of` (PR #6624)
* Removed moribund `Essence` OS from supported targets (PR #6623)
* Add `intrinsics.c_va_*` (PR #6629)
* Fix type info not being generated for types only used in `[]typeid` literals (PR #6630)
* Fix compiler warning on Linux (PR #6638)

## New Packages
* [core:crypto/noise] Add Noise implementation (PR #6573)

## Package Improvements
* [core:os] Add `dir` procedure (PR #6517, PR #6528)
* [base:runtime] Native simd width (PR #6545)
* [core:os] Fix `_volume_name_len` to handle paths of purely path separators (PR #6547)
* [core:math/linalg] Faster `dot`, `cross3`, `floor`, `ceil`, and add `trunc` (PR #6549)
* [core:math/linalg] More matrix related calls: `pseudo_inverse`, `inverse_lu_decomposition`, `matrix_inverse_gauss_jordan`
* [core:mem/virtual] Fix arena overcommit bug (PR #6552)
* [core:sys/linux] Fix missing argument in `adjtimex` syscall (PR #6502)
* [vendor:wgpu] Update to v29.0.0.0 (PR #6551)
* [core:sys/freebsd] Add `ioctl` and `stdio` `FILENO` constants (PR #6537)
* [core:nbio] Handle `EOF` in poll on Posix (PR #6556)
* [core:container/xar] Fix a typo in example (PR #6559)
* [core:testing] Ensure `make_*` style bounds traps are handled in test runner `expect_signal` on Windows (PR #6563)
* [core:sys/windows] Add I/O Ring API bindings (PR #6562)
* [vendor:directx/d3d12] Fix `D3D12_BARRIER_SUBRESOURCE_RANGE` struct (PR #6557)
* [core:testing] Fix stop reason being wrong for OOB on Windows (PR #6570)
* [core:fmt] Remove redundant 'defer bufio.writer_flush' from `fprint` procs (PR #6567)
* [vendor:zlib] Fix signature of `inflateInit_` (PR #6566)
* [vendor:sdl3] Mixer: Removed `#by_ptr` from args that are valid as `nil` (PR #6576)
* [core:mem/virtual] Fix `map_file` usage example (PR #6577)
* [core:mem/virtual] Add `address_hint` to `reserve` (PR #6558)
* [core:os] Fix `stem` on empty path (PR #6579)
* [core:path/filepath] Create wrappers for allocating procedures (PR #6575)
* [core:fmt] Omit value when formatting `map[T]struct{}` sets (PR #6581)
* [vendor:vulkan] Add version macros (PR #6565)
* [core:sys/windows] Add Registry Association API (PR #6525)
* [core:sys/windows] Fix `LockFileEx` and `UnlockFileEx` (PR #6625)
* [core:math/linalg] Fix negated quaternions in `angle_from_quaternion` (PR #6607)
* [core:sys/linux] Emulate `dup2` better on arm64 and riscv (PR #6632)

## Full Change Log
**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2026-04...dev-2026-05

---

## dev-2026-04 - 2026-04-03

**dev-2026-04** by Kelimion - <https://github.com/odin-lang/Odin/releases/tag/dev-2026-04>

## New Language Features
* [Fixed Capacity Dynamic Arrays](https://github.com/odin-lang/Odin/pull/6406), adds `[dynamic; N]T`

## New Compiler Improvements
* Limit maximum exponent of integer literals to avoid unnecessary work
* Add `-in-source-order` option to `odin doc` to show docs in source order within each file
* Support clang-style `+`/`-` prefixes in target features
* Fix #6396: handle full-width `bit_field` literal masks
* Fix #6401: generic cycle deadlock in struct layout
* Add support for other Android architectures
* Fix #5602: "Internal Compiler Error: Type_Info for 'x' could not be found" for poly procs with named parameters
* Continuous Compiler Improvements
* Add initial LLVM 22 support on non-Windows platforms
* More accurate `-march:native` feature selection
* Allow pointers to types which have subtype fields at offset 0 to be assignable in proc parameters.
* `offset_of(some_bit_field)` now raises a proper error
* Add `intrinsics.type_field_bit_offset(typeid, string)` to get a compile-time `bit_field` field offset in bits
* Add `intrinsics.type_field_bit_size(typeid, string)` to get a compile-time `bit_field` field size in bits (the value after `|`)
* Fix #6407: Global unions do not get initialized correctly
* Fix `>=` comparison `base:runtime` dependencies for `string` and `cstring` types
* Fix `GB_PANIC` format string in `lb_emit_conv` invalid subtype cast
* Fix `[^]u16` to `cstring16` transmute condition in `lb_emit_conv`
* Remove `Tilde` backend
* Fix #6484: Two `when` blocks which evaluate to `true` in a `foreign` block misses following decls
* Fix declaration order bug #6506: False-positive `where`-clause failures in recursive polymorphic subtype cases
* Fix declaration order bugs #5572 and #5961: Incorrectly rejecting valid in-progress/forward union references

## New Packages
* `core:crypto/argon2id` initial import
* `vendor:windows/wasapi`
* `vendor:sdl3/mixer`

## Package Improvements
* Add more JS to `examples/all`
* Update Unicode database to newer version
* Fix modular exponentiation in `core:math/big`
* Fix `assign_at` documentation
* `core:fmt` now formats `time.Duration` with a space between duration and unit when using `% v`
* Correct SIMD `shr` example documention
* Fix `sync.Auto_Reset_Event` signal deadlock
* `core:sys/darwin/Foundation`: fix `NSTimer` binding
* Partial 1.619.x d3d12 bindings
* `core:mem/virtual`: Fix for virtual arena overcommit bug #5821
* `core:crypto`: Add ARM AES hardware acceleration
* `core:crypto`: Add ARM SHA256 hardware acceleration
* `core:fmt`: Improve `core:container/small_array` formatting
* `vendor:stb/vorbis`: Add WASM support
* `core:encoding/cbor`: Fix order-dependent partial unmarshals
* `core:encoding/json`: Fix user unmarshaler example
* Fix possible OOM in `core:os.get_working_directory()` on Linux
* Fix #6455: `core:mem/virtual.map_file_from_path` ignores flags
* Fix for corner case in the `core:mem` scratch allocator.
* Minor cleanup in `base:runtime` and `core:mem`
* Fix #6495: Handle starting separator during name comparison in `core:os`
* Improved `delete_key` documentation to mention it's safe to delete keys while iterating a map as long as no resizes take place
* Fix source size check in `core:crypto/aes` ECB encrypt/decrypt

## Full Change Log

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2026-03...dev-2026-04

---

## dev-2026-03 - 2026-03-04

**dev-2026-03** by Kelimion - <https://github.com/odin-lang/Odin/releases/tag/dev-2026-03>

## BREAKING Changes

* `core:os` has been replaced with our newly improved and rewritten v2, previously available at `core:os/os2`. The old `core:os` implementation will remain available at `core:os/old` until sometime in Q3 of 2026.
  * Article on [Moving Towards a New `"core:os"`](https://odin-lang.org/news/moving-towards-a-new-core-os/)

* `core:sys/info` previously retrieved all information before `main` was entered, using `@(init)`, and exposed everything via globals. It now gathers more information on demand, and returns everything via accessors for a consistent API. Where practical - like cpu name + features - those values will be cached.

## New Language Features

* `for init; x in y {}` style loops

## New Compiler Improvements
* Stop silently ignoring unknown directives on an inline `asm` expression
* Do not allow duplicated `#partial` directives on switch statements
* Add broadcasting to strings (Fix #1837)
* Improve LLVM version picking
* Fix name canonicalization for typed ranges in `bit_set`
* Fix `bit_set` parapoly specialization
* Fix separating of diverging procedure types from block statements
* Update `Type_Info_Bit_Set` to always record underlying type. Add `runtime.type_info_underlying`
* Fix #6347
* Fix #6270

## New Packages
* `core:crypto/ecdsa`: Add ECDSA support

## Package Improvements
* [BREAKING] `core:os/os2` -> `core:os` integration
* [BREAKING] `core:sys/info`: Change API from globals to calls. Do as little work in `@(init)` as practical.
* Allow test names to be specified as a command line option for tests executable
* `vendor:x11/xlib`: Fix signature of XChangeWindowAttributes
* `vendor:directx/d3d12`: Added `IGraphicsCommandList7` and fix access violation errors
* Minimize some internal depencies in the `core` packages, e.g. don't import `core:mem` just for `mem.Allocator_Error`
* `vendor:box2d`: Fix and try Git LFS
* `core:log`: Add support for `js/wasm`
* `core:container/xar`: Fixes and improvements
* `core:container/pool`: Fix parapoly type inference around address sanitization when using multiple Pool types
* `core:container/handle_map`: Improvement
* `demo.odin` Fix `cross_3d` typo
* `core:encoding/hex`: Add uppercase encoding
* `core:bytes`: Update comment on `compare`; add additional caller location propagation
* `core:math/big`: Clean up
* `core:os`: Fix silent failure in `os.replace_path_separators` if the separator was multi-byte
* Add additional tests
* `core:sys/es`: Fix build errors
* `core:unicode/utf8`: Fix utf-8 validation
* Vendor Wycheproof cryptographic tests under `tests/core/`
* Propagate allocator errors from certain unicode functions
* Fix some tools and examples after `core:os` update and `using-stmt` feature
* Fix typo in `atomic.odin` documentation
* `core:os`: Remove `process_close` and add `process_terminate`
* `core:time`: Correct 12-hour clock string
* Update Unicode specification
* `vendor:curl`: Fix `what` argument for `url_set`
* Small optimization for dynamic arrays
* `vendor:miniaudio`: Upgrade to 0.11.24
* `core:container/priority_queue`: Add example and tests
* `core:text/regex`: Fix `\b` handling in iterator
* `vendor:sdl3`: Update to 3.4.2
* Add bindings to allow custom hardware cursors
* `core:nbio`: Fix op reuse
* `core:strings`: Fix `substring` not returning end of range
* `core:sys/windows`: Add more `win32` API bindings
* `core:sys/windows`: Fix incorrect `PVOID`/`VOID` use in some signatures
* `core:sys/windows`: Tighten up `MultiByteToWideChar` usage in `utf8_to_wstring_buf`
* `vendor:stb/vorbis`: Remove unnecessary `core:c/libc` import
* `vendor:wasm/WebGL`: Add bindings, fix `Tex*Image*D`
* `core:os`: Return `.Permission_Denied` for `.EACCES` in Posix and Linux
* `core:crypto/_blake2`: Fix final blocks call with partial block
* Kill deprecated file tags and fix assignment of package docs

## Full Change Log

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2026-02...dev-2026-03

---

## dev-2026-02 - 2026-02-04

**dev-2026-02** by gingerBill - <https://github.com/odin-lang/Odin/releases/tag/dev-2026-02>

## New Language Features

* `#+feature using-stmt`
  * `using` as a statement and procedure parameter modifier is now an opt-in feature on a per-file basis rather than on by default
  * `using` on struct fields still works
* `struct #simple`
  * force a struct to use simple comparison if all of the fields "nearly simply comparable"
  * This is a niche solution to a niche problem
  * "simply comparable" are types which can be compared with the equivalent of C's `memcmp` directly (e.g. integers, booleans, aggregates of them)
  * "nearly simply comparable" include the simply comparable types and floats, since floats have different rules for `+0`, `-0`, and `NaN`, and are NEARLY simply comparable if you don't care about those edge cases
  * This struct directive will force a struct to be "simply comparable" even if its fields would make it "nearly simply comparable"

## New Compiler Improvements

* Link-Time Optimization Support
  *  `-lto:thin` and `-lto:thin-files`
* `#must_tail` directive and `preserve/none`/`preserve/most`/`preserve/all`  calling conventions
  * Enables the ability to state how optimize for tail calls
* `-disable-unwind`
* Improvements to the constant conversion checks
* `intrinsics.count_leading_ones` and `intrinsics.count_trailing_ones`
* Show `-target` flag usage example in help
* Numerous debug info fixes
* Static linking on non-Windows platforms
* Add warning for `size_of(&x)` as it will always be `size_of(rawptr)` and probably a typo
* `-target:freestanding_amd64_mingw`
  * Allowing for linking to MinGW on Windows but for freestanding purposes (not general)
* Fix `string16` issues on Mac and Linux
* Fix `in`/`not_in` on constant `bit_set`s 
* Allow `#+vet` tags always work in addition to command line flag
* General fixes to `-vet`
* Type assertions now use the same `context.assertion_failure_proc` as `assert` and `panic`  where possible
* `#+feature force-type-assert`  which overrides `-no-type-assert` on a per-file basis
* Fix numerous data races in the compiler frontend
* Fix numerous threading bugs in the compiler frontend

## New Packages

* `core:nbio`
  * Non-Blocking IO
* `core:container/handle_map`
  * Utilizing `core:container/xar` for stable backing data

## Package Improvements

* `core:thread`
  * Add `init` and `fini` callback procedures to thread pools
* `core:crypto`
  * Add initial support for short Weierstrass curves
  * General improvements and additions
* `core:testing`
  * Use Windows API for SIG handling on Windows
* `core:image`
  * Fix TGA header detections
  * `.do_not_expand_grayscale` for TGA
* `core:os`/`core:os/os2`
  * Fix `lookup_env_buf`
  * Fix truncate-clamp op order when determining to_read size
* `core:encoding/base64`
  * Add support URL variant
* `core:encoding/entity`
  * Update handling of 2-codepoint based entities
* `core:encoding/xml`
  * Correct how comment handling and entities
* `core:strings`
  * Add `loc := #caller_location` to allocating procedures that would benefit for it
* `core:sys/windows` 
  * add a few procedure bindings
  * sync barriers
  * procedure-based "macros" for RawInput
* `core:text/regex`
  * Pass given allocator on in `create_iterator`
* `vendor:x11/xlib`
  * Binding fixes, correcting incorrect signatures
* `vendor:directx` 
  * Improve string type uses in DirectX bindings
* `vendor:compress/lz4`
  * Fix linking on non-Windows platforms
* `vendor:curl`
  * Fix linking on all unix-like OSes
* `vendor:sdl3`
  * Add missing procedures `GetGpueDeviceProperties`
  * Fix signature of `RenderTextureRotated`
* `vendor:sdl3/image`
  * Update to 3.4.0
* Move `vendor:libc` to `vendor:libc-shim`
  * This is to clarify that it exists as a "shim" rather than a proper replacement
* Update Orca bindings
* General additions and improvements to `core:sys/linux` 
* Bulk-write to a slice in xoshiro/pcg_random_generator_proc
* Fixes to darwin/Foundation bindings


## Full Change Log

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2026-01...dev-2026-02

---

## dev-2026-01 - 2026-01-05

**dev-2026-01** by Kelimion - <https://github.com/odin-lang/Odin/releases/tag/dev-2026-01>

## New Language Features

* 

## New Compiler Improvements

* Undetected type declaration cycles work-around
* Fix misleading error messages for `init`, `fini` and `test` attributes
* Fix automatic `objc_msgSend` on static methods via selector expression not resolving aliased types
* Fix `#packed #all_or_none`
* Fix auto `objc_msgSend` incorrectly treating certain class methods as instance methods.
* Fix handling of `#force_inline`
* Fix literal endianness

## New Packages

* `core:container/xar`, an Odin-native implementation of an [Exponential Array](https://azmr.uk/dyn/#exponential-arrayxar)

## Package Improvements

* Fix duplicate `jpeg.load` on JS
* Added more `NSApplication` and `NSWindow` bindings
* Update `kb_text_shape` to v2.03
* Fix default temp allocator underflow bug
* SDL2: Use multi-pointer so you can pass array
* Fix function signature for memmove in `vendor:libc`
* Freebsd: Fixed 'write' syscall to cause 'ESPIPE' on the pipe fd
* Update `Box2d` to 3.1.1
* Fix `core:debug/trace` example
* Make `linux.IO_Vec.base` a multipointer
* Ensure libc is linked on Windows for `vendor:compress/lz4`
* Change Return Type of `sdl2.GetWindowFlags` from `u32` to Existing `WindowFlags` `bit_set`
* Fix minor issues within `curl` bindings
* `core:time/timezone` added additional search paths to match musl
* More bindings for Darwin
* Add `@builtin` to missing builtin procedure group procs
* os/os2: fix stale errors on windows when reading from console
* os/os2: better fix for the stale errors
* Fix `runtime.print_i64` using an OOB index when `min(i64)` is given.
* os/os2: use ReadFile for Console reads too, at least for now
* core:sys/linux Add timerfd syscall wrappers
* Fix `nfds_t` alias for Linux
* `core:io/utils`: fix buffer size in `write_*` procs
* `core:net` docs: recv of 0 bytes with no error is a graceful close
* `core:math/rand` small documentation fix
* Address issue identifying CDATA in XML file
* encoding/base32: Fix padding validation for malformed input
* Fix standard json parsing / unmarshalling issue for pure arrays
* Add user32 scroll bar related bindings, and FrameRect
* Add missing 'caller_location' to several procedures in 'slice' package
* Update `letter.odin`
* WebGL binding additions
* Add JSON5/SJSON Comments When Marshalling
* Fix Unicode Output When Marshalling JSON
* Allow Unmarshalling to rune
* Custom json (un)marshalling, similar to `core:fmt`'s custom formatters
* Fix `net.map_to_ip6` offset
* [vendor/sdl3] update to sdl 3.4.0

## Other

* Fix NetBSD CI by @krnowak in https://github.com/odin-lang/Odin/pull/6080

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2025-12a...dev-2026-01

---

## dev-2025-12a - 2025-12-04

**dev-2025-12a** by Kelimion - <https://github.com/odin-lang/Odin/releases/tag/dev-2025-12a>

## New Language Features

* 

## New Compiler Improvements

* Fix duplicate code emission in type assertions.

## New Packages

* 

## Package Improvements

* `core:os/os2`: Fix [#5873](https://github.com/odin-lang/Odin/issues/5873)
* Replace cURL library for Windows with one built against msvcrt
* Update cURL bindings to 8.17

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2025-12...dev-2025-12a

---

## dev-2025-12 - 2025-12-02

**dev-2025-12** by Kelimion - <https://github.com/odin-lang/Odin/releases/tag/dev-2025-12>

## Breaking changes

* BREAKING: Use `chacha8rand` as the default RNG.

The old default generator is available under `core:math/rand` in `rand_pcg.odin` in case you require a seed to return the same sequence as before.

## New Language Features

* Introduce `#all_or_none` for structs, which requires that struct literals have all or none of the fields set

## New Compiler Improvements

* Use SIP hash as name canonicalization hash
* Moved checking of `-vet-unused-procedures` and `-vet-packages` flags to after all flags are parsed
* Fixes for 32 bit with regards to typeid
* Fix [#5894](https://github.com/odin-lang/Odin/issues/5894)
* Remove `#no_copy`
* Don't check proc signature similarity for imported Objective-C methods
* Ubuntu arm ci and posix fixes
* Fix allocation of anonymous globals
* Fix [#5967](https://github.com/odin-lang/Odin/issues/5967): Incorrect stack overflow warning for by ref switches over unions
* Skip collision panic when package names aren't unique

## New Packages

* Add `vendor:curl`

## Package Improvements

* Improve docs for stable sort procedures
* Fix: `linalg.quaternion_from_forward_and_up`
* Clone unquoted strings in `encoding/json`
* Add missing `SetLayeredWindowAttributes`
* Add io uring API
* Add `FreeLibraryAndExitThread` in kernel32. Add `EnumProcessModules` in psapi
* Fix typo in `NS.String_initWithCString`
* Remove the Darwin-specific paths from `thread_unix`
* Fix `thread_act_t` size
* Fix: make `choice_bit_set` respect `bit_set` domain
* `math/rand`: Add range-based number generation procedures
* Fix `is_pointer_internally` not handling Named Types
* Faster `big.itoa`
* Add Xoshiro256 RNG
* Add `LockFileEx`/`UnlockFileEx` and related flags
* Fix `vendor:stb/image` resize `alpha_channel` parameter type to `c.int`
* Move some OS `General_Error` values to `io.Error`
* Fix out of bounds access when parsing end_pos
* Add `WSASendTo` and `WSARecvFrom`
* Update `d3d12` bindings for `D3D12_FEATURE_D3D12_TIGHT_ALIGNMENT`
* Add `NSWindow` coordinate space conversion bindings
* Don't build log allocator file on freestanding targets
* Adjust docs links for satellite SDL libraries
* Increase `base64` decoding table size to 256, preventing out of bounds reads
* `vendor/xlib`: a few more IM-related procedures and constants
* add `math.sign` and `math.sign_bit` overloads for int types
* Implement more Linux syscalls
* Add `SIO_UDP_CONNRESET` winsock constant
* `os2.File_Stream`

## Other

* Fix up macOS CI

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2025-11...dev-2025-12

---

## dev-2025-11 - 2025-11-04

**dev-2025-11** by gingerBill - <https://github.com/odin-lang/Odin/releases/tag/dev-2025-11>

## Licensing Changes

* Change Odin's LICENSE to zlib from BSD 3-clause

## New Language Features

* `intrinsics.concatenate`
  * Concatentation of constant slices, strings, and some arrays at compile time
* `intrinsics.objc_super` & `@(objc_superclass=<type>)`


## New Compiler Improvements

* Objective-C interface improvements
  * `intrinsics.objc_super` and automatically emit `objc_msgSend` calls where necessary for `@(objc_superclass)` attribute
  * Fix block symbols naming conflict across modules
* LLVM backend fixes 
  * `#simd` vector only uses bit cast when elements are not pointers
  * Fix bitcasting `context` pointer to prevent compilation errors on LLVM-14
  * Numerous constant union improvements
  * Prefer the `Type *` ver `LLVMTypeRef` when looking up `struct_field_remapping` due to lack of uniqueness
* Default parameter exclusion counting improvement for procedure groups
* Improved `-target-features` flag by allow the user to disable a target feature
  *  `-target-features:-sse,-sse2,-avx`
* `-export-linked-libs-file:<string>` flag to export the linked libraries to a file
* Fix a few compiler hangs on macOS.
* LLVM 21 support for non-Windows platforms
* Fix: `#load` alignment bug
  * set minimum alignment to 16-bytes
* Fix orca linking path
* Add `#subtype`/`using` to name canonicalization rules
* Numerous frontend bugs fixed

## New Packages

*

## Package Improvements

* More documentation improvements across the core library
* General improvements and more documentation for `core:os/os2`
* Add `inject_at_soa` and `append_nothing_soa`
* `vendor:wgpu` update to 27.0.2.0
* `core:unicode/utf8`: Add `Grapheme_Iterator`
* New `slice.sort` implementation to allow for better code generation and general API
* Deprecate the C style procedures in `strconv` (e.g. `iota`, `atoi`, etc`)
* WASM: Fix odin.js undefined `this.mem`
* Fix sRGB <-> linear RGB conversion
* `core:encoding/json` fixes
  * Fix `null` parsing in certain cases
* `core:encoding/cbor`: Fix epoch tag with small values
* `core:container/rbtree` add `find_or_insert`
* Fix bindings generator for `vendor:vulkan` for extensions and `~0` style constants
* Disable bounds checking where appropriate for Unicode and UTF-8 procedures
* `vendor:fontstash`: Fix crash with `.TTC` files
* `core:simd` : Fix incorrectly named calls in `bit_not`
* `vendor:sdl3`: Add `PointInRectFloat`
* `vendor/egl`
  * add a few more procedures and constants
  * Fix `GetPlatformDisplay` and `CreatePlatformWindowSurface` to use `int` instead of `i32`
* `vendor:box2d` 
  * fixes to bindings mismatches
  * Add `targetAngle` to `RevoluteJoint` struct/procs
* `core:odin/parser`  
  * fixes for `end_pos`
  * parse empty identifiers after selector as a selector expression with an empty field
* `core:hash`: add CCITT CRC-16
* Make packed conditional on `EPoll_Event` to match kernel
* `core:math/linalg/hlsl`: support `half` types
* `core:math/ease`: Add inverse ease procedures
* `vendor:raylib`: add `MAX_MATERIAL_MAPS` constant
* `core:sys/darwin/Foundation`: add additional AppKit bindings
* `core:text/scanner` allow for octal prefix style parsing for C-style ints

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2025-10...dev-2025-11

---

## dev-2025-10 - 2025-10-05

**dev-2025-10** by Kelimion - <https://github.com/odin-lang/Odin/releases/tag/dev-2025-10>

## New Language Features

*

## New Compiler Improvements

* Improve type inferencing of literals when calling proc groups
* Windows i386 support
* Fix Darwin `addObserver` methods and add support for new `Objc_Block`
* Fix segfault involving `string_to_string16` on Linux
* Improve OSX threading performance
* Basic support for constant union literals
* Add `-build-diagnostics`
* Prevent returning a struct containing compound literal slice
* Relax `signature_parameter_similar_enough` on struct params and fix various foreign signatures
* Preempt field checking on `signature_parameter_similar_enough` with a type ptr equality check
* Remove stray debug printf

## New Packages

* [core/image]: Add baseline JPEG support

## Package Improvements

* Use `.Image_Dimensions_Too_Large` in `core:image`
* `tick_now`: Use `f64` (was `f32`) as a return type of `odin_env.tick_now()`
* Allow missing trailing comma with proc groups in `core:odin` parser
* Fix incorrect json encoding for control characters < 32
* Initializing `big.Int` constants is now `"contextless"`
* Add `CancelIoEx` and other overlapped I/O functions.
* Add missing caller location param to append in `strings.Builder`
* Add "contextless" to small_array `get_safe` and `get_ptr_safe`
* Zero `small_array` resize
* Unify `filepath.join` return between Unix/Windows
* Fix out-of-band allocations in dynamic arenas by
* Fix for `temp_file` name prefix being deallocated before being used
* Add `runtime.conditional_mem_zero` to improve `heap_allocator` performance on non-Windows systems
* Add `digit_to_int` to `core:strconv`
* Remove inaccurate tprint comment

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2025-09...dev-2025-10

---

## dev-2025-09 - 2025-09-08

**dev-2025-09** by gingerBill - <https://github.com/odin-lang/Odin/releases/tag/dev-2025-09>

## New Language Features

* Native support for UTF-16 strings: `string16` and `cstring16`
  * Mostly for interfacing with Windows code, and other foreign code
* Define Integer Division By Zero  https://github.com/odin-lang/Odin/pull/5556

## New Compiler Improvements

* `@(init)`  and `@(fini)` must be `proc "contextless" ()`
* Implement `intrinsics.objc_block` @harold-b in https://github.com/odin-lang/Odin/pull/5547
  *  Implements the Apple block ABI.2010.3.16 natively
* Improve deference missing suggestion message
* Do not check for explicit allocators when determining proc in proc group by @janga-perlind in https://github.com/odin-lang/Odin/pull/5564
* Skip errors on polymorphic procs when in a proc group with other options 
* Fix compiler segfault when trying to use proc at type level or trying to use `()` as a type

## New Packages

*

## Package Improvements

* Fixes to `vendor:darwin/Metal`
* Numerous minor fixes to `base:runtime`
* Improvements to `base:runtime` docs
* Fixes to `vendor:wasm/WebGL` bindings
* Cleanup in `math/rand` and `runtime/random_generator`
* Add missing xlib functions for getting and setting text properties
* `vendor:OpenGL` fix misnamed parameter by 
* Make D3D12_FEATURE_DATA_D3D12_OPTIONS.MinPrecisionSupport a bitset 
* Fix buddy allocator assert 
* Check for EOF when scanning file tags
* Fix stride in `memory_equal/compare_zero` giving false positves
* Split SDL_ttf bindings to group with and without require_results
* Propogate `#caller_location` to core:container/queue procs
* Support using allocator resize in `_reserve_soa` 
* Zero existing memory when using `resize_soa`
* Add `add/remove_document_event_listener()` to `core:sys/wasm/js` 
* Fixed and added obj-c methods for `NSWindow`
* fix typo in `CLSIDFromProgIDEx` signature 
* Fix broken `wglUseFontBitmaps` binding 
* Add `LPFN_GETACCEPTEXSOCKADDRS` to ws2_32.odin
* Specify `%m` and `%M `as verbs for integer formatting in `core:fmt`
* Add `@(require_results)` attribute to procs returning an allocator 
* Handle allocator error when appending in `read_entire_file_from_file`
* `vendor:box2d` fix `CreateMotorJoint` procedure signature 
* Add build tags to `posix/spawn.odin`

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2025-08...dev-2025-09

---

## dev-2025-08 - 2025-08-05

**dev-2025-08** by gingerBill - <https://github.com/odin-lang/Odin/releases/tag/dev-2025-08>

## New Language Features
*

## New Compiler Improvements
* General compiler bug fixes
* `intrinsics.type_enum_is_contiguous`
* `intrinsics.simd_runtime_swizzle`
* Add iOS and iPhoneSimulator subtargets for `-target:darwin`
* Fix `@(objc_implement)` methods not respecting `@(objc_is_class_method)`
* `@(objc_name)`  attribute be inferrable
* Add `Did you mean?` for `card`/`len`
* `#+vet explicit-allocators`
* Saner stack linker flags for WASM
* Fix macos amd64 builds
* amd64 ABI fixes regarding certain types of SIMD vectors


## New Packages
*

## Package Improvements
* Update `core:prof/spall` to version 3
  * Adds @(no_instrumentation) to spall buffer and SCOPED operations
* `core:hash/xxhash`: Static SIMD Support for XXH3 
* Minor fixes to `core:mem/virtual` edge cases
* Unix build script for `kb_text_shape`
* Add `IUnknown` UUID for win32 related code
* `crypto/hash`: hash_bytes_to_buffer slice result to digest size
* Minor fix to `-default-to-nil-allocator`
* Disable filepath/match.odin and filepath/walk.odin compilation on js targets 
* Minor fixes to `SDL_image` save procedure that should return a boolean
* Mach Process Control
* Fix amd64 no-crt entry assembly 
* Add cgltf filter type and wrap mode enums 
* SDL2 - AudioAllowChangeFlags bit_set 
* `core:thread` - set stack size to rlimit for \*nix platforms

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2025-07...dev-2025-08

---

## dev-2025-07 - 2025-07-09

**dev-2025-07** by Kelimion - <https://github.com/odin-lang/Odin/releases/tag/dev-2025-07>

## New Language Features
* Add `intrinsics.type_is_bit_field`
* Add `@(no_sanitize_memory)` with additions to `base:sanitizer`

## New Compiler Improvements
* Correct spelling in `odin doc -help` output
* Let `-test-all-packages` work with `-build-mode:test`
* Fix package docs
* Fix `swizzle` in `for in` statement
* Fix `divti3` not being exported
* Fix scope attribute proc grouping
* Forbid multiple uses of `-sanitize`
* `-vet-style`: Be strict with type switch case column alignment
* Let compound literal array be broadcast to a struct field of arrays
* Packages with `.odin` in the name no longer attempt to parse as odin files
* Let `-no-entry-point` work for Windows DLLs
* Guard against invalid proc types in parameter list
* Push `context` onto stack before evaluating procedure parameters
* Consider custom `#align` when determining union tag size
* Ensure `volatile` status for all atomic operations
* Fix WASM C ABI for raw unions
* Fix invalid selector for acceleration structure
* Fix `check_shift`
* Forbid nested declaration of instrumentation procedures
* Fix bug where compiler treated `uint` enums as `int`s
* Fix load type panic because front-end allows a deref of a type
* Added options to show, obfuscate, trim, and hide source code locations
* Various fixes

## New Packages
* `vendor/kb_text_shape`

## Package Improvements
* Add examples/all/sdl3 for all sdl3 dependant packages
* Rewrite `Atomic_RW_Mutex`
* Add overlapped I/O bindings for Windows
* Allow `odin check examples/all` for `js_wasm` target
* Guard against negative `index` in `inject_at`
* Print timings to stderr instead of stdout
* Change `os2.user_*` on Windows to use `SHGetKnownFolderPath`
* Add `core:os/os2` user dirs helper to retrieve common paths like Downloads, Videos, et al
* Clarify `strconv.append_*` to `strconv.write_*`
* Remove old @(deprecated) things.
* DXC: Fixed broken bindings of `ICompiler` and `ICompiler2`
* Fix GMT+/- timezone handling
* Clarify `core:flags` variadic behaviors
* Move `core:math/bìg` tests over to `core:testing` instead of using Python3 as an oracle
* Add initial tests for big rationals
* Sync chan refactor
* Replace `core:posix` usage in `core:os/os2`
* compat allocator improvements
* Fix `pool_join` hangs if no threads are started
* Fix early `join` after start
* Expose `getpeername` in `core:net` package as `peer_endpoint`
* Let tests expect assertion failures and signals raised
* Get env buffer
* Allow `core:net` to be imported with `-default-to-panic-allocator`
* Update vendor:sdl3 from 3.2.10 to 3.2.16, and vendor:sdl3/image from 3.2.0 to 3.2.4
* More `Buddy_Allocator` safeguards
* Fix RegEx docs
* Added TIOCGWINSZ to darwin, linux and freebsd
* Escape object file paths properly during linker_stage
* Fix `try_send` and `send`
* Added `IS_SUPPORTED` to `core:sys/posix`
* Fix issue parsing `vendor/stb/image` with the `core:odin/parser` parser
* Fix memory leak in `core:math/big.internal_rat_norm`
* raylib: Refer to Odin-style enum over original C enum
* sys/linux: Unify `IPC_Flags` and `IPC_Mode` bit_sets
* testing: Make test state changes its own feature
* Add `slice.suffix_length`
* Various fixes

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2025-06...dev-2025-07

---

## dev-2025-06 - 2025-06-02

**dev-2025-06** by gingerBill - <https://github.com/odin-lang/Odin/releases/tag/dev-2025-06>

## New Language Features
* -

## New Compiler Improvements
* Improvements to building with Android
* Add more asan support to the odin runtime and sanitizing for various allocators
* Fix to compile-time and variable NaN comparisons
* Fix to syscalls on NetBSD ARM64
* Fix Darwin version reporting on older macOS versions
* General compiler bug fixes
* `intrinsics.type_elem_type(simd_vector)`
* Fix Global/Static Variable Alignment
* Fixes assigning null as a type if it's an alias but the base type is null
* `@(no_sanitize_address)`
* Support Objective-C class implementation
* Add debug info for labels to Odin
* `intrinsics.type_integer_to_unsigned` and `intrinsics.type_integer_to_signed`
* Use `--sysroot` instead of `-Wl,-syslibroot` on Darwin
* Fix global and static `any` usage
* Re-enable static map calls on AMD64 SysV due to ABI fixes
* Make `odin help` more precise
* `-dynamic-literals`
* Do not call disabled deferred procedures
* Add `/usr/local/lib` to FreeBSD linker path
* Add error with a suggestion when trying to extract an element from a `#simd` array, and prefer `simd.extract`
* Only trim `.odin` from build filename
* Keep shared libraries from calling main program's startup/cleanup procs on Linux
* Add `-build-only`, `-keep-test-executable`, delete test executable after running 
* Enable all sanitizers on FreeBSD
* RAD Debugger support through custom `.raddbg` section
  * Default views for slices and matrices
* Error on unterminated multi-line comment
* Fix output of object names (https://github.com/odin-lang/Odin/pull/5241)
* Add suggestions for `quaternionN` or `complexN` conversions 

## New Packages
* `base:sanitizer`
* `vendor:windows/XAudio2`
* `vendor:sdl3/ttf`
* `core:terminal`
* `core:encoding/ansi` -> `core:terminal/ansi`

## Package Improvements
* Vectorize `base:runtime.memory_*`
* `core:net` 
  * Rework errors to be cross-platform
  * Replace `default_tcp_options` with a constant
* `core:container/small_array`: Improve documentation for 
* `core:sync/chan`: Improve documentation
* `core:mem/tlsf`: refactor, add `free_all` support, add automatic new pools
* `core:fmt`: Fix printing for `bit_set[Enum]` when `min(Enum) != 0`
* `vendor/glfw` 
  * fix `SetMonitorCallback` and `MonitorProc` type definition
  * use `b32` where appropriate
* `core:text/regex`: Add iterator
* `core:math`: Fix `math.nextafter` skipping from 0 to 1
* `vendor:wgpu`: 
  * Update to 25.0.2.1
  * Fix function name for wgpu.js `genericGetAdapterInfo`
  * Correct `mipmpaFilter` field name in wgpu.js
* `core:time/timezone`: preserve nanoseconds on calls
* `vendor:box2d`:
  *  Update to 3.1.0
  * Add missing field in `box2d.BodyDef`
  * Make `build_box2d.sh` more flexible
* `core:container/priority_queue`
  * let it return `runtime.Allocator_Error`
  * Fix off-by-one error in `remove`
* `core:sys/darwin/Foundation` : Loads of additions and related stuff
* `vendor:sdl2`: correct RWwrite signature
* `vendor:sdl3`: 
  * Fix `count` output parameter of `GetFullscreenDisplayModes`
  * Add `Semaphore` API
* `core:encoding/*`, fix parsing of CDATA tags
* `core:time`: add `tick_add`
* `core:encoding/cbor`, fix slice overflow
* `core:os/os2`: general improvements
* `vendor:wasm/WebGL`: Fix incorrect parameter types
* `core:bufio`: Fix typo from `b.w-b.w` to `b.w-b.r`
* `core:simd/x86`: BMI/BMI2 intrinsics
* `base:intrinsics`: alternate `reduce_add`/`reduce_mul` intrinsics
* `core:strconv`, add support for hex-floats (`0h`)
* `vendor:raylib/rlgl` add some missing functions
* `vendor:directx/d3d12` 
  * add more FEATURE_DATA_OPTIONs 
  * Fix RESOURCE_STATE_ALL_SHADER_RESOURCE flags and add new HEAP_TYPE
* `core:encoding/json`: when unmarshalling, only match on struct tags if present
* `vendor/miniaudio`: update to 0.11.22
* `core:math/big`: fix range check in `int_atoi`
* Add comments to `builtin.odin`, documenting ODIN_* constants
* `vendor:windows/GameInput`: fixes and tweaks
* `core:encoding/csv`: Fix incorrect CSV reader settings for example
* Vectorize `strings.prefix_length`

**Full Changelog**: https://github.com/odin-lang/Odin/compare/dev-2025-04...dev-2025-06

---

## dev-2025-04 - 2025-04-03

**dev-2025-04** by gingerBill - <https://github.com/odin-lang/Odin/releases/tag/dev-2025-04>

## New Language Features

*

## New Compiler Improvements

* Support LLVM 20.1
* Fix Objective-C Selector and Class linking problems caused by a race condition
* VERY Rudimentary support for Android:
    * `-subtarget:android` for `-target:linux_arm64`
* Numerous `js_wasm32` improvements
* Add `~{memory}` clobber to syscalls intrinsics
* Improve `or_else` type inference logic
* Use Microsoft's "best practices" for using `vswhere`
* General Bug Fixes which caused compiler crashes

## New Packages

*

## Package Improvements

* Update `vendor:sdl3` to `3.2.10`
* `core:crypto`
  * General improvements
* `core:os/os2/path.odin` rewrite from scratch
  * Improved Documentation
  * Remove dependency on `core:path/filepath`

---

## dev-2025-03 - 2025-03-05

**dev-2025-03** by gingerBill - <https://github.com/odin-lang/Odin/releases/tag/dev-2025-03>

## New Language Features

-

## New Compiler Improvements

* Name Canonicalization
  * Deterministic Name Mangling Rules for Symbols (Procedures, Variables, Debug Types, etc)
* `typeid` layout change
  * Always 8-bytes in size
  * Represents a hash of the canonical name for the type
* Improved generation times for `odin doc`
* Allow `-show-timings` for `odin doc`
* Very minor parser improvements to catch weird edges cases
* `intrinsics.simd_extract_msbs`
* `intrinsics.simd_extract_lsbs`
* `for x in bit_set` will use a count leading zeros intrinsics internally rather than checking each bit manually
* General bug fixes for LLVM backend


## New Packages

* `vendor:sdl3/image`

## Package Improvements

* Update `vendor:wgpu` to `v24`
* Improved documentation for `core:simd`
* Minor fixes to SDL3 bindings
* Support use of `*` in format strings without an index
* `NS.SavePanel_URL` fix 
* Support `%b` for `rune`
* `os2` fixes
  * Recursive directory walker
  * Fix race conditions on Linux
  * `os2.random_string` to use `context.random_generator`

---

## dev-2025-02 - 2025-02-11

**dev-2025-02** by gingerBill - <https://github.com/odin-lang/Odin/releases/tag/dev-2025-02>

## New Language Features

* Support `#unroll(N) for` with arrays

## Compiler Improvements

* Enable `-use-separate-module` as default for all platforms (except wasm based ones)
* General Bug Fixes
* Remove erroneous warnings regarding stack overflow in range loops "by reference"
* Allow broadcasting of untyped values to `#simd` arrays
* Improvements to `-obfuscate-source-code-locations`
* Remove duplicates of .framework/.dynlib/.so in linker
* Darwin: Sort frameworks to link first


## New Packages

* `vendor:sdl3` (3.2.2)
* `vendor:windows/GameInput`

## Package Improvements

* Improvements to D3D12 package
* Improvements for Haiku
* Add missing procedures to GLFW
* `runtime.map_entry`
* XInput bindings for `core:sys/windows`
* More work on `core:os/os2` development
* More Objective-C bindings
* Additional bindings and constants for `core:sys/windows`
* `mem.Tracking_Allocator` defaults to panicking on bad frees

---

