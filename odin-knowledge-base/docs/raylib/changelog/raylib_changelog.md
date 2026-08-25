---
source: github-releases
repo: raysan5/raylib
tag: consolidated
date: 2026-08-25
type: changelog
status: active
version: 1.0.0
lastUpdated: "2026-08-25T10:35:56Z"
updatedBy: "MiniMax-M3 (Kilo Code)"
tags: [OdinRAG, kb, source/raylib, changelog, raylib]
---
# Raylib Changelog (consolidated, 10 releases)

> Generated from the [raysan5/raylib releases](https://github.com/raysan5/raylib/releases) feed on 2026-08-25.
> Re-run `python _Helpers/scripts/scrapers/scrape_raylib_changelog.py` to refresh.

## 6.0 - 2026-04-23

**raylib v6.0** by raysan5 - <https://github.com/raysan5/raylib/releases/tag/6.0>

<img width="960" height="421" alt="raylib60_banner" src="https://github.com/user-attachments/assets/f651ef5d-a5a7-470e-b16b-6065f7f65c30" />

# raylib 6.0 release notes

A new `raylib` release is finally ready and, again, this is the **biggest `raylib` release ever**! Thanks to the support of many amazing contributors this release comes packed with many new features and improvements, also thanks to the financial support of [NLnet](https://nlnet.nl/) and the [NGI Zero Commond Fund](https://nlnet.nl/NGI0/) that allowed me to work on this project mostly fulltime for the past few months.

Some astonishing numbers for this release:

 - **+330** closed issues (for a TOTAL of **+2150**!)
 - **+2000** commits since previous RELEASE (for a TOTAL of **+9760**!)
 - **+20** new functions ADDED to raylib API (for a TOTAL of **600**!)
 - **+70** new examples to learn from (for a TOTAL of **+215**!)
 - **+210** new contributors (for a TOTAL of **+850**!)

Highlights for `raylib 6.0`:

 - **`NEW` Software Renderer - [`rlsw`](https://github.com/raysan5/raylib/blob/master/src/external/rlsw.h)**: The biggest addition of this new release. A new software renderer backend, that allows raylib to run purely on CPU, with no neeed for a GPU. It finally closes the circle of my search for a portable self-contained, with **no-external-dependencies**, graphics library, able to run on any device providing some CPU-power and some RAM memory. It has been possible thanks to the amazing work of **Le Juez Victor** ([@Bigfoot71](https://github.com/Bigfoot71)), who created [`rlsw`](https://github.com/raysan5/raylib/blob/master/src/external/rlsw.h), a single-file header-only library implementing OpenGL 1.1+ specification, tailored to fit into raylib [`rlgl`](https://github.com/raysan5/raylib/blob/master/src/rlgl.h) OpenGL wrapper, and allowing to run raylib seamlessly over CPU with **no code changes required on user side**. As expected, software rendering is slower than hardware-accelerated rendering but it is still fast enough to run basic application at 30-60 fps. Actually, it already proved it usefulness on a new [raylib port for ESP32](https://components.espressif.com/components/georgik/raylib/versions/6.0.0/readme) microcontroller by Espressif, useful for industrial applications, and opens the door to the upcoming RISC-V powered devices that start arriving to the marked, and many times come with no GPU. Along the new software renderer, some of the existing platform backends have been adapted to support it (SDL, RGFW, DRM) and also **new platforms backends have been created** to accomodate it (Win32, Emscripten), incluing a new `PLATFORM_MEMORY`, that allows direct rendering to a memory framebuffer.

<div align="center">
  <video src="https://gist.github.com/user-attachments/assets/ead0b2b0-33e3-45ec-a650-770def71fbde" />
</div>

 - **`NEW` Platform backend: Memory - [`rcore_memory`](https://github.com/raysan5/raylib/blob/master/src/platforms/rcore_memory.c)**: This new platform has been added along the **software renderer** backend, allowing 2d and 3d rendering over a **platform-agnostic memory framebuffer**, it can run headless and output frames can be directly exported to images. This new backend could also be useful for graphics rendering on servers or process images directly using the memory buffer.

 - **`NEW` Platform backend: Win32 - [`rcore_desktop_win32`](https://github.com/raysan5/raylib/blob/master/src/platforms/rcore_desktop_win32.c)**: A new **Windows platform backend** and the first step towards a potential replacement/alternative to the platform libraries currently used by raylib (GLFW/SDL/RGFW). This backend follows same API template structure than the other raylib backends, but directly implementing Win32 API calls. It allows initializing OpenGL GPU-accelerated windows and also GDI based windows, useful for the software renderer backend. This new backend approach, following a common template-structure and separating the platform logic by specific OS/Windowing system, will simplify code, improve maintenance, readability and portability for raylib, setting some bases for the future. *NOTE: This backend is new and it could require further testing, use it as an experimental backend for now.*

 - **`NEW` Platform backend: Emscripten - [`rcore_web_emscripten`](https://github.com/raysan5/raylib/blob/master/src/platforms/rcore_web_emscripten.c)**: In the same line as Win32 backend, this new web backend moves away from `libglfw.js` and **directly implements Emscripten/JS functionality**, with **no other dependencies**, adding support for the new software renderer to draw directly on a **non-accelerated 2d canvas** but also supporting a WebGL-hardware-accelerated canvas when required. *NOTE: This backend is new and it could require further testing, use it as an experimental backend for now.*

<img width="1270" height="940" alt="raylib_platforms_supported_600" src="https://github.com/user-attachments/assets/a406acfb-d823-47a1-8c1e-58ca0b792b0e" />

 - **`REDESIGNED` Fullscreen modes and High-DPI content scaling**: After many years and many related issues, the full-screen and high-dpi content scaling support has been **completely redesigned** from scratch. New design prioritizes **borderless fullscreen modes** and automatically detects current monitor content scaling configuration to scale window and framebuffer accordingly when required. Still, High-DPI support must be requested by user if desired enabling `FLAG_WINDOW_HIGHDPI` on window creation. This new system has been carefully tested on Windows, Linux (X11, Wayland), macOS with multiple monitors and multiple resolutions, including 4K monitors.

 - **`REDESIGNED` Skeletal Animation System**: A new animation system for 3d models has been created to support animation blending, between single frames but also between differents frames on different animations, to allow easy **timed transitions** between animations. This redesign implied reviewing several raylib structures to better accomodate animation data: `Model`, `ModelSkeleton`, `ModelAnimation`, but the API was simplified and support for GPU-skinning was improved with multiple optimizations.

<div align="center">
  <video src="https://gist.github.com/user-attachments/assets/293030f3-9e73-4f50-8a5b-d7f4aea2e8ba" />
</div>

 - **`REDESIGNED` Build Config System - [`config.h`](https://github.com/raysan5/raylib/blob/master/src/config.h)**: raylib allows lot of customization for specific needs (i.e. disabling modules not needed for specific applications like rmodels or raudio) but previous implementation did not allow easely disabling some features from **custom build systems**. New design not only allows disabling features with simple `-DSUPPORT_FILEFORMAT_OBJ=0` on building command-line but also the full system has been reviewed, removing useless flags and exposing new ones.

 - **`NEW` File System API**: Along the years, multiple filesystem functions have been added to raylib API as required but it felt somewhat inconsistent with some pieces missing. In this new release, the full filesystem API has beeen reviewed and reorganized, compiling all the functionality single module: [rcore](https://github.com/raysan5/raylib/blob/master/src/raylib.h#L1126), consequently `utils` module has been removed and build system has been simplified even more; **only 6-7 modules (.c) need to be compiled containing the full raylib library**. This new filesystem API will allow raylib to be used on the creation of **custom build systems**, as already demostrated with the new `rexm` tool for examples management. At the moment raylib includes **+40 file system management functions**:
```c
// File system management functions
unsigned char *LoadFileData(const char *fileName, int *dataSize); // Load file data as byte array (read)
void UnloadFileData(unsigned char *data);                     // Unload file data allocated by LoadFileData()
bool SaveFileData(const char *fileName, void *data, int dataSize); // Save data to file from byte array (write), returns true on success
bool ExportDataAsCode(const unsigned char *data, int dataSize, const char *fileName); // Export data to code (.h), returns true on success
char *LoadFileText(const char *fileName);                     // Load text data from file (read), returns a '\0' terminated string
void UnloadFileText(char *text);                              // Unload file text data allocated by LoadFileText()
bool SaveFileText(const char *fileName, const char *text);    // Save text data to file (write), string must be '\0' terminated, returns true on success

int FileRename(const char *fileName, const char *fileRename); // Rename file (if exists)
int FileRemove(const char *fileName);                         // Remove file (if exists)
int FileCopy(const char *srcPath, const char *dstPath);       // Copy file from one path to another, dstPath created if it doesn't exist
int FileMove(const char *srcPath, const char *dstPath);       // Move file from one directory to another, dstPath created if it doesn't exist
int FileTextReplace(const char *fileName, const char *search, const char *replacement); // Replace text in an existing file
int FileTextFindIndex(const char *fileName, const char *search); // Find text in existing file
bool FileExists(const char *fileName);                        // Check if file exists
bool DirectoryExists(const char *dirPath);                    // Check if a directory path exists
bool IsFileExtension(const char *fileName, const char *ext);  // Check file extension (recommended include point: .png, .wav)
int GetFileLength(const char *fileName);                      // Get file length in bytes (NOTE: GetFileSize() conflicts with windows.h)
long GetFileModTime(const char *fileName);                    // Get file modification time (last write time)
const char *GetFileExtension(const char *fileName);           // Get pointer to extension for a filename string (includes dot: '.png')
const char *GetFileName(const char *filePath);                // Get pointer to filename for a path string
const char *GetFileNameWithoutExt(const char *filePath);      // Get filename string without extension (uses static string)
const char *GetDirectoryPath(const char *filePath);           // Get full path for a given fileName with path (uses static string)
const char *GetPrevDirectoryPath(const char *dirPath);        // Get previous directory path for a given path (uses static string)
const char *GetWorkingDirectory(void);                        // Get current working directory (uses static string)
const char *GetApplicationDirectory(void);                    // Get the directory of the running application (uses static string)
int MakeDirectory(const char *dirPath);                       // Create directories (including full path requested), returns 0 on success
bool ChangeDirectory(const char *dirPath);                    // Change working directory, return true on success
bool IsPathFile(const char *path);                            // Check if a given path is a file or a directory
bool IsFileNameValid(const char *fileName);                   // Check if fileName is valid for the platform/OS
FilePathList LoadDirectoryFiles(const char *dirPath);         // Load directory filepaths, files and directories, no subdirs scan
FilePathList LoadDirectoryFilesEx(const char *basePath, const char *filter, bool scanSubdirs); // Load directory filepaths with extension filtering and subdir scan; some filters available: "*.*", "FILES*", "DIRS*"
void UnloadDirectoryFiles(FilePathList files);                // Unload filepaths
bool IsFileDropped(void);                                     // Check if a file has been dropped into window
FilePathList LoadDroppedFiles(void);                          // Load dropped filepaths
void UnloadDroppedFiles(FilePathList files);                  // Unload dropped filepaths
unsigned int GetDirectoryFileCount(const char *dirPath);      // Get the file count in a directory
unsigned int GetDirectoryFileCountEx(const char *basePath, const char *filter, bool scanSubdirs); // Get the file count in a directory with extension filtering and recursive directory scan. Use 'DIR' in the filter string to include directories in the result
```

 - **`NEW` Text Management API**: Along with the new file system functionality, a new set of text management functions has been added, also very useful for text procesing and also used in **custom build systems creation using raylib**. At the moment raylib includes **+30 text management functions**:
```c
// Text strings management functions (no UTF-8 strings, only byte chars)
// WARNING: Most of these functions use a internal static buffer[], it's recommended to store returned data on user-side for re-use
char **LoadTextLines(const char *text, int *count);           // Load text as separate lines ('\n')
void UnloadTextLines(char **text, int lineCount);             // Unload text lines
int TextCopy(char *dst, const char *src);                     // Copy one string to another, returns bytes copied
bool TextIsEqual(const char *text1, const char *text2);       // Check if two text string are equal
unsigned int TextLength(const char *text);                    // Get text length, checks for '\0' ending
const char *TextFormat(const char *text, ...);                // Text formatting with variables (sprintf() style)
const char *TextSubtext(const char *text, int position, int length); // Get a piece of a text string
const char *TextRemoveSpaces(const char *text);               // Remove text spaces, concat words
char *GetTextBetween(const char *text, const char *begin, const char *end); // Get text between two strings
char *TextReplace(const char *text, const char *search, const char *replacement); // Replace text string with new string
char *TextReplaceAlloc(const char *text, const char *search, const char *replacement); // Replace text string with new string, memory must be MemFree()
char *TextReplaceBetween(const char *text, const char *begin, const char *end, const char *replacement); // Replace text between two specific strings
char *TextReplaceBetweenAlloc(const char *text, const char *begin, const char *end, const char *replacement); // Replace text between two specific strings, memory must be MemFree()
char *TextInsert(const char *text, const char *insert, int position); // Insert text in a defined byte position
char *TextInsertAlloc(const char *text, const char *insert, int position); // Insert text in a defined byte position, memory must be MemFree()
char *TextJoin(char **textList, int count, const char *delimiter); // Join text strings with delimiter
char **TextSplit(const char *text, char delimiter, int *count); // Split text into multiple strings, using MAX_TEXTSPLIT_COUNT static strings
void TextAppend(char *text, const char *append, int *position); // Append text at specific position and move cursor
int TextFindIndex(const char *text, const char *search);      // Find first text occurrence within a string, -1 if not found
char *TextToUpper(const char *text);                          // Get upper case version of provided string
char *TextToLower(const char *text);                          // Get lower case version of provided string
char *TextToPascal(const char *text);                         // Get Pascal case notation version of provided string
char *TextToSnake(const char *text);                          // Get Snake case notation version of provided string
char *TextToCamel(const char *text);                          // Get Camel case notation version of provided string
int TextToInteger(const char *text);                          // Get integer value from text
float TextToFloat(const char *text);                          // Get float value from text
```

 - **`NEW` tool: raylib examples manager - [rexm](https://github.com/raysan5/raylib/tree/master/tools/rexm)**: raylib examples collection is huge, with **more than 200 examples** it was quite difficult to manage: adding, removing, renaming examples was a very costly process involving many files to be modified (including build systems), also the examples did not follow a common header convention neither a structure conventions. For that reason, a new support tool has been created: **rexm**, a raylib examples manager that allows to easely add/remove/rename examples, automatically fix inconsistencies and even **building and automated testing** on multiple platforms.
```
USAGE:
    > rexm <command> <example_name> [<example_rename>]

COMMANDS:
    create <new_example_name>     : Creates an empty example, from internal template
    add <example_name>            : Add existing example to collection
    rename <old_examples_name> <new_example_name> : Rename an existing example
    remove <example_name>         : Remove an existing example from collection
    build <example_name>          : Build example for Desktop and Web platforms
    test <example_name>           : Build and Test example for Desktop and Web platforms
    validate                      : Validate examples collection, generates report
    update                        : Validate and update examples collection, generates report
```

 - **`NEW` +70 new examples**: Thanks to `rexm` and the simplification on examples management, this new raylib release includes +70 new examples to learn from, most of them contributed by community. Multiple examples have also been renamed for consistency and all examples header and structure have been reviewed and unified.

<img width="1320" height="540" alt="new_raylib_examples" src="https://github.com/user-attachments/assets/c9805cf5-a455-4981-a9e7-355e8925e424" />

Make sure to check raylib [CHANGELOG](https://github.com/raysan5/raylib/blob/master/CHANGELOG) for a detailed list of changes!

I want to **thank all the contributors (+850!**) that along the years have **greatly improved raylib** and pushed it further and better day after day. And **many thanks to raylib community and all raylib users** for supporting the library along those many years.

Finally, I want to thank [puffer.ai](https://puffer.ai/) and [comma.ai](https://comma.ai/) for **usign raylib and supporting the project** as platinum sponsors, along many others individuals that have been sponsoring raylib along the years. Thanks to all of you for allowing me to keep working on this library!

**After +12 years of development, `raylib 6.0` is today one of the bests libraries to enjoy games/tools/graphic programming!**

**Enjoy graphics programming with raylib!** :)

## New Contributors
* @kovidomi made their first contribution in https://github.com/raysan5/raylib/pull/4510
* @villares made their first contribution in https://github.com/raysan5/raylib/pull/4512
* @hippietrail made their first contribution in https://github.com/raysan5/raylib/pull/4515
* @Booklordofthedings made their first contribution in https://github.com/raysan5/raylib/pull/4514
* @mikeemm made their first contribution in https://github.com/raysan5/raylib/pull/4496
* @interkosmos made their first contribution in https://github.com/raysan5/raylib/pull/4518
* @uwiwiow made their first contribution in https://github.com/raysan5/raylib/pull/4520
* @HaxSam made their first contribution in https://github.com/raysan5/raylib/pull/4531
* @mobius3 made their first contribution in https://github.com/raysan5/raylib/pull/4541
* @PieVieRo made their first contribution in https://github.com/raysan5/raylib/pull/4545
* @Mossieur-Patate made their first contribution in https://github.com/raysan5/raylib/pull/4544
* @RealDoigt made their first contribution in https://github.com/raysan5/raylib/pull/4550
* @CalebHeydon made their first contribution in https://github.com/raysan5/raylib/pull/4539
* @mrjonjonjon made their first contribution in https://github.com/raysan5/raylib/pull/4556
* @mrryanjohnston made their first contribution in https://github.com/raysan5/raylib/pull/4559
* @ahmedqarmout2 made their first contribution in https://github.com/raysan5/raylib/pull/4565
* @legendaryredfox made their first contribution in https://github.com/raysan5/raylib/pull/4567
* @0riginaln0 made their first contribution in https://github.com/raysan5/raylib/pull/4585
* @meadiode made their first contribution in https://github.com/raysan5/raylib/pull/4579
* @hexmaster111 made their first contribution in https://github.com/raysan5/raylib/pull/4596
* @saxofon made their first contribution in https://github.com/raysan5/raylib/pull/4603
* @Kirandeep-Singh-Khehra made their first contribution in https://github.com/raysan5/raylib/pull/4602
* @Fancy2209 made their first contribution in https://github.com/raysan5/raylib/pull/4621
* @james2doyle made their first contribution in https://github.com/raysan5/raylib/pull/4633
* @BotRandomness made their first contribution in https://github.com/raysan5/raylib/pull/4639
* @marionauta made their first contribution in https://github.com/raysan5/raylib/pull/4640
* @Joonsey made their first contribution in https://github.com/raysan5/raylib/pull/4620
* @peter15914 made their first contribution in https://github.com/raysan5/raylib/pull/4649
* @rexept made their first contribution in https://github.com/raysan5/raylib/pull/4656
* @maiconpintoabreu made their first contribution in https://github.com/raysan5/raylib/pull/4661
* @pope made their first contribution in https://github.com/raysan5/raylib/pull/4667
* @Hakunamawatta made their first contribution in https://github.com/raysan5/raylib/pull/4674
* @mobiuscog made their first contribution in https://github.com/raysan5/raylib/pull/4675
* @teatwig made their first contribution in https://github.com/raysan5/raylib/pull/4683
* @anstropleuton made their first contribution in https://github.com/raysan5/raylib/pull/4699
* @pejorativefox made their first contribution in https://github.com/raysan5/raylib/pull/4703
* @sleeptightAnsiC made their first contribution in https://github.com/raysan5/raylib/pull/4707
* @elite0OG made their first contribution in https://github.com/raysan5/raylib/pull/4727
* @whaleymar made their first contribution in https://github.com/raysan5/raylib/pull/4742
* @henrikglass made their first contribution in https://github.com/raysan5/raylib/pull/4745
* @goto40 made their first contribution in https://github.com/raysan5/raylib/pull/4753
* @mannikim made their first contribution in https://github.com/raysan5/raylib/pull/4764
* @vict-Yang made their first contribution in https://github.com/raysan5/raylib/pull/4772
* @deckarep made their first contribution in https://github.com/raysan5/raylib/pull/4779
* @loftafi made their first contribution in https://github.com/raysan5/raylib/pull/4787
* @slendidev made their first contribution in https://github.com/raysan5/raylib/pull/4792
* @Destructor17 made their first contribution in https://github.com/raysan5/raylib/pull/4364
* @jordan4ibanez made their first contribution in https://github.com/raysan5/raylib/pull/4793
* @AshishBhattarai made their first contribution in https://github.com/raysan5/raylib/pull/4811
* @Kaluub made their first contribution in https://github.com/raysan5/raylib/pull/4812
* @zewenn made their first contribution in https://github.com/raysan5/raylib/pull/4819
* @10aded made their first contribution in https://github.com/raysan5/raylib/pull/4827
* @david-vanderson made their first contribution in https://github.com/raysan5/raylib/pull/4826
* @AmityWilder made their first contribution in https://github.com/raysan5/raylib/pull/4829
* @NiamhNightglow made their first contribution in https://github.com/raysan5/raylib/pull/4835
* @MykBamberg made their first contribution in https://github.com/raysan5/raylib/pull/4833
* @aidonmaster made their first contribution in https://github.com/raysan5/raylib/pull/4839
* @theundergroundsorcerer made their first contribution in https://github.com/raysan5/raylib/pull/4843
* @bamless made their first contribution in https://github.com/raysan5/raylib/pull/4845
* @marler8997 made their first contribution in https://github.com/raysan5/raylib/pull/4856
* @lumenkeyes made their first contribution in https://github.com/raysan5/raylib/pull/4870
* @AndrewHamel111 made their first contribution in https://github.com/raysan5/raylib/pull/4895
* @mUnicorn made their first contribution in https://github.com/raysan5/raylib/pull/4896
* @ZeanKey made their first contribution in https://github.com/raysan5/raylib/pull/4907
* @gfaster made their first contribution in https://github.com/raysan5/raylib/pull/4909
* @rael346 made their first contribution in https://github.com/raysan5/raylib/pull/4913
* @Servall4 made their first contribution in https://github.com/raysan5/raylib/pull/4914
* @daniel-abbott made their first contribution in https://github.com/raysan5/raylib/pull/4916
* @Pivok7 made their first contribution in https://github.com/raysan5/raylib/pull/4944
* @parzivail made their first contribution in https://github.com/raysan5/raylib/pull/4948
* @padmadevd made their first contribution in https://github.com/raysan5/raylib/pull/4947
* @meowstr made their first contribution in https://github.com/raysan5/raylib/pull/4963
* @garrisonhh made their first contribution in https://github.com/raysan5/raylib/pull/4981
* @williewillus made their first contribution in https://github.com/raysan5/raylib/pull/4980
* @LainLayer made their first contribution in https://github.com/raysan5/raylib/pull/4982
* @hmz-rhl made their first contribution in https://github.com/raysan5/raylib/pull/4985
* @Marcos-cat made their first contribution in https://github.com/raysan5/raylib/pull/4993
* @ElDigoXD made their first contribution in https://github.com/raysan5/raylib/pull/5006
* @Sir-Irk made their first contribution in https://github.com/raysan5/raylib/pull/5016
* @fosskers made their first contribution in https://github.com/raysan5/raylib/pull/5014
* @wwderw made their first contribution in https://github.com/raysan5/raylib/pull/5033
* @jonathandw743 made their first contribution in https://github.com/raysan5/raylib/pull/5026
* @zedeckj made their first contribution in https://github.com/raysan5/raylib/pull/5025
* @Emil2010 made their first contribution in https://github.com/raysan5/raylib/pull/5020
* @vinnyhorgan made their first contribution in https://github.com/raysan5/raylib/pull/5043
* @RomainPlmg made their first contribution in https://github.com/raysan5/raylib/pull/5047
* @PanicTitan made their first contribution in https://github.com/raysan5/raylib/pull/5041
* @katanya04 made their first contribution in https://github.com/raysan5/raylib/pull/5050
* @didas72 made their first contribution in https://github.com/raysan5/raylib/pull/5053
* @Joecheong2006 made their first contribution in https://github.com/raysan5/raylib/pull/5057
* @kariem2k made their first contribution in https://github.com/raysan5/raylib/pull/5063
* @rob-bits made their first contribution in https://github.com/raysan5/raylib/pull/4988
* @lepasona made their first contribution in https://github.com/raysan5/raylib/pull/5068
* @Moros1138 made their first contribution in https://github.com/raysan5/raylib/pull/4956
* @Luca-coder07 made their first contribution in https://github.com/raysan5/raylib/pull/5073
* @lpow100 made their first contribution in https://github.com/raysan5/raylib/pull/5077
* @killerdevildog made their first contribution in https://github.com/raysan5/raylib/pull/5075
* @Auios made their first contribution in https://github.com/raysan5/raylib/pull/5090
* @wileyanderssen made their first contribution in https://github.com/raysan5/raylib/pull/5096
* @JohnnyCena123 made their first contribution in https://github.com/raysan5/raylib/pull/5099
* @matthijskooijman made their first contribution in https://github.com/raysan5/raylib/pull/5104
* @lassade made their first contribution in https://github.com/raysan5/raylib/pull/5108
* @Andersama made their first contribution in https://github.com/raysan5/raylib/pull/4837
* @jan-beukes made their first contribution in https://github.com/raysan5/raylib/pull/5119
* @rossberg made their first contribution in https://github.com/raysan5/raylib/pull/5133
* @alexander-nichols made their first contribution in https://github.com/raysan5/raylib/pull/5136
* @CashWasabi made their first contribution in https://github.com/raysan5/raylib/pull/5128
* @feive7 made their first contribution in https://github.com/raysan5/raylib/pull/5137
* @Siltnamis made their first contribution in https://github.com/raysan5/raylib/pull/5139
* @annaymone made their first contribution in https://github.com/raysan5/raylib/pull/5143
* @theavege made their first contribution in https://github.com/raysan5/raylib/pull/5150
* @maiphi made their first contribution in https://github.com/raysan5/raylib/pull/5158
* @0stamina made their first contribution in https://github.com/raysan5/raylib/pull/5164
* @vegerot made their first contribution in https://github.com/raysan5/raylib/pull/5186
* @ArmanOmmid made their first contribution in https://github.com/raysan5/raylib/pull/5201
* @keks137 made their first contribution in https://github.com/raysan5/raylib/pull/5204
* @dog6 made their first contribution in https://github.com/raysan5/raylib/pull/5205
* @meisei4 made their first contribution in https://github.com/raysan5/raylib/pull/5207
* @timlittle made their first contribution in https://github.com/raysan5/raylib/pull/5212
* @zerohorsepower made their first contribution in https://github.com/raysan5/raylib/pull/5218
* @Jopestpe made their first contribution in https://github.com/raysan5/raylib/pull/5217
* @RobinsAviary made their first contribution in https://github.com/raysan5/raylib/pull/5216
* @Teeto44 made their first contribution in https://github.com/raysan5/raylib/pull/5224
* @pyrokn8 made their first contribution in https://github.com/raysan5/raylib/pull/5234
* @hugoarnal made their first contribution in https://github.com/raysan5/raylib/pull/5233
* @Arrangemonk made their first contribution in https://github.com/raysan5/raylib/pull/5244
* @sakgoyal made their first contribution in https://github.com/raysan5/raylib/pull/5252
* @Bala050814 made their first contribution in https://github.com/raysan5/raylib/pull/5246
* @themushroompirates made their first contribution in https://github.com/raysan5/raylib/pull/5254
* @JordSant made their first contribution in https://github.com/raysan5/raylib/pull/5260
* @aixiansheng made their first contribution in https://github.com/raysan5/raylib/pull/5276
* @MULTidll made their first contribution in https://github.com/raysan5/raylib/pull/5279
* @NimComPoo-04 made their first contribution in https://github.com/raysan5/raylib/pull/5278
* @diogohartuiqdebarba made their first contribution in https://github.com/raysan5/raylib/pull/5295
* @alexgb0 made their first contribution in https://github.com/raysan5/raylib/pull/5291
* @krispy-snacc made their first contribution in https://github.com/raysan5/raylib/pull/5236
* @adeebshihadeh made their first contribution in https://github.com/raysan5/raylib/pull/5308
* @cthulhuology made their first contribution in https://github.com/raysan5/raylib/pull/5319
* @tacf made their first contribution in https://github.com/raysan5/raylib/pull/5323
* @EDBCREPO made their first contribution in https://github.com/raysan5/raylib/pull/5324
* @komunre made their first contribution in https://github.com/raysan5/raylib/pull/5325
* @NoNameAuthenticated made their first contribution in https://github.com/raysan5/raylib/pull/5332
* @Chakri-fun made their first contribution in https://github.com/raysan5/raylib/pull/5339
* @und3f made their first contribution in https://github.com/raysan5/raylib/pull/5358
* @ChocolateChipKookie made their first contribution in https://github.com/raysan5/raylib/pull/5363
* @MaeBrooks made their first contribution in https://github.com/raysan5/raylib/pull/5366
* @acquitelol made their first contribution in https://github.com/raysan5/raylib/pull/5370
* @johnmichaeljimenez made their first contribution in https://github.com/raysan5/raylib/pull/5373
* @davidbuzatto made their first contribution in https://github.com/raysan5/raylib/pull/5372
* @XenoMustache made their first contribution in https://github.com/raysan5/raylib/pull/5383
* @rayumie made their first contribution in https://github.com/raysan5/raylib/pull/5384
* @Sethbones made their first contribution in https://github.com/raysan5/raylib/pull/5386
* @spineda2019 made their first contribution in https://github.com/raysan5/raylib/pull/5390
* @gmitch215 made their first contribution in https://github.com/raysan5/raylib/pull/5397
* @Marcos-D made their first contribution in https://github.com/raysan5/raylib/pull/5392
* @olaron made their first contribution in https://github.com/raysan5/raylib/pull/5410
* @dtasada made their first contribution in https://github.com/raysan5/raylib/pull/5415
* @caszuu made their first contribution in https://github.com/raysan5/raylib/pull/5414
* @SabeDoesThings made their first contribution in https://github.com/raysan5/raylib/pull/5421
* @msmith-codes made their first contribution in https://github.com/raysan5/raylib/pull/5422
* @KiviTK made their first contribution in https://github.com/raysan5/raylib/pull/5430
* @Crisspl made their first contribution in https://github.com/raysan5/raylib/pull/5431
* @kellemar made their first contribution in https://github.com/raysan5/raylib/pull/5439
* @LeapersEdge made their first contribution in https://github.com/raysan5/raylib/pull/5444
* @TheLazyIndianTechie made their first contribution in https://github.com/raysan5/raylib/pull/5445
* @CosmosShell made their first contribution in https://github.com/raysan5/raylib/pull/5457
* @mcdubhghlas made their first contribution in https://github.com/raysan5/raylib/pull/5427
* @oneafter made their first contribution in https://github.com/raysan5/raylib/pull/5450
* @JJLDonley made their first contribution in https://github.com/raysan5/raylib/pull/5462
* @jackboakes made their first contribution in https://github.com/raysan5/raylib/pull/5468
* @al13n321 made their first contribution in https://github.com/raysan5/raylib/pull/5469
* @ssszcmawo made their first contribution in https://github.com/raysan5/raylib/pull/5470
* @pauldahacker made their first contribution in https://github.com/raysan5/raylib/pull/5478
* @MarcosTypeAP made their first contribution in https://github.com/raysan5/raylib/pull/5481
* @Meehai made their first contribution in https://github.com/raysan5/raylib/pull/5482
* @lucas150670 made their first contribution in https://github.com/raysan5/raylib/pull/5484
* @jamesmintram made their first contribution in https://github.com/raysan5/raylib/pull/5486
* @mdm5995 made their first contribution in https://github.com/raysan5/raylib/pull/5487
* @iisakkirotko made their first contribution in https://github.com/raysan5/raylib/pull/5490
* @mck1117 made their first contribution in https://github.com/raysan5/raylib/pull/5494
* @jscaff made their first contribution in https://github.com/raysan5/raylib/pull/5498
* @noinodev made their first contribution in https://github.com/raysan5/raylib/pull/5505
* @vdemcak made their first contribution in https://github.com/raysan5/raylib/pull/5506
* @The4codeblocks made their first contribution in https://github.com/raysan5/raylib/pull/5508
* @jasoncnm made their first contribution in https://github.com/raysan5/raylib/pull/5516
* @eloj made their first contribution in https://github.com/raysan5/raylib/pull/5523
* @alexf91 made their first contribution in https://github.com/raysan5/raylib/pull/5529
* @bielern made their first contribution in https://github.com/raysan5/raylib/pull/5531
* @Sumethh made their first contribution in https://github.com/raysan5/raylib/pull/5534
* @LunaStev made their first contribution in https://github.com/raysan5/raylib/pull/5539
* @n-s-kiselev made their first contribution in https://github.com/raysan5/raylib/pull/5540
* @arlez80 made their first contribution in https://github.com/raysan5/raylib/pull/5548
* @0xPD33 made their first contribution in https://github.com/raysan5/raylib/pull/5564
* @dmitrii-brand made their first contribution in https://github.com/raysan5/raylib/pull/5543
* @TheKodeToad made their first contribution in https://github.com/raysan5/raylib/pull/5574
* @FinnDemonCat made their first contribution in https://github.com/raysan5/raylib/pull/5585
* @BadRAM made their first contribution in https://github.com/raysan5/raylib/pull/5587
* @aceiii made their first contribution in https://github.com/raysan5/raylib/pull/5590
* @ghera made their first contribution in https://github.com/raysan5/raylib/pull/5589
* @konakona418 made their first contribution in https://github.com/raysan5/raylib/pull/5602
* @lamweilun made their first contribution in https://github.com/raysan5/raylib/pull/5613
* @m039 made their first contribution in https://github.com/raysan5/raylib/pull/5617
* @dodome2k6 made their first contribution in https://github.com/raysan5/raylib/pull/5620
* @ggrizzly made their first contribution in https://github.com/raysan5/raylib/pull/5615
* @JoeStrout made their first contribution in https://github.com/raysan5/raylib/pull/5626
* @victorberdugo1 made their first contribution in https://github.com/raysan5/raylib/pull/5629
* @SardineMilk made their first contribution in https://github.com/raysan5/raylib/pull/5635
* @dan-hoang made their first contribution in https://github.com/raysan5/raylib/pull/5637
* @jtorrestx made their first contribution in https://github.com/raysan5/raylib/pull/5647
* @Wertual08 made their first contribution in https://github.com/raysan5/raylib/pull/5645
* @somamizobuchi made their first contribution in https://github.com/raysan5/raylib/pull/5653
* @0x00650a made their first contribution in https://github.com/raysan5/raylib/pull/5671
* @devel60-alt made their first contribution in https://github.com/raysan5/raylib/pull/5672
* @georgik made their first contribution in https://github.com/raysan5/raylib/pull/5674
* @lvntky made their first contribution in https://github.com/raysan5/raylib/pull/5682
* @LewisLee26 made their first contribution in https://github.com/raysan5/raylib/pull/5693
* @bosoni made their first contribution in https://github.com/raysan5/raylib/pull/5696
* @dotmrjosh made their first contribution in https://github.com/raysan5/raylib/pull/5702
* @r3g492 made their first contribution in https://github.com/raysan5/raylib/pull/5708
* @arbipink made their first contribution in https://github.com/raysan5/raylib/pull/5713
* @angshumankishore made their first contribution in https://github.com/raysan5/raylib/pull/5727
* @mudhairless made their first contribution in https://github.com/raysan5/raylib/pull/5755
* @nadav78 made their first contribution in https://github.com/raysan5/raylib/pull/5763
* @nilsojunior made their first contribution in https://github.com/raysan5/raylib/pull/5766
* @areynaldo made their first contribution in https://github.com/raysan5/raylib/pull/5769
* @Monjaris made their first contribution in https://github.com/raysan5/raylib/pull/5722
* @Itwernme made their first contribution in https://github.com/raysan5/raylib/pull/5779

**Full Changelog**: https://github.com/raysan5/raylib/compare/5.5...6.0

---

## 5.5 - 2024-11-18

**raylib v5.5** by raysan5 - <https://github.com/raysan5/raylib/releases/tag/5.5>

![raylib55_banner](https://github.com/user-attachments/assets/2d18c1d8-e623-4f55-8496-bf6adfdb73df)

One year after raylib 5.0 release, arribes `raylib 5.5`, the next big revision of the library. It's been **11 years** since raylib 1.0 release and in all this time it has never stopped growing and improving. With an outstanding number of new contributors and improvements, it's, again, the biggest raylib release to date.

Some numbers for this release:

 - **+270** closed issues (for a TOTAL of **+1810**!)
 - **+800** commits since previous RELEASE (for a TOTAL of **+7770**!)
 - **+30** functions ADDED to raylib API (for a TOTAL of **580**!)
 - **+110** functions REVIEWED with fixes and improvements
 - **+140** new contributors (for a TOTAL of **+640**!)

Highlights for `raylib 5.5`:

 - **`NEW` raylib pre-configured Windows package**: The new raylib **portable and self-contained Windows package** for `raylib 5.5`, intended for nobel devs that start in programming world, comes with one big addition: support for **C code building for Web platform with one-single-mouse-click!** For the last 10 years, the pre-configured raylib Windows package allowed to edit simple C projects on Notepad++ and easely compile Windows executables with an automatic script; this new release adds the possibility to compile the same C projects for Web platform with a simple mouse click. This new addition **greatly simplifies C to WebAssembly project building for new users**. The `raylib Windows Installer` package can be downloaded for free from [raylib on itch.io](https://raysan5.itch.io/raylib).

 - **`NEW` raylib project creator tool**: A brand new tool developed to help raylib users to **setup new projects in a professional way**. `raylib project creator` generates a complete project structure with **multiple build systems ready-to-use** and **GitHub CI/CD actions pre-configured**. It only requires providing some C files and basic project parameters! The tools is [free and open-source](https://raysan5.itch.io/raylib-project-creator), and [it can be used online](https://raysan5.itch.io/raylib-project-creator)!.

 - **`NEW` Platform backend supported: RGFW**: Thanks to the `rcore` platform-split implemented in `raylib 5.0`, **adding new platforms backends has been greatly simplified**, new backends can be added using provided template, self-contained in a single C module, completely portable. A new platform backend has been added: [`RGFW`](https://github.com/raysan5/raylib/blob/master/src/platforms/rcore_desktop_rgfw.c). `RGFW` is a **new single-file header-only portable library** ([`RGFW.h`](https://github.com/ColleagueRiley/RGFW)) intended for platform-functionality management (windowing and inputs); in this case for **desktop platforms** (Windows, Linux, macOS) but also for **Web platform**. It adds a new alternative to the already existing `GLFW` and `SDL` platform backends.
 
 - **`NEW` Platform backend version supported: SDL3**: Previous `raylib 5.0` added support for `SDL2` library, and `raylib 5.5` not only improves SDL2 functionality, with several issues reviewed, but also adds support for the recently released big SDL update in years: [`SDL3`](https://wiki.libsdl.org/SDL3/FrontPage). Now users can **select at compile time the desired SDL version to use**, increasing the number of potential platforms supported in the future!
 
 - **`NEW` Retro-console platforms supported: Dreamcast, N64, PSP, PSVita, PS4**: Thanks to the platform-split on `raylib 5.0`, **supporting new platform backends is easier than ever!** Along the raylib `rlgl` module support for the  `OpenGL 1.1` graphics API, it opened the door to [**multiple homebrew retro-consoles backend implementations!**](https://github.com/raylib4Consoles) It's amazing to see raylib running on +20 year old consoles like [Dreamcast](https://github.com/raylib4Consoles/raylib4Dreamcast), [PSP](https://github.com/raylib4Consoles/raylib4Psp) or [PSVita](https://github.com/psp2dev/raylib4Vita), considering the hardware constraints of those platforms and proves **raylib outstanding versability!** Those additional platforms can be found in separate repositories and have been created by the amazing programmer Antonio Jose Ramos Marquez (@psxdev).
 
 - **`NEW` GPU Skinning support**: After lots of requests for this feature, it has been finally added to raylib thanks to the contributor Daniel Holden (@orangeduck), probably the developer that has further pushed models animations with raylib, developing two amazing tools to visualize and test animations: [GenoView](https://github.com/orangeduck/GenoView) and [BVHView](https://github.com/orangeduck/BVHView). Adding GPU skinning was a tricky feature, considering it had to be **available for all raylib supported platforms**, including limited ones like Raspberry Pi with OpenGL ES 2.0, where some advance OpenGL features are not available (UBO, SSBO, Transform Feedback) but a multi-platform solution was found to make it possible. A new example, [`models_gpu_skinning`](https://github.com/raysan5/raylib/blob/master/examples/models/models_gpu_skinning.c) has been added to illustrate this new functionality. As an extra, previous existing CPU animation system has been greatly improved, multiplying performance by a factor (simplifiying required maths).
 
 - **`NEW` [`raymath`](https://github.com/raysan5/raylib/blob/master/src/raymath.h) C++ operators**: After several requested for this feature, C++ math operators for `Vector2`, `Vector3`, `Vector4`, `Quaternion` and `Matrix` has been added to `raymath` as an extension to current implementation. Despite being only available for C++ because C does not support it, these operators **simplify C++ code when doing math operations**.

Beside those new big features, `raylib 5.5` comes with MANY other improvements: 

- Normals support on batching system
- Clipboard images reading support
- CRC32/MD5/SHA1 hash computation
- Gamepad vibration support
- Improved font loading (no GPU required) with BDF fonts support
- Time-based camera movement
- Improved GLTF animations loading

...and [much much more](https://github.com/raysan5/raylib/blob/master/CHANGELOG), including **many functions reviews and new functions added!**
 
Make sure to check raylib [CHANGELOG](https://github.com/raysan5/raylib/blob/master/CHANGELOG) for a detailed list of changes!

To end with, I want to **thank all the contributors (+640!**) that along the years have **greatly improved raylib** and pushed it further and better day after day. Thanks to all of them, raylib is the amazing library it is today.

Last but not least, I want to thank **raylib sponsors and all the raylib community** for their support and continuous engagement with the library, creating and sharing amazing raylib projects on a daily basis. **Thanks for making raylib a great platform to enjoy games/tools/graphic programming!**

**After 11 years of development, `raylib 5.5` is the best raylib ever.**

**Enjoy programming with raylib!** :)

## New Contributors
* @Kimo-s made their first contribution in https://github.com/raysan5/raylib/pull/3528
* @MrScautHD made their first contribution in https://github.com/raysan5/raylib/pull/3546
* @AuzFox made their first contribution in https://github.com/raysan5/raylib/pull/3552
* @Zapunidi made their first contribution in https://github.com/raysan5/raylib/pull/3555
* @ManuMario0 made their first contribution in https://github.com/raysan5/raylib/pull/3574
* @Minmoose made their first contribution in https://github.com/raysan5/raylib/pull/3609
* @davidthings made their first contribution in https://github.com/raysan5/raylib/pull/3615
* @riadbettole made their first contribution in https://github.com/raysan5/raylib/pull/3624
* @lipx1508 made their first contribution in https://github.com/raysan5/raylib/pull/3618
* @benjibst made their first contribution in https://github.com/raysan5/raylib/pull/3627
* @rmn20 made their first contribution in https://github.com/raysan5/raylib/pull/3631
* @orosmatthew made their first contribution in https://github.com/raysan5/raylib/pull/3632
* @Starpelly made their first contribution in https://github.com/raysan5/raylib/pull/3640
* @devdad made their first contribution in https://github.com/raysan5/raylib/pull/3621
* @DongkunLee made their first contribution in https://github.com/raysan5/raylib/pull/3536
* @Toctave made their first contribution in https://github.com/raysan5/raylib/pull/3585
* @cinghycreations made their first contribution in https://github.com/raysan5/raylib/pull/3641
* @tromero made their first contribution in https://github.com/raysan5/raylib/pull/3666
* @wisonye made their first contribution in https://github.com/raysan5/raylib/pull/3682
* @maverikou made their first contribution in https://github.com/raysan5/raylib/pull/3678
* @IoIxD made their first contribution in https://github.com/raysan5/raylib/pull/3681
* @seiren-games made their first contribution in https://github.com/raysan5/raylib/pull/3692
* @casavaca made their first contribution in https://github.com/raysan5/raylib/pull/3710
* @Minnowo made their first contribution in https://github.com/raysan5/raylib/pull/3712
* @LievenPetersen made their first contribution in https://github.com/raysan5/raylib/pull/3720
* @candrewlee14 made their first contribution in https://github.com/raysan5/raylib/pull/3727
* @karl-zylinski made their first contribution in https://github.com/raysan5/raylib/pull/3701
* @Blockguy24 made their first contribution in https://github.com/raysan5/raylib/pull/3732
* @JayLCypher made their first contribution in https://github.com/raysan5/raylib/pull/3737
* @idircarlos made their first contribution in https://github.com/raysan5/raylib/pull/3751
* @mllimo made their first contribution in https://github.com/raysan5/raylib/pull/3750
* @aubs-dev made their first contribution in https://github.com/raysan5/raylib/pull/3760
* @marrony made their first contribution in https://github.com/raysan5/raylib/pull/3770
* @bmbkr made their first contribution in https://github.com/raysan5/raylib/pull/3774
* @stanthesoupking made their first contribution in https://github.com/raysan5/raylib/pull/3735
* @The-Night-Watch made their first contribution in https://github.com/raysan5/raylib/pull/3776
* @oblerion made their first contribution in https://github.com/raysan5/raylib/pull/3771
* @jfoscarini made their first contribution in https://github.com/raysan5/raylib/pull/3799
* @BliznyukNM made their first contribution in https://github.com/raysan5/raylib/pull/3804
* @Logicless-Coder made their first contribution in https://github.com/raysan5/raylib/pull/3817
* @GideonSerf made their first contribution in https://github.com/raysan5/raylib/pull/3819
* @Dev-Tade made their first contribution in https://github.com/raysan5/raylib/pull/3832
* @GaryMcWhorter made their first contribution in https://github.com/raysan5/raylib/pull/3823
* @ipzaur made their first contribution in https://github.com/raysan5/raylib/pull/3833
* @Bowserinator made their first contribution in https://github.com/raysan5/raylib/pull/3828
* @hardliner66 made their first contribution in https://github.com/raysan5/raylib/pull/3835
* @zuckschwerdt made their first contribution in https://github.com/raysan5/raylib/pull/3839
* @aiafrasinei made their first contribution in https://github.com/raysan5/raylib/pull/3842
* @REDl3east made their first contribution in https://github.com/raysan5/raylib/pull/3846
* @joyousblunder made their first contribution in https://github.com/raysan5/raylib/pull/3868
* @zyperpl made their first contribution in https://github.com/raysan5/raylib/pull/3871
* @proberge-dev made their first contribution in https://github.com/raysan5/raylib/pull/3881
* @MrMugame made their first contribution in https://github.com/raysan5/raylib/pull/3879
* @ProIcons made their first contribution in https://github.com/raysan5/raylib/pull/3891
* @iarkn made their first contribution in https://github.com/raysan5/raylib/pull/3896
* @Belllg made their first contribution in https://github.com/raysan5/raylib/pull/3901
* @AriaMoKr made their first contribution in https://github.com/raysan5/raylib/pull/3910
* @He-Is-HaZaRdOuS made their first contribution in https://github.com/raysan5/raylib/pull/3908
* @Mute124 made their first contribution in https://github.com/raysan5/raylib/pull/3914
* @dylanlangston made their first contribution in https://github.com/raysan5/raylib/pull/3915
* @benjitrosch made their first contribution in https://github.com/raysan5/raylib/pull/3919
* @eldskald made their first contribution in https://github.com/raysan5/raylib/pull/3923
* @dertseha made their first contribution in https://github.com/raysan5/raylib/pull/3907
* @KotzaBoss made their first contribution in https://github.com/raysan5/raylib/pull/3912
* @lima-limon-inc made their first contribution in https://github.com/raysan5/raylib/pull/3938
* @OetkenPurveyorOfCode made their first contribution in https://github.com/raysan5/raylib/pull/3939
* @UmgefallenesGlas made their first contribution in https://github.com/raysan5/raylib/pull/3949
* @gabriel-marques made their first contribution in https://github.com/raysan5/raylib/pull/3956
* @ColleagueRiley made their first contribution in https://github.com/raysan5/raylib/pull/3941
* @alexmozaidze made their first contribution in https://github.com/raysan5/raylib/pull/3979
* @Filyus made their first contribution in https://github.com/raysan5/raylib/pull/3974
* @myQwil made their first contribution in https://github.com/raysan5/raylib/pull/3977
* @CosmicBagel made their first contribution in https://github.com/raysan5/raylib/pull/3983
* @cemalgnlts made their first contribution in https://github.com/raysan5/raylib/pull/3940
* @FishingHacks made their first contribution in https://github.com/raysan5/raylib/pull/3986
* @ListeriaM made their first contribution in https://github.com/raysan5/raylib/pull/3994
* @Odex64 made their first contribution in https://github.com/raysan5/raylib/pull/3995
* @sgalindo made their first contribution in https://github.com/raysan5/raylib/pull/3990
* @L-Briand made their first contribution in https://github.com/raysan5/raylib/pull/4004
* @avx0 made their first contribution in https://github.com/raysan5/raylib/pull/4011
* @DarkAssassin23 made their first contribution in https://github.com/raysan5/raylib/pull/4013
* @vaezim made their first contribution in https://github.com/raysan5/raylib/pull/4017
* @kai-z99 made their first contribution in https://github.com/raysan5/raylib/pull/4018
* @denovodavid made their first contribution in https://github.com/raysan5/raylib/pull/4022
* @paulmelis made their first contribution in https://github.com/raysan5/raylib/pull/4034
* @Sprixitite made their first contribution in https://github.com/raysan5/raylib/pull/4020
* @jgabaut made their first contribution in https://github.com/raysan5/raylib/pull/4039
* @KonradGrande made their first contribution in https://github.com/raysan5/raylib/pull/4040
* @fruzitent made their first contribution in https://github.com/raysan5/raylib/pull/4042
* @carverdamien made their first contribution in https://github.com/raysan5/raylib/pull/4049
* @lzralbu made their first contribution in https://github.com/raysan5/raylib/pull/4054
* @VitoTringolo made their first contribution in https://github.com/raysan5/raylib/pull/4053
* @TokyoSU made their first contribution in https://github.com/raysan5/raylib/pull/4059
* @ShalokShalom made their first contribution in https://github.com/raysan5/raylib/pull/4068
* @okvik made their first contribution in https://github.com/raysan5/raylib/pull/4027
* @spelufo made their first contribution in https://github.com/raysan5/raylib/pull/3744
* @CrackedPixel made their first contribution in https://github.com/raysan5/raylib/pull/4074
* @jspast made their first contribution in https://github.com/raysan5/raylib/pull/4104
* @brccabral made their first contribution in https://github.com/raysan5/raylib/pull/4105
* @FrankyBalu made their first contribution in https://github.com/raysan5/raylib/pull/4129
* @ninadsachania made their first contribution in https://github.com/raysan5/raylib/pull/4136
* @NishiOwO made their first contribution in https://github.com/raysan5/raylib/pull/4139
* @InventorXtreme made their first contribution in https://github.com/raysan5/raylib/pull/4150
* @kai-kj made their first contribution in https://github.com/raysan5/raylib/pull/4154
* @jkaup made their first contribution in https://github.com/raysan5/raylib/pull/4102
* @CDM15y made their first contribution in https://github.com/raysan5/raylib/pull/4167
* @jaens made their first contribution in https://github.com/raysan5/raylib/pull/4175
* @Jutastre made their first contribution in https://github.com/raysan5/raylib/pull/4179
* @SoloByte made their first contribution in https://github.com/raysan5/raylib/pull/4189
* @maxmutant made their first contribution in https://github.com/raysan5/raylib/pull/4184
* @rnpnr made their first contribution in https://github.com/raysan5/raylib/pull/4197
* @ZzzhHe made their first contribution in https://github.com/raysan5/raylib/pull/4186
* @lnc3l0t made their first contribution in https://github.com/raysan5/raylib/pull/4193
* @MaximKn1 made their first contribution in https://github.com/raysan5/raylib/pull/4202
* @hanaxars made their first contribution in https://github.com/raysan5/raylib/pull/4247
* @Paperdomo101 made their first contribution in https://github.com/raysan5/raylib/pull/4270
* @Bugsia made their first contribution in https://github.com/raysan5/raylib/pull/4276
* @Mercotui made their first contribution in https://github.com/raysan5/raylib/pull/4275
* @konstruktor227 made their first contribution in https://github.com/raysan5/raylib/pull/4279
* @satchelfrost made their first contribution in https://github.com/raysan5/raylib/pull/4203
* @Tchan0 made their first contribution in https://github.com/raysan5/raylib/pull/4284
* @IllusionMan1212 made their first contribution in https://github.com/raysan5/raylib/pull/4288
* @emdzej made their first contribution in https://github.com/raysan5/raylib/pull/4305
* @masnm made their first contribution in https://github.com/raysan5/raylib/pull/4308
* @Alex-Velez made their first contribution in https://github.com/raysan5/raylib/pull/4311
* @dostoievsky made their first contribution in https://github.com/raysan5/raylib/pull/4318
* @SusgUY446 made their first contribution in https://github.com/raysan5/raylib/pull/4310
* @foxblock made their first contribution in https://github.com/raysan5/raylib/pull/4302
* @orangeduck made their first contribution in https://github.com/raysan5/raylib/pull/4321
* @asdqwe made their first contribution in https://github.com/raysan5/raylib/pull/4334
* @Ridge3Dproductions made their first contribution in https://github.com/raysan5/raylib/pull/4332
* @FluxFlu made their first contribution in https://github.com/raysan5/raylib/pull/4356
* @VisenDev made their first contribution in https://github.com/raysan5/raylib/pull/4366
* @HarryDC made their first contribution in https://github.com/raysan5/raylib/pull/4373
* @cedeon made their first contribution in https://github.com/raysan5/raylib/pull/4374
* @yuval-herman made their first contribution in https://github.com/raysan5/raylib/pull/4383
* @R-YaTian made their first contribution in https://github.com/raysan5/raylib/pull/4384
* @Joshalosh made their first contribution in https://github.com/raysan5/raylib/pull/4382
* @arrecis made their first contribution in https://github.com/raysan5/raylib/pull/4391
* @rapha-s made their first contribution in https://github.com/raysan5/raylib/pull/4408
* @cypressru made their first contribution in https://github.com/raysan5/raylib/pull/4423
* @franztt made their first contribution in https://github.com/raysan5/raylib/pull/4421
* @juliohq made their first contribution in https://github.com/raysan5/raylib/pull/4428
* @mpv-enjoyer made their first contribution in https://github.com/raysan5/raylib/pull/4448
* @evertonse made their first contribution in https://github.com/raysan5/raylib/pull/4435
* @archewashi made their first contribution in https://github.com/raysan5/raylib/pull/4451
* @MikiZX1 made their first contribution in https://github.com/raysan5/raylib/pull/4460
* @waveydave made their first contribution in https://github.com/raysan5/raylib/pull/4461
* @decromo made their first contribution in https://github.com/raysan5/raylib/pull/4462
* @deathbeam made their first contribution in https://github.com/raysan5/raylib/pull/4468
* @kimierik made their first contribution in https://github.com/raysan5/raylib/pull/4485
* @OussamaTeyib made their first contribution in https://github.com/raysan5/raylib/pull/4493
* @zet23t made their first contribution in https://github.com/raysan5/raylib/pull/4494

**Full Changelog**: https://github.com/raysan5/raylib/compare/5.0...5.5

---

## 5.0 - 2023-11-18

**raylib v5.0** by raysan5 - <https://github.com/raysan5/raylib/releases/tag/5.0>

![raylib50_banner_10th_anniversary_github](https://github.com/raysan5/raylib/assets/5766837/f71081d5-aeeb-4dff-8663-fe73f7b2831d)

It's been **7 months** since latest raylib release and **10 years** since raylib 1.0 was officially released... what an adventure! In the last 10 years raylib has improved a lot, new functions have been added, many new features and improvements implemented, up to **500 contributors** have helped to shape the library as it is today. `raylib 5.0` is the final result of all this incredible amount of work and dedication. Here it is the summary with the key features and additions of this NEW major version of raylib.

Some numbers for this release:

 - **+200** closed issues (for a TOTAL of **+1540**!)
 - **+550** commits since previous RELEASE (for a TOTAL of **+6950**!)
 - **+35** functions ADDED to raylib API (for a TOTAL of **552**!)
 - **+60** functions REVIEWED/REDESIGNED
 - **+80** new contributors (for a TOTAL of **+500**!)

Highlights for `raylib 5.0`:

 - **`rcore` module platform-split**: Probably the biggest raylib redesign in the last 10 years. raylib started as a library targeting 3 desktop platforms: `Windows`, `Linux` and `macOS` (thanks to `GLFW` underlying library) but with the years support for several new platforms has been added (`Android`, `Web`, `Rapsberry Pi`, `RPI native`...); lot of the platform code was shared so the logic was all together on `rcore.c` module, separated by compilation flags. This approach was very handy but also made it very difficult to support new platforms and specially painful for contributors not familiar with the module, navigating +8000 lines of code in a single file. A big redesign was really needed but the amount of work required was humungus and quite scary for a solo-developer like me, moreover considering that everything was working and the chances to break things were really high. Fortunately, some contributors were ready for the task (@ubkp, @michaelfiber, @Bigfoot71) and thanks to their initiative and super-hard work, the `rcore` [platform split](https://github.com/raysan5/raylib/blob/master/src/platforms) has been possible! This new raylib architecture greatly improves the platforms maintenance but also greatly simplifies the addition of new platforms. A [`platforms/rcore_template.c`](https://github.com/raysan5/raylib/blob/master/src/platforms/rcore_template.c) file is provided with the required structure and functions to be filled for the addition of new platforms, actually it has been simplified to mostly filling some pre-defined functions: `InitPlatform()`, `ClosePlatform`, `PollInputEvents`... Undoubtely, **this redesign opens the doors to a new era for raylib**, letting the users to plug new platforms as desired.
 
 - **`NEW` Platform backend supported: SDL**: Thanks to the new `rcore` platform-split, the addition of new platforms/backends to raylib has been greatly simplified. As a proof of concept, [`SDL2`](https://libsdl.org/) platform backend has been added to raylib as an aternative for `GLFW` library for desktop builds: [`platforms/rcore_desktop_sdl`](https://github.com/raysan5/raylib/blob/master/src/platforms/rcore_desktop_sdl.c). Lot of work has been put to provide exactly the same features as the other platforms and carefully test the new implementation. Now `SDL2` fans can use this new backend, just providing the required include libraries on compilation and linkage (not included in raylib, like `GLFW`). `SDL` backend support also **eases the process of supporting a wider range of platforms** that already support `SDL`.

 - **`NEW` Platform backend supported: Nintendo Switch (closed source)**: The addition of the `SDL` backend was quite a challenge but to really verify the robustness and ease of the new platform plugin system, adding support for a console was a more demanding adventure. Surprisingly, only two days of work were required to add support for `Nintendo Switch` to raylib! Implementation result showed an outstanding level of simplicity, with a **self-contained module** (`rcore_swith.cpp`) supporting graphics and inputs. Unfortunately this module can not be open-sourced due to licensing restrictions.

 - **`NEW` Splines drawing and evaluation API**: A complete set of functions has been added to [draw](https://github.com/raysan5/raylib/blob/5.0/src/raylib.h#L1258) and [evaluate](https://github.com/raysan5/raylib/blob/5.0/src/raylib.h#L1270) different types of splines: `Linear`, `Basis`, `Catmull-Rom`, `Quadratic Bezier` and `Cubic Bezier`. Splines are extremely useful for game development (describe paths, control NPC movement...) but they can also be very useful on tools development (node-conections, elements-movement, 3d modelling, animations...). This was the missing feature on the raylib [`rshapes`](https://github.com/raysan5/raylib/blob/5.0/src/rshapes.c) module to make it complete! Note that `rshapes` module can also be used independently of raylib just providing the **only 6 functions required for vertex definition and drawing**.
 
 - **`NEW` Pseudo-random numbers generator: rprand**: After several years of users asking for this missing piece, a brand new pseudo-random generator module has been added to raylib. [`rprand`](https://github.com/raysan5/raylib/blob/5.0/src/external/rprand.h) implements the `Xoshiro128**` algorithm combined with `SplitMix64`, specially suited for **fast software pseudo-random numbers generation**. The module also implies some useful functions to generate non-repetitive random numbers sequences, functionality exposed by raylib. usage of this module can be controlled by a compilation flag, in case the default libc `rand()` function was preferred.

 - **`NEW` Automation Events System API**: This new system was first added in `raylib 4.0` as an experimental feature but it was a bit clumsy and there was no API exposed to users. For the new `raylib 5.0` the system has been redesigned and [proper API](https://github.com/raysan5/raylib/blob/5.0/src/raylib.h#L1135) added for the users. With this new events automation system, users can **record input events for later replay**, very useful feature for testing automation, tutorials generation, assisted game playing, in-game cinematics, speedruns saving or even AI assited game playing!

 - **`NEW` [`raygui 4.0`](https://github.com/raysan5/raygui)**: The **official raylib immediate-mode gui library** designed for tools development has been updated to a new version, aligned with raylib 5.0. This new version is a complete redesign of raygui to unify all controls structure and usage, now all controls have the same function signature!. `raygui` has been battle-tested with the development of +12 published tools in the last few years. The tools can be seen and used for free in the [raylib technologies tools page](https://raylibtech.itch.io/). Worth mentioning that several of those **tools have been open sourced** for anyone to use, compile, contribute or learn how the code works.

 - **`NEW` raylib web examples functionality**: Beside the addition of several new examples, the web examples functionality has been improved. Examples have been organized by [complexity level](https://www.raylib.com/examples.html), marked with one star for simple examples and up to 4 stars for more complex ones. A new option has been added to web to allow to **filter examples by function-name** usage, to ease the learning process when looking for an usage example of some function. Finally, **open-graph metadata** information has been added to all examples individual webpages, improving a the visuals and information when sharing those webpages on social networks, sharing the example screenshot and details.

As always, those are only some highlights of the new `raylib 5.0` but there is many more improvements! Support for 16-bit HDR images/textures, SVG loading and scaling support, new OpenGL ES 3.0 graphic backend, new image gradient generators, sound alias loading, improved 3d models loading, multiple optimizations, new bindings, CodeQL integration and much more! 
 
Make sure to check raylib [CHANGELOG]([CHANGELOG](https://github.com/raysan5/raylib/blob/5.0/CHANGELOG)) for a detailed list of changes!

Undoubtely, this is the **biggest raylib update in 10 years**. Many new features and improvements with a special focus on maintainabiliy and long-term sustainability. **Undoubtely, this is the raylib of the future**.

**Enjoy programming!** :)


## New Contributors
* @Koromix made their first contribution in https://github.com/raysan5/raylib/pull/2968
* @Webfra made their first contribution in https://github.com/raysan5/raylib/pull/2972
* @eltociear made their first contribution in https://github.com/raysan5/raylib/pull/2976
* @devmanso made their first contribution in https://github.com/raysan5/raylib/pull/2977
* @gingerBill made their first contribution in https://github.com/raysan5/raylib/pull/2981
* @jarroddavis68 made their first contribution in https://github.com/raysan5/raylib/pull/2983
* @RicoP made their first contribution in https://github.com/raysan5/raylib/pull/2982
* @chocolate42 made their first contribution in https://github.com/raysan5/raylib/pull/2997
* @eternalStudent made their first contribution in https://github.com/raysan5/raylib/pull/3006
* @benjamin-thomas made their first contribution in https://github.com/raysan5/raylib/pull/3014
* @RadsammyT made their first contribution in https://github.com/raysan5/raylib/pull/3013
* @Soutaisei made their first contribution in https://github.com/raysan5/raylib/pull/3017
* @szsam made their first contribution in https://github.com/raysan5/raylib/pull/3021
* @kolunmi made their first contribution in https://github.com/raysan5/raylib/pull/3031
* @Bigfoot71 made their first contribution in https://github.com/raysan5/raylib/pull/3032
* @Stopfield made their first contribution in https://github.com/raysan5/raylib/pull/3033
* @nullstare made their first contribution in https://github.com/raysan5/raylib/pull/3043
* @Gamer-Kold made their first contribution in https://github.com/raysan5/raylib/pull/3045
* @alfredbaudisch made their first contribution in https://github.com/raysan5/raylib/pull/3044
* @Shoozza made their first contribution in https://github.com/raysan5/raylib/pull/3048
* @manuel5975p made their first contribution in https://github.com/raysan5/raylib/pull/3052
* @lesleyrs made their first contribution in https://github.com/raysan5/raylib/pull/3062
* @hamyyy made their first contribution in https://github.com/raysan5/raylib/pull/3058
* @crynux made their first contribution in https://github.com/raysan5/raylib/pull/3065
* @PixelPhobicGames made their first contribution in https://github.com/raysan5/raylib/pull/3066
* @danemadsen made their first contribution in https://github.com/raysan5/raylib/pull/3074
* @Luramoth made their first contribution in https://github.com/raysan5/raylib/pull/3079
* @jasonliang-dev made their first contribution in https://github.com/raysan5/raylib/pull/3082
* @archydragon made their first contribution in https://github.com/raysan5/raylib/pull/3083
* @rayit made their first contribution in https://github.com/raysan5/raylib/pull/3085
* @yujiri8 made their first contribution in https://github.com/raysan5/raylib/pull/3090
* @TheLastBilly made their first contribution in https://github.com/raysan5/raylib/pull/3091
* @chemaguerra made their first contribution in https://github.com/raysan5/raylib/pull/3107
* @dantecatalfamo made their first contribution in https://github.com/raysan5/raylib/pull/3115
* @Gisteron made their first contribution in https://github.com/raysan5/raylib/pull/3150
* @ewpratten made their first contribution in https://github.com/raysan5/raylib/pull/3164
* @superxkooda made their first contribution in https://github.com/raysan5/raylib/pull/3176
* @RokasPuzonas made their first contribution in https://github.com/raysan5/raylib/pull/3181
* @AlbertoGP made their first contribution in https://github.com/raysan5/raylib/pull/3186
* @danilwhale made their first contribution in https://github.com/raysan5/raylib/pull/3189
* @smalltimewizard made their first contribution in https://github.com/raysan5/raylib/pull/3185
* @jakubvf made their first contribution in https://github.com/raysan5/raylib/pull/3191
* @bohonghuang made their first contribution in https://github.com/raysan5/raylib/pull/3203
* @ndytts made their first contribution in https://github.com/raysan5/raylib/pull/3211
* @mode777 made their first contribution in https://github.com/raysan5/raylib/pull/3212
* @kassane made their first contribution in https://github.com/raysan5/raylib/pull/3214
* @VitusVeit made their first contribution in https://github.com/raysan5/raylib/pull/3222
* @mohad12211 made their first contribution in https://github.com/raysan5/raylib/pull/3230
* @actondev made their first contribution in https://github.com/raysan5/raylib/pull/3254
* @asdqwe made their first contribution in https://github.com/raysan5/raylib/pull/3258
* @Dial0 made their first contribution in https://github.com/raysan5/raylib/pull/3263
* @n77y made their first contribution in https://github.com/raysan5/raylib/pull/3256
* @branc116 made their first contribution in https://github.com/raysan5/raylib/pull/3261
* @jbarthelmes made their first contribution in https://github.com/raysan5/raylib/pull/3283
* @SuperUserNameMan made their first contribution in https://github.com/raysan5/raylib/pull/3296
* @vushu made their first contribution in https://github.com/raysan5/raylib/pull/3299
* @gabrielssanches made their first contribution in https://github.com/raysan5/raylib/pull/3298
* @wilsonsilva made their first contribution in https://github.com/raysan5/raylib/pull/3318
* @Codom made their first contribution in https://github.com/raysan5/raylib/pull/3321
* @WraithGlade made their first contribution in https://github.com/raysan5/raylib/pull/3350
* @thechampagne made their first contribution in https://github.com/raysan5/raylib/pull/3358
* @blueloveTH made their first contribution in https://github.com/raysan5/raylib/pull/3361
* @luis605 made their first contribution in https://github.com/raysan5/raylib/pull/3353
* @DaveH355 made their first contribution in https://github.com/raysan5/raylib/pull/3363
* @purple4pur made their first contribution in https://github.com/raysan5/raylib/pull/3393
* @Murlocohol made their first contribution in https://github.com/raysan5/raylib/pull/3394
* @BabakSamimi made their first contribution in https://github.com/raysan5/raylib/pull/3403
* @KislyjKisel made their first contribution in https://github.com/raysan5/raylib/pull/3405
* @BeardedBread made their first contribution in https://github.com/raysan5/raylib/pull/3414
* @bluesillybeard made their first contribution in https://github.com/raysan5/raylib/pull/3417
* @jcorks made their first contribution in https://github.com/raysan5/raylib/pull/3427
* @neyrox made their first contribution in https://github.com/raysan5/raylib/pull/3425
* @rexim made their first contribution in https://github.com/raysan5/raylib/pull/3434
* @keithstellyes made their first contribution in https://github.com/raysan5/raylib/pull/3449
* @gk646 made their first contribution in https://github.com/raysan5/raylib/pull/3458
* @2Bear made their first contribution in https://github.com/raysan5/raylib/pull/3469
* @M374LX made their first contribution in https://github.com/raysan5/raylib/pull/3468
* @jestarray made their first contribution in https://github.com/raysan5/raylib/pull/3464
* @khalid586 made their first contribution in https://github.com/raysan5/raylib/pull/3477
* @JaanDev made their first contribution in https://github.com/raysan5/raylib/pull/3483
* @JettMonstersGoBoom made their first contribution in https://github.com/raysan5/raylib/pull/3490
* @27justin made their first contribution in https://github.com/raysan5/raylib/pull/3496
* @Techuuu made their first contribution in https://github.com/raysan5/raylib/pull/3495
* @cabarger made their first contribution in https://github.com/raysan5/raylib/pull/3501
* @AndreaBoroni made their first contribution in https://github.com/raysan5/raylib/pull/3505
* @freakmangd made their first contribution in https://github.com/raysan5/raylib/pull/3506
* @glowiak made their first contribution in https://github.com/raysan5/raylib/pull/3508
* @icy-comet made their first contribution in https://github.com/raysan5/raylib/pull/3511
* @b4yuan made their first contribution in https://github.com/raysan5/raylib/pull/3476
* @awfulcooking made their first contribution in https://github.com/raysan5/raylib/pull/3514
* @maksut made their first contribution in https://github.com/raysan5/raylib/pull/3518
* @mmilenkov made their first contribution in https://github.com/raysan5/raylib/pull/3519
* @isaacgravenortechnologies made their first contribution in https://github.com/raysan5/raylib/pull/3525

**Full Changelog**: https://github.com/raysan5/raylib/compare/4.5.0...5.0

---

## 4.6-dev - 2023-10-08

**raylib v4.6-dev** by raysan5 - <https://github.com/raysan5/raylib/releases/tag/4.6-dev>

**This is not a raylib release**

This pre-release is created only for the tag before a BIG library redesign merge.

`rcore` module has been split per-platform, this is one of the big changes comming to the future `raylib 5.0` release.

Just creating this point in time in case everything needs to be reverted (hopefully not).

So, time to merge changes for the new release...

---

## 4.5.0 - 2023-03-18

**raylib v4.5** by raysan5 - <https://github.com/raysan5/raylib/releases/tag/4.5.0>

![raylib_release_promo_450](https://user-images.githubusercontent.com/5766837/226331474-61ebe2b2-dbe4-46e7-8ab5-7ffb4a6d5fae.png)

It's been **7 months** since latest raylib release. As usual, **many parts of the library have been reviewed and improved** along those months. Many issues have been closed, staying under 10 open issues at the moment of this writting and also many PRs from contributors have been received, reviewed and merged into raylib library. Some new functions have been added and some others have been removed to improve library coherence and avoid moving too high level, giving the users the tools to implement advance functionality themselfs over raylib. Again, this is a big release with a considerable amount of changes and improvements. Here it is a small summary highlighting this new **rayib 4.5**.

Some numbers for this release:

 - **+100** closed issues (for a TOTAL of **+1340**!)
 - **+350** commits since previous RELEASE (for a TOTAL of **+6350**!)
 - **+25** functions ADDED to raylib API (for a TOTAL of **516**!)
 - **+40** functions REVIEWED/REDESIGNED
 - **+40** new contributors (for a TOTAL of **405**!)

Highlights for `raylib 4.5`:

 - **`NEW` Improved ANGLE support on Desktop platforms**: Support for OpenGL ES 2.0 on Desktop platforms (Windows, Linux, macOS) has been reviewed by @wtnbgo GitHub user. Now raylib can be compiled on desktop for OpenGL ES 2.0 and linked against [`ANGLE`](https://github.com/google/angle). This _small_ addition open the door to building raylib for all **ANGLE supported backends: Direct3D 11, Vulkan and Metal**. Please note that this new feature is still experimental and requires further testing!

 - **`NEW` Camera module**: A brand new implementation from scratch for `rcamera` module, contributed by @Crydsch GitHub user! **New camera system is simpler, more flexible, more granular and more extendable**. Specific camera math transformations (movement/rotation) have been moved to individual functions, exposing them to users if required. Global state has been removed from the module and standalone usage has been greatly improved; now `rcamera.h` single-file header-only library can be used externally, independently of raylib. A new `UpdateCameraPro()` function has been added to address input-dependency of `UpdateCamera()`, now advance users have **full control over camera inputs and movement/rotation speeds**!
 
 - **`NEW` Support for M3D models and M3D/GLTF animations**: 3d models animations support has been a limited aspect of raylib for long time, some versions ago IQM animations were supported but raylib 4.5 also adds support for the brand new [M3D file format](https://bztsrc.gitlab.io/model3d/), including animations and the long expected support for **GLTF animations**! The new M3D file format is **simple, portable, feature complete, extensible and open source**. It also provides a complete set of tools to export/visualize M3D models from/to Blender! Now raylib supports up to **3 model file-formats with animations**: `IQM`, `GLTF` and `M3D`.
 
 - **`NEW` Support QOA audio format (import/export)**: Just a couple of months ago the new [QOA file format](https://qoaformat.org/) was published, a very simple, portable and open source quite-ok-audio file format. raylib already supports it, added to `raudio` module and including audio loading from file, loading from memory, streaming from file, streaming from memory and **exporting to QOA** audio format. **Because simplicity really matters to raylib!**
 
 - **`NEW` Module for compressed textures loading**: [`rl_gputex`](https://github.com/raysan5/raylib/blob/master/src/external/rl_gputex.h), a portable single-file header-only small library to load compressed texture file-formats (DDS, PKM, KTX, PVR, ASTC). Provided functionality is not new to raylib but it was part of the raylib `rtextures` module, now it has been moved into a separate self-contained library, **improving portability**. Note that this module is only intended to **load compressed data from files, ready to be uploaded to GPU**, no compression/decompression functionality is provided. This change is a first step towards a better modularization of raylib library.
 
 - **Reviewed `rlgl` module for automatic limits checking**: Again, [`rlgl`](https://github.com/raysan5/raylib/blob/master/src/rlgl.h) has been reviewed to simplify usage. Now users do not need to worry about reaching the internal render-batch limits when they send their triangles to draw 2d/3d, `rlgl` manages it automatically! This change allows a **great simplification for other modules** like `rshapes`, `rtextures` and `rmodels` that do not need to worry about bufffer overflows and can just define as many vertex as desired!
 
 - **Reviewed `rshapes` module to minimize the rlgl dependency**: Now `rshapes` 2d shapes drawing functions **only depend on 6 low-level functions**: `rlBegin()`, `rlEnd()`, `rlVertex3f()`, `rlTexCoord2f()`, `rlNormal3f()`, `rlSetTexture()`. With only those pseudo-OpenGl 1.1 minimal functionality, everything can be drawn! This improvement converts `rshapes` module in a **self-contained, portable shapes-drawing library that can be used independently of raylib**, as far as entry points for those 6 functions are provided by the user. It even allows to be used for software rendering, with the proper backend! 

 - **Added data structures validation functions**: Multiple functions have been added by @RobLoach GitHub user to ease the validation of raylib data structures: `IsImageReady()`, `IsTextureReady()`, `IsSoundReady()`... Now users have a simple mechanism to **make sure data has been correctly loaded**, instead of checking internal structure values by themselfs.
 
As usual, those are only some highlights but there is much more! New image generators, new color transformation functionality, improved blending support for color/alpha, etc... Make sure to check raylib [CHANGELOG](https://github.com/raysan5/raylib/blob/master/CHANGELOG) for a detailed list of changes! Please, note that all breaking changes have been flagged with a `WARNING` in the CHANGELOG, specially useful for binding creators!

**raylib keeps improving one more version** with a special focus on maintainability and sustainability. Always working towards making the library more **simple and easy-to-use**. 

Let's keep **enjoying games/tools/graphics programming!** :)

## New Contributors
* @trumoose made their first contribution in https://github.com/raysan5/raylib/pull/2640
* @daipom made their first contribution in https://github.com/raysan5/raylib/pull/2643
* @disketteman made their first contribution in https://github.com/raysan5/raylib/pull/2682
* @acejacek made their first contribution in https://github.com/raysan5/raylib/pull/2685
* @skylar779 made their first contribution in https://github.com/raysan5/raylib/pull/2687
* @murilluhenrique made their first contribution in https://github.com/raysan5/raylib/pull/2696
* @AQuantumPotato made their first contribution in https://github.com/raysan5/raylib/pull/2701
* @deniska made their first contribution in https://github.com/raysan5/raylib/pull/2702
* @bXi made their first contribution in https://github.com/raysan5/raylib/pull/2719
* @realtradam made their first contribution in https://github.com/raysan5/raylib/pull/2737
* @pure01fx made their first contribution in https://github.com/raysan5/raylib/pull/2741
* @JupiterRider made their first contribution in https://github.com/raysan5/raylib/pull/2745
* @SzieberthAdam made their first contribution in https://github.com/raysan5/raylib/pull/2746
* @hatkidchan made their first contribution in https://github.com/raysan5/raylib/pull/2750
* @Anut-py made their first contribution in https://github.com/raysan5/raylib/pull/2753
* @Its-Kenta made their first contribution in https://github.com/raysan5/raylib/pull/2757
* @IanBand made their first contribution in https://github.com/raysan5/raylib/pull/2761
* @InKryption made their first contribution in https://github.com/raysan5/raylib/pull/2763
* @IsaacTCB made their first contribution in https://github.com/raysan5/raylib/pull/2783
* @RomanAkberov made their first contribution in https://github.com/raysan5/raylib/pull/2786
* @RGDTAB made their first contribution in https://github.com/raysan5/raylib/pull/2787
* @SpexGuy made their first contribution in https://github.com/raysan5/raylib/pull/2793
* @shelvick made their first contribution in https://github.com/raysan5/raylib/pull/2796
* @Pere001 made their first contribution in https://github.com/raysan5/raylib/pull/2800
* @jtainer made their first contribution in https://github.com/raysan5/raylib/pull/2797
* @lxmcf made their first contribution in https://github.com/raysan5/raylib/pull/2804
* @simendsjo made their first contribution in https://github.com/raysan5/raylib/pull/2826
* @AlxHnr made their first contribution in https://github.com/raysan5/raylib/pull/2829
* @turborium made their first contribution in https://github.com/raysan5/raylib/pull/2838
* @Wytekol made their first contribution in https://github.com/raysan5/raylib/pull/2846
* @BugraAlptekinSari made their first contribution in https://github.com/raysan5/raylib/pull/2836
* @charles-l made their first contribution in https://github.com/raysan5/raylib/pull/2844
* @wtnbgo made their first contribution in https://github.com/raysan5/raylib/pull/2840
* @ImazighenGhost made their first contribution in https://github.com/raysan5/raylib/pull/2857
* @masoudd made their first contribution in https://github.com/raysan5/raylib/pull/2870
* @KOLANICH made their first contribution in https://github.com/raysan5/raylib/pull/2877
* @PencilAmazing made their first contribution in https://github.com/raysan5/raylib/pull/2882
* @the-argus made their first contribution in https://github.com/raysan5/raylib/pull/2905
* @haved made their first contribution in https://github.com/raysan5/raylib/pull/2909
* @star-tek-mb made their first contribution in https://github.com/raysan5/raylib/pull/2910
* @stickM4N made their first contribution in https://github.com/raysan5/raylib/pull/2914
* @fubark made their first contribution in https://github.com/raysan5/raylib/pull/2939
* @Skaytacium made their first contribution in https://github.com/raysan5/raylib/pull/2951
* @ashn-dot-dev made their first contribution in https://github.com/raysan5/raylib/pull/2958
* @Brian-ED made their first contribution in https://github.com/raysan5/raylib/pull/2962

**Full Changelog**: https://github.com/raysan5/raylib/compare/4.2.0...4.5.0

---

## 4.2.0 - 2022-08-13

**raylib v4.2.0** by raysan5 - <https://github.com/raysan5/raylib/releases/tag/4.2.0>

**New raylib release!** Nine months after latest raylib, here it is a new version. It was supposed to be just a small update but, actually, it's a huge update with lots of changes and improvements. It has been possible thanks to the many contributors that have helped with issues and improvements, it's the **update with more contributors to date** and that's amazing!

Some numbers to start with:

 - **+200** closed issues (for a TOTAL of **1230**!)
 - **+550** commits since previous RELEASE (for a TOTAL of **+6000**!)
 - **+20** functions ADDED to raylib API (for a TOTAL of **502**!)
 - **+60** functions REVIEWED/REDESIGNED
 - **+70** new contributors (for a TOTAL of **+360**!)

Highlights for `raylib 4.2`:

 - **raylib extra libraries cleanup**: raylib has been on diet and all the _extra_ libraries included on previous releases have been removed from raylib. Now raylib only includes the original **7** raylib modules: `rcore`, `rlgl`, `rshapes`, `rtextures`, `rtext`, `rmodels` and `raudio`. But no worries, _extra_ libraries have not been deleted, they have been moved to their own repos for better maintainability and more focus on its functionality. The libraries moved out from raylib repo are: [`raygui`](https://github.com/raysan5/raygui), [`physac`](https://github.com/raysan5/physac), [`rmem`](https://github.com/raylib-extras/rmem), [`reasings`](https://github.com/raylib-extras/reasings) and [`raudio`](https://github.com/raysan5/raudio) (standalone mode). On that same line, a new **amazing GitHub group:** [`raylib-extras`](https://github.com/raylib-extras) has been created by @JeffM2501 to contain raylib extra libraries as well as other raylib add-ons provided by the community. Jeff has done an amazing work on that line, providing multiple libraries and examples for raylib, like [custom first-person and third person camera systems](https://github.com/raylib-extras/extras-c/tree/main/cameras), [Dear ImGui raylib integration](https://github.com/raylib-extras/rlImGui), [multiple specific examples](https://github.com/raylib-extras/examples-c) and even a complete [RPG Game Example](https://github.com/raylib-extras/RPGExample)! Great work Jeff! :D
 
 - **raylib examples review**: The +120 raylib examples have been reviewed to add clearer information about when they were first created (raylib version used) and when they were updated for the last time. But the greatest improvement for users has been the **addition of an estimated difficulty level** for every example, [web has been updated accordingly](https://www.raylib.com/examples.html) to reflect those difficulty levels. Now examples are classified with **1 to 4 stars** depending on difficulty to help users with their learning process. Personally, I think this "small" addition could be a game-changer to better guide new users on the library adoption! Additionally, this new raylib release includes 7 new examples; the most interesting one: [`text_codepoints_loading`](https://www.raylib.com/examples/text/loader.html?name=text_codepoints_loading) that illustrates how to load and draw custom codepoints from a font file, very useful for Asian languages. 

 - [**`rres 1.0`**](https://github.com/raysan5/rres): New `rres` **resources packaging file-format**, including a [`rres-raylib`](https://github.com/raysan5/rres/blob/master/src/rres-raylib.h) library implementation and [`rrespacker`](https://raylibtech.itch.io/rrespacker) tool. `rres` file format has been [under development for +8 years](https://github.com/raysan5/rres#design-history) and it was originally created to be part of raylib. It was highly inspired by _XNA XNB_ resources file format but design has changed a lot along the years. This first release of the format specs is engine-agnostic and has been designed to be portable to any engine, including lots of professional features like data processing, compression and encryption.

 - [**`raygui 3.2`**](https://github.com/raysan5/raygui): The **official raylib immediate-mode gui library** designed for tools development has been updated to a new version aligned with raylib 4.2. Multiple controls have been reviewed for library consistency, now all controls follow a similar function signature. It has been battle-tested with the development of +8 published tools in the last months. The tools can be seen and used for free in the [raylib technologies tools page](https://raylibtech.itch.io/). Worth mentioning that several of those **tools have been open sourced** for anyone to use, compile, contribute or learn how the code works.
 
 - [**`raylib_parser`**](https://github.com/raysan5/raylib/tree/master/parser): Multiple contributors **using the tool to automatize bindings creation** have contributed with improvements of this **tool to parse `raylib.h`** (and other raylib-style headers) to tokenize its enums, structs and functions. Processed data can be exported to custom file formats (i.e XML, JSON, LUA) for bindings generation or even docs generation if required.

 - **New file system API**: Current API has been redesigned to be more comprehensive and better aligned with raylib naming conventions, two new functions are provided `LoadDirectoryFiles()`/`LoadDirectoryFilesEx()` to load a `FilePathList` for provided path, supporting extension filtering and recursive directory scan. `LoadDroppedFiles()` has been renamed to better reflect its internal functionality. Now, all raylib functions that start with `Load*()` allocate memory internally and a equivalent `Unload*()` function is defined to take care of that memory internally when not required any more!

 - **New audio stream processors API** (_experimental_): Now real-time audio stream data processors can be added using callbacks to played Music. It allows users to create custom effects for audio like delays of low-pass-filtering (example provided). The new API uses a callback system and it's still _ highly experimental_, it differs from the usual level of complexity that provides raylib and it is intended for advance users. It could change in the future but, actually, `raudio` module is in the spotlight for future updates; [miniaudio](https://github.com/mackron/miniaudio) implements a new higher-level API that can be useful in the future for raylib.

As always, there are more improvements than the key features listed, make sure to check raylib [CHANGELOG](CHANGELOG) for the detailed list of changes; for this release a `WARNING` flag has been added to all the changes that could affect bindings or productivity code. **raylib keeps improving one more version** and a special focus on maintainability has been put on the library for the future. Specific/advance functionality will be provided through **raylib-extras** repos and raylib main repo devlelopment will be focused on what made raylib popular: being a simple and easy-to-use library to **enjoy videogames programming**.

**Enjoy gamedev/tools/graphics programming!** :)

### New Contributors
* @KonPet made their first contribution in https://github.com/raysan5/raylib/pull/2111
* @Schweinepriester made their first contribution in https://github.com/raysan5/raylib/pull/2114
* @WIITD made their first contribution in https://github.com/raysan5/raylib/pull/2116
* @lukekras made their first contribution in https://github.com/raysan5/raylib/pull/2121
* @ampers0x26 made their first contribution in https://github.com/raysan5/raylib/pull/2126
* @sol-vin made their first contribution in https://github.com/raysan5/raylib/pull/2130
* @ronnieholm made their first contribution in https://github.com/raysan5/raylib/pull/2136
* @WilledgeR made their first contribution in https://github.com/raysan5/raylib/pull/2148
* @wolfenrain made their first contribution in https://github.com/raysan5/raylib/pull/2149
* @ytrms made their first contribution in https://github.com/raysan5/raylib/pull/2156
* @pancakevirus made their first contribution in https://github.com/raysan5/raylib/pull/2163
* @jasonswearingen made their first contribution in https://github.com/raysan5/raylib/pull/2168
* @anders-n08 made their first contribution in https://github.com/raysan5/raylib/pull/2175
* @Toby222 made their first contribution in https://github.com/raysan5/raylib/pull/2179
* @HarriP made their first contribution in https://github.com/raysan5/raylib/pull/2189
* @jdeokkim made their first contribution in https://github.com/raysan5/raylib/pull/2196
* @petelliott made their first contribution in https://github.com/raysan5/raylib/pull/2202
* @eutro made their first contribution in https://github.com/raysan5/raylib/pull/2208
* @ptarabbia made their first contribution in https://github.com/raysan5/raylib/pull/2215
* @wereii made their first contribution in https://github.com/raysan5/raylib/pull/2217
* @pitpit made their first contribution in https://github.com/raysan5/raylib/pull/2233
* @salotz made their first contribution in https://github.com/raysan5/raylib/pull/2238
* @planetis-m made their first contribution in https://github.com/raysan5/raylib/pull/2243
* @shivajiva101 made their first contribution in https://github.com/raysan5/raylib/pull/2253
* @tusharsingh09 made their first contribution in https://github.com/raysan5/raylib/pull/2254
* @glorantq made their first contribution in https://github.com/raysan5/raylib/pull/2260
* @gtrxAC made their first contribution in https://github.com/raysan5/raylib/pull/2264
* @hero2002 made their first contribution in https://github.com/raysan5/raylib/pull/2270
* @ArchieAtkinson made their first contribution in https://github.com/raysan5/raylib/pull/2276
* @hartmannathan made their first contribution in https://github.com/raysan5/raylib/pull/2277
* @MatthewOwens made their first contribution in https://github.com/raysan5/raylib/pull/2281
* @phil-shenk made their first contribution in https://github.com/raysan5/raylib/pull/2296
* @royqh1979 made their first contribution in https://github.com/raysan5/raylib/pull/2298
* @siddharthroy12 made their first contribution in https://github.com/raysan5/raylib/pull/2308
* @makuto made their first contribution in https://github.com/raysan5/raylib/pull/2318
* @megagrump made their first contribution in https://github.com/raysan5/raylib/pull/2324
* @audinue made their first contribution in https://github.com/raysan5/raylib/pull/2319
* @locriacyber made their first contribution in https://github.com/raysan5/raylib/pull/2329
* @zigster64 made their first contribution in https://github.com/raysan5/raylib/pull/2332
* @DavidLyhedDanielsson made their first contribution in https://github.com/raysan5/raylib/pull/2347
* @chrisws made their first contribution in https://github.com/raysan5/raylib/pull/2366
* @IrishBruse made their first contribution in https://github.com/raysan5/raylib/pull/2375
* @AnilBK made their first contribution in https://github.com/raysan5/raylib/pull/2376
* @Hejsil made their first contribution in https://github.com/raysan5/raylib/pull/2383
* @tixvage made their first contribution in https://github.com/raysan5/raylib/pull/2384
* @guidoism made their first contribution in https://github.com/raysan5/raylib/pull/2385
* @kristianlm made their first contribution in https://github.com/raysan5/raylib/pull/2390
* @futureapricot made their first contribution in https://github.com/raysan5/raylib/pull/2396
* @joaotavora made their first contribution in https://github.com/raysan5/raylib/pull/2398
* @tana made their first contribution in https://github.com/raysan5/raylib/pull/2419
* @ZimonIsHim made their first contribution in https://github.com/raysan5/raylib/pull/2423
* @twuky made their first contribution in https://github.com/raysan5/raylib/pull/2431
* @saccharineboi made their first contribution in https://github.com/raysan5/raylib/pull/2428
* @FireFlyForLife made their first contribution in https://github.com/raysan5/raylib/pull/2424
* @jcgamestoy made their first contribution in https://github.com/raysan5/raylib/pull/2437
* @leomonta made their first contribution in https://github.com/raysan5/raylib/pull/2442
* @ryupold made their first contribution in https://github.com/raysan5/raylib/pull/2449
* @lazaray made their first contribution in https://github.com/raysan5/raylib/pull/2444
* @Capital-EX made their first contribution in https://github.com/raysan5/raylib/pull/2466
* @anggape made their first contribution in https://github.com/raysan5/raylib/pull/2481
* @noodlecollie made their first contribution in https://github.com/raysan5/raylib/pull/2485
* @patm1987 made their first contribution in https://github.com/raysan5/raylib/pull/2486
* @gulrak made their first contribution in https://github.com/raysan5/raylib/pull/2446
* @naveensrinivasan made their first contribution in https://github.com/raysan5/raylib/pull/2496
* @dawranliou made their first contribution in https://github.com/raysan5/raylib/pull/2509
* @Tekkitslime made their first contribution in https://github.com/raysan5/raylib/pull/2521
* @TheTophatDemon made their first contribution in https://github.com/raysan5/raylib/pull/2525
* @quantumedbox made their first contribution in https://github.com/raysan5/raylib/pull/2536
* @hanaxar made their first contribution in https://github.com/raysan5/raylib/pull/2539
* @Bitwise101 made their first contribution in https://github.com/raysan5/raylib/pull/2559
* @CastimierDev made their first contribution in https://github.com/raysan5/raylib/pull/2570
* @MikeDX made their first contribution in https://github.com/raysan5/raylib/pull/2581
* @Timofffee made their first contribution in https://github.com/raysan5/raylib/pull/2585
* @andsiu made their first contribution in https://github.com/raysan5/raylib/pull/2587
* @evanTj made their first contribution in https://github.com/raysan5/raylib/pull/2589
* @kirigirihitomi made their first contribution in https://github.com/raysan5/raylib/pull/2591
* @MyUncle made their first contribution in https://github.com/raysan5/raylib/pull/2592
* @wiertek made their first contribution in https://github.com/raysan5/raylib/pull/2594
* @veins1 made their first contribution in https://github.com/raysan5/raylib/pull/2579
* @sDos280 made their first contribution in https://github.com/raysan5/raylib/pull/2602
* @BlueStaggo made their first contribution in https://github.com/raysan5/raylib/pull/2604
* @TheManTheMythTheGameDev made their first contribution in https://github.com/raysan5/raylib/pull/2608
* @ramiromagno made their first contribution in https://github.com/raysan5/raylib/pull/2611
* @sysrpl made their first contribution in https://github.com/raysan5/raylib/pull/2617
* @DaJobat made their first contribution in https://github.com/raysan5/raylib/pull/2620
* @archie2x made their first contribution in https://github.com/raysan5/raylib/pull/2622
* @ERmilburn02 made their first contribution in https://github.com/raysan5/raylib/pull/2627
* @SomeUnusualGames made their first contribution in https://github.com/raysan5/raylib/pull/2628

**Full Changelog**: https://github.com/raysan5/raylib/compare/4.0.0...4.2.0

---

## 4.0.0 - 2021-11-04

**raylib v4.0.0** by raysan5 - <https://github.com/raysan5/raylib/releases/tag/4.0.0>

It's been about 6 months since last raylib release and it's been **8 years since I started with this project**, what an adventure! It's time for a new release: `raylib 4.0`, **the biggest release ever** and an inflexion point for the library. Many hours have been put in this release to make it special, **many library details have been polished**: syntax, naming conventions, code comments, functions descriptions, log outputs... Almost all the issues have been closed (only 3 remain open at the moment of this writing) and some amazing new features have been added. I expect this **`raylib 4.0`** to be a long term version (LTS), stable and complete enough for any new graphic/game/tool application development.

Let's start with some numbers:

 - **+130** closed issues (for a TOTAL of **+1030**!)
 - **+550** commits since previous RELEASE
 - **+20** functions ADDED to raylib API
 - **+60** functions ADDED to rlgl API
 - **+40** functions RENAMED/REVIEWED/REDESIGNED
 - **+60** new contributors (for a TOTAL of **+275**!)
 
Highlights for `raylib 4.0`:

 - **Naming consistency and coherency**: `raylib` API has been completely reviewed to be consistent on naming conventions for data structures and functions, comments and descriptions have been reviewed, also the syntax of many symbols for consistency; some functions and structs have been renamed (i.e. `struct CharInfo` to `struct GlyphInfo`). Output log messages have been also improved to show more info to the users. Several articles have been writen in this process: [raylib_syntax analysis](https://github.com/raysan5/raylib/wiki/raylib-syntax-analysis) and [raylib API usage analysis](https://gist.github.com/raysan5/7c0c9fff1b6c19af24bb4a51b7383f1e). In general, a big polishment of the library to make it more consistent and coherent.

 - **Event Automation System**: This new _experimental_ feature has been added for future usage, it allows to **record input events and re-play them automatically**. This feature could be very useful to automatize examples testing but also for tutorials with assited game playing, in-game cinematics, speedruns, AI playing and more! Note this feature is still experimental.

 - **Custom game-loop control**: As requested by some advance users, **the game-loop control can be exposed** compiling raylib with the config flag: `SUPPORT_CUSTOM_FRAME_CONTROL`. It's intended for advance users that want to control the events polling and also the timming mechanisms of their games.

 - [**`rlgl 4.0`**](https://github.com/raysan5/raylib/blob/master/src/rlgl.h): This module has been completely **decoupled from platform layer** and raylib, now `rlgl` single-file header-only library only depends on the multiple OpenGL backends supported, even the dependency on `raymath` has been removed. Additionally, **support for OpenGL 4.3** has been added, supporting compute shaders and Shader Storage Buffer Objects (SSBO). Now `rlgl` can be used as a complete standalone portable library to wrap several OpenGL version and providing **a simple and easy-to-use pseudo-OpenGL immediate-mode API**.
 
 - [**`raymath 1.5`**](https://github.com/raysan5/raylib/blob/master/src/raymath.h): This module has been reviewed and some new conventions have been adopted to make it **more portable and self-contained**:
   - Functions are self-contained, no function use other raymath function inside, required code is directly re-implemented
   - Functions input parameters are always received by value
   - Functions use always a "result" variable for return
   - Angles are always in radians (`DEG2RAD`/`RAD2DEG` macros provided for convenience)

 - [**`raygui 3.0`**](https://github.com/raysan5/raygui): The **official raylib immediate-mode gui library** (included in `raylib/src/extras`) has been updated to a new version, embedding the icons collection and adding mulstiple improvements. It has been simplified and constrained for a better focus on its task: provide a simple and easy-to-use immediate-mode-gui library for small tools development.  

 - [**`raylib_parser`**](https://github.com/raysan5/raylib/tree/master/parser): Added **new tool to parse `raylib.h`** and tokenize its enums, structs and functions, extracting all required info (name, params, descriptions...) into custom output formats (TXT, XML, JSON...) for further processing. This tool is specially useful to **automatize bindings generation**. Hopefully, this tool will make life easier to binding creators to update their bindings for raylib 4.0 or adding new ones!

 - **Zig and Odin official support for raylib**: Those two new amazing programming languages are officially supporting raylib, `Zig` lists raylib as an [official example for C interoperatibility](https://ziglang.org/learn/samples/#c-interoperability) and Odin [officially supports raylib as a vendor library](https://github.com/odin-lang/Odin/tree/master/vendor/raylib). Both languages also have several bingings to raylib. Additionally, Zig build system supported has been added to compile raylib library and examples.

Those are some of the key features for this new release but actually there is way more! **Support for `VOX` ([MagikaVoxel](https://ephtracy.github.io/)) 3d model format** has been added, **new [raylib_game_template](https://github.com/raysan5/raylib-game-template)** repo shared, **new `EncodeDataBase64()` and `DecodeDataBase64()` functions** added, **improved HiDPI support**, new `DrawTextPro()` with support for text rotations, completely **reviewed `glTF` models loading**, added **`SeekMusicStream()` for music seeking**, many new examples and +20 examples reviewed... **hundreds of improvements and bug fixes**! Make sure to check [CHANGELOG](CHANGELOG) for a detailed list of changes! 

Undoubtely, **this is the best raylib ever**. Enjoy gamedev/tools/graphics programming! :)

---

## 3.7.0 - 2021-04-26

**raylib v3.7.0** by raysan5 - <https://github.com/raysan5/raylib/releases/tag/3.7.0>

April 2021, it's been about 4 months since last raylib release and here it is already a new one, this time with a bunch of internal redesigns and improvements. Surprisingly, on April the 8th I was awarded for a second time with the [Google Open Source Peer Bonus Award](https://opensource.googleblog.com/2021/04/announcing-first-group-of-google-open-source-peer-bonus-winners.html) for my contribution to open source world with raylib and it seems the library is getting some traction, what a better moment for a new release? Let's see what can be found in this new version:

Let's start with some numbers:

 - **+100** closed issues (for a TOTAL of **+900**!)
 - **+400** commits since previous RELEASE
 - **+50** functions ADDED (**+30** of them to rlgl API)
 - **+30** functions REVIEWED/REDESIGNED
 - **+40** new contributors (for a TOTAL of **+210**!)
 
Highlights for `raylib 3.7`:

 - **REDESIGNED: `rlgl` module for greater abstraction level**. This suppose an **important change in raylib architecture**, now `rlgl` functionality is self-contained in the module and used by higher-level layers (specially by `core` module), those upper layers are the ones that expose functionality to the main API when required, for example the `Shaders`, `Mesh` and `Materials` functionality. Multiple `rlgl` functions have been renamed for consistency, in this case, following the `rl*()` prefix convention. Functions have also been reorganized internally by categories and `GenTexture*()` functions have been removed from the library and moved to [`models_material_pbr`](https://github.com/raysan5/raylib/blob/master/examples/models/models_material_pbr.c) example.
 
 - **REDESIGNED: VR simulator and stereo rendering mechanism**. A **brand new API** has been added, more comprehensive and better integrated with raylib, the **new stereo rendering** can be combined with `RenderTexture` and `Shader` API allowing the user to **manage fbo and distortion shader directly**. Also, the new rendering mechanism supports **instancing on stereo rendering**! Check the updated [`core_vr_simulator`](https://github.com/raysan5/raylib/blob/master/examples/core/core_vr_simulator.c) example for reference!
 
 - **ADDED: New file access callbacks system**. Several new callback functions have been added to the API to allow custom file loaders. A [nice example](https://github.com/RobLoach/raylib-physfs) it's the **raylib integration with a virtual file system** [PhysFS](https://icculus.org/physfs/).
 
 - **ADDED: glTF animations support**. glTF is the preferred models file format to be used with raylib and along the addition of a models animation API on latest raylib versions, now animations support for glTF format has come to raylib, thanks for this great contribution to [Hristo Stamenov](@object71)
 
 - **ADDED: Music streaming support from memory**. raylib has been adding the `Load*FromMemory()` option to all its supported file formats but **music streaming** was not supported yet... until now. Thanks to this great contribution by [Agnis "NeZvērs" Aldiņš](@nezvers), now raylib supports music streamming from memory data for all supported file formats: WAV, OGG, MP3, FLAC, XM and MOD.
 
 - **RENAMED: enums values for consistency**. Most raylib enums names and values names have been renamed for consistency, now all value names start with the type of data they represent. It increases clarity and readability when using those values and also **improves overall library consistency**.
 
Beside those key changes, many functions have been reviewed with improvements and bug fixes, many of them contributed by the community! Thanks! And again, this release sets a **new milestone for raylib library**. Make sure to check [CHANGELOG](https://github.com/raysan5/raylib/blob/master/CHANGELOG) for detailed list of changes! Hope you enjoy this new raylib installment!

Happy **gamedev/tools/graphics** programming! :)

---

## 3.5.0 - 2020-12-25

**raylib v3.5.0** by raysan5 - <https://github.com/raysan5/raylib/releases/tag/3.5.0>

It's December 25th... this crazy 2020 is about to finish and finally the holidays gave me some time to put a new version of raylib. It's been **9 months since last release** and last November raylib become 7 years old... I was not able to release this new version back then but here it is. Many changes and improvements have happened in those months and, even, last August, raylib was awarded with an [Epic Megagrant](https://www.unrealengine.com/en-US/blog/epic-megagrants-fall-2020-update)! Bindings list kept growing to [+50 programming languages](https://github.com/raysan5/raylib/blob/master/BINDINGS.md) and some new platforms have been supported. Let's see this new version details:

First, some general numbers of this new update:

 - **+650** commits since previous RELEASE
 - **+30** functions ADDED (for a TOTAL of **475**!)
 - **+90** functions REVIEWED/REDESIGNED
 - **+30** contributors (for a TOTAL of **170**!)
 - **+8** new examples (for a TOTAL of **+120**!)
 
Here the list with some highlights for `raylib 3.5`.
 
 - NEW **Platform** supported: **Raspberry Pi 4 native mode** (no X11 windows) through [DRM](https://en.wikipedia.org/wiki/Direct_Rendering_Manager) subsystem and GBM API. Actually this is a really interesting improvement because it opens the door to raylib to support other embedded platforms (Odroid, GameShell, NanoPi...). Also worth mentioning the un-official homebrew ports of raylib for [PS4](https://github.com/orbisdev/orbisdev-orbisGl2) and [PSVita](https://github.com/psp2dev/raylib4Vita).
 
 - NEW **configuration options** exposed: For custom raylib builds, `config.h` now exposes **more than 150 flags and defines** to build raylib with only the desired features, for example, it allows to build a minimal raylib library in just some KB removing all external data filetypes supported, very useful to generate **small executables or embedded devices**.
 
 - NEW **automatic GIF recording** feature: Actually, automatic GIF recording (**CTRL+F12**) for any raylib application has been available for some versions but this feature was really slow and low-performant using an old gif library with many file-accesses. It has been replaced by a **high-performant alternative** (`msf_gif.h`) that operates directly on memory... and actually works very well! Try it out!
 
 - NEW **RenderBatch** system: `rlgl` module has been redesigned to support custom **render batches** to allow grouping draw calls as desired, previous implementation just had one default render batch. This feature has not been exposed to raylib API yet but it can be used by advance users dealing with `rlgl` directly. For example, multiple `RenderBatch` can be created for 2D sprites and 3D geometry independently.
 
 - NEW **Framebuffer** system: `rlgl` module now exposes an API for custom **Framebuffer attachments** (including cubemaps!). raylib `RenderTexture` is a basic use-case, just allowing color and depth textures, but this new API allows the creation of more advance Framebuffers with multiple attachments, like the **G-Buffers**. `GenTexture*()` functions have been redesigned to use this new API.
 
 - Improved **software rendering**: raylib `Image*()` API is intended for software rendering, for those cases when **no GPU or no Window is available**. Those functions operate directly with **multi-format** pixel data on RAM and they have been completely redesigned to be way faster, specially for small resolutions and retro-gaming. Low-end embedded devices like **microcontrollers with custom displays** could benefit of this raylib functionality!
 
 - File **loading from memory**: Multiple functions have been redesigned to load data from memory buffers **instead of directly accessing the files**, now all raylib file loading/saving goes through a couple of functions that load data into memory. This feature allows **custom virtual-file-systems** and it gives more control to the user to access data already loaded in memory (i.e. images, fonts, sounds...).
 
 - NEW **Window states** management system: raylib `core` module has been redesigned to support Window **state check and setup more easily** and also **before/after Window initialization**, `SetConfigFlags()` has been reviewed and `SetWindowState()` has been added to control Window minification, maximization, hidding, focusing, topmost and more.
 
 - NEW **GitHub Actions** CI/CD system: Previous CI implementation has been reviewed and improved a lot to support **multiple build configurations** (platforms, compilers, static/shared build) and also an **automatic deploy system** has been implemented to automatically attach the diferent generated artifacts to every new release. As the system seems to work very good, previous CI platforms (AppVeyor/TravisCI) have been removed.
 
A part of those changes, many new functions have been added, some redundant functions removed and many functions have been reviewed for consistency with the full API (function name, parameters name and order, code formatting...). Again, this release is a **great improvement for raylib and marks the way forward** for the library. Make sure to check [CHANGELOG](https://github.com/raysan5/raylib/blob/master/CHANGELOG) for details! Hope you enjoy it!

Happy holidays! :)

---

## 3.0.0 - 2020-04-01

**raylib v3.0.0** by raysan5 - <https://github.com/raysan5/raylib/releases/tag/3.0.0>

After **10 months of intense development**, new raylib version is ready. Despite primary intended as a minor release, the [CHANGELIST](CHANGELOG) has grown so big and the library has changed so much internally that it finally became a major release. Library **internal ABI** has received a big redesign and review, targeting portability, integration with other platforms and making it a perfect option for other progamming [language bindings](BINDINGS.md).

 - All **global variables** from the multiple raylib modules have been moved to a **global context state**, it has several benefits, first, better code readability with more comprehensive variables naming and categorization (organized by types, i.e. `CORE.Window.display.width`, `CORE.Input.Keyboard.currentKeyState` or `RLGL.State.modelview`). Second, it allows better memory management to load global context state dynamically when required (not at the moment), making it easy to implement a **hot-reloading mechanism** if desired.

 - All **memory allocations** on raylib and its dependencies now use `RL_MALLOC`, `RL_FREE` and similar macros. Now users can easely hook their own memory allocations mechanism if desired, having more control over memory allocated internally by the library. Additionally, it makes it easier to port the library to embedded devices where memory control is critical. For more info check raylib issue #1074.

 - All **I/O file accesses** from raylib are being moved to **memory data access**, now all I/O file access is centralized into just four functions: `LoadFileData()`, `SaveFileData()`, `LoadFileText()`, `SaveFileText()`. Users can just update those functions to any I/O file system. This change makes it easier to integrate raylib with **Virtual File Systems** or custom I/O file implementations.

 - All **raylib data structures** have been reviewed and optimized for pass-by-value usage. One of raylib distinctive design decisions is that most of its functions receive and return data by value. This design makes raylib really simple for newcomers, avoiding pointers and allowing complete access to all structures data in a simple way. The downside is that data is copied on stack every function call and that copy could be costly so, all raylib data structures have been optimized to **stay under 64 bytes** for fast copy and retrieve.

 - All **raylib tracelog messages** have been reviewd and categorized for a more comprehensive output information when developing raylib applications, now all display, input, timer, platform, auxiliar libraries, file-accesses, data loading/unloading issues are properly reported with more detailed and visual messages.

 - `raudio` module has been internally reviewed to accomodate the new `Music` structure (converted from previous pointer format) and the module has been adapted to the **highly improved** [`miniaudio v0.10`](https://github.com/dr-soft/miniaudio).

 - `text` module reviewed to **improve fonts generation** and text management functions, `Font` structure has been redesigned to better accomodate characters data, decoupling individual characters as `Image` glyphs from the font atlas parameters. Several improvements have been made to better support Unicode strings with UTF-8 encoding.

 - **Multiple new examples added** (most of them contributed by raylib users) and all examples reviewed for correct execution on most of the supported platforms, specially Web and Raspberry Pi. A detailed categorized table has been created on github for easy examples navigation and code access.

 - New **GitHub Actions CI** system has been implemented for Windows, Linux and macOS code and examples compilation on every new commit or PR to make sure library keeps stable and usable with no breaking bugs.

Note that only key changes are listed here but there is way more! About **30 new functions**, multiple functions reviewed, bindings to [+40 programming languages](https://github.com/raysan5/raylib/blob/master/BINDINGS.md) and great samples/demos/tutorials [created by the community](https://discord.gg/VkzNHUE), including raylib integration with [Spine](https://github.com/WEREMSOFT/spine-raylib-runtimes), [Unity](https://unitycoder.com/blog/2019/12/09/using-raylib-dll-in-unity/), [Tiled](https://github.com/OnACoffeeBreak/raylib_tiled_import_with_tmx), [Nuklear](http://bedroomcoders.co.uk/implementing-a-3d-gui-with-raylib/), [enet](https://github.com/nxrighthere/NetDynamics) and [more](https://github.com/raysan5/raylib/issues/1079)!

It has been **10 months of improvements** to create the best raylib ever.

Welcome to **raylib 3.0**.

---

