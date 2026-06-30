// Minimal Odin + Raylib example that opens window and lets you control a
// rectangle using the arrow keys. Beginners can use this as a starting point.
//
// Copy this into a file called whatever_you_want.odin inside an empty folder.
// Use the command prompt to navigate to that folder and run:
// odin run .
// Note the period, with a space before it! This should run this minimal example.
package raylib_minimal

import rl "vendor:raylib"
import "core:math/linalg"

main :: proc() {
	rl.SetConfigFlags({.VSYNC_HINT})
	rl.InitWindow(1280, 720, "Raylib Minimal")

	// This just makes sure your battery doesn't drain too fast in case VSYNC
	// is forced off.
	rl.SetTargetFPS(500)

	// rl.Vector2 is equivalent to `[2]f32`. Meaning it is a fixed array of two
	// floating point numbers.
	pos := rl.Vector2 { 200, 200 }
	size := rl.Vector2 { 20, 20 }

	for !rl.WindowShouldClose() {
		dt := rl.GetFrameTime()
		movement: rl.Vector2

		// These check if the key is held. There are also IsKeyPressed and
		// IsKeyReleassed, which are only true on the frame when that happaned.
		//
		// Open `<odin>/vendor/raylib/raylib.odin` and to see all the input-
		// related procedures.
		if rl.IsKeyDown(.UP) { movement.y -= 1 }
		if rl.IsKeyDown(.DOWN) { movement.y += 1 }
		if rl.IsKeyDown(.LEFT) { movement.x -= 1 }
		if rl.IsKeyDown(.RIGHT) { movement.x += 1 }

		// normalize0 makes sure length of movement is 1 (so you don't move
		// faster when going diagonally).
		// 
		// Note that normalize0 takes a vector and returns a new vector. We then
		// multiply that vector by `400` and `dt`, producing another vector.
		// Then that whole vector is added to `pos`.
		pos += linalg.normalize0(movement) * 400 * dt

		// For the curious person:
		//
		// (Sublime Text) Check out what normalize0 does:
		// * add `<odin>/core` to your project (drag n drop core folder into sublime)
		// * put text cursor on `normalize0` and press F12
		//
		// More info on how to "find things in core" in this video:
		// https://www.youtube.com/watch?v=mljzCWnvWCs

		// You must have Begin/End drawing. EndDrawing in particular is the
		// thing in raylib that processes input so stuff like `rl.IsKeyDown` works.
		rl.BeginDrawing()
		rl.ClearBackground(rl.DARKBLUE)
		rl.DrawRectangleV(pos, size, rl.WHITE)
		rl.EndDrawing()
	}

	rl.CloseWindow()
}