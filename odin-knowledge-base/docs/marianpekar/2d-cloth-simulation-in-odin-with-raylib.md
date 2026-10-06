# 2D Cloth Simulation in Odin with raylib

26th January 2025 • 23 min read

In this post, I'll walk you through the implementation of a two-dimensional cloth simulation that is based on a simple idea with [Verlet integration](https://en.wikipedia.org/wiki/Verlet_integration), written in [Odin Programming Language](https://odin-lang.org) and using [raylib](https://www.raylib.com).

In 2022, I already wrote a blog post for Gustavo Pezzi on his Pikuma blog, which goes much deeper into the underlying math principles. It covers the basics of the implementation in JavaScript before moving on to a full implementation in C++ using [SDL](https://www.libsdl.org).

Because I don't see the point in rewriting the same stuff, this post will focus mostly on the new implementation in Odin with raylib. If you're interested in learning more about Verlet integration, I recommend first reading the original post: [Verlet Integration and Cloth Physics Simulation](https://pikuma.com/blog/verlet-integration-2d-cloth-physics-simulation).

I've recently become very enthusiastic about the Odin. If you've written C or C++ before, especially if you've done so professionally, I believe Odin will get your heart, too. It really brings a lot of joy to programming.

The original C++ implementation with SDL spans across several files and has nearly 700 lines of code, while the new one takes just 200 and a few lines and fits reasonably within a single `.odin` file.

## Importing raylib, Preparing Structs, and the General Idea

Let’s now look at this implementation, and I’ll explain everything as we go. But if this is your first encounter with Odin, I highly recommend you read the [Odin documentation](https://odin-lang.org/docs/), and if you want to follow along, also [download Odin](https://odin-lang.org/docs/install/) and set up your environment, which is, with Odin, dead simple.

Once you've got everything set up and have looked at the basics of Odin, we can start writing into the `main.odin` file. After the [package](https://odin-lang.org/docs/overview/#packages) declaration and importing [raylib](https://pkg.odin-lang.org/vendor/raylib/) as `rl`, we'll declare three structs: `Point`, `Stick`, and `Cloth`.

```odin
package main 

import rl "vendor:raylib"

Point :: struct {
     pos: rl.Vector2,
     prevPos: rl.Vector2,
     initPos: rl.Vector2,
     isPinned: bool,
     isSelected: bool
}

Stick :: struct {
    p0: ^Point,
    p1: ^Point,
    isTeared: bool
}

Cloth :: struct {
    points: [dynamic]^Point,
    sticks: [dynamic]^Stick
}
```

The idea behind this cloth simulation is that we have an array of points. Each point has a position initially within a perfect grid pattern. We also have sticks to link neighbouring points to each other. The entire cloth is represented by two dynamic arrays: one with pointers to points and the other with pointers to sticks. Each stick consists of two pointers to points, representing two connected points. With all this, we:

1. Iterate over all points and apply forces to them. In our case, we'll apply gravity uniformly to all points (except for those in the first row, which will have `isPinned` set to `true`), plus we'll generate additional force based on mouse movement. The faster you move the mouse while holding the left mouse button, the stronger force will be applied to the selected points (the points covered by the cursor will have `isSelected` set to `true`). We'll make the size of the cursor adjustable, as you saw in the video above.
2. Iterate over the sticks and gradually apply corrections to maintain an equal distance between the two connected points, unless the distance is already too large, in which case we break the connection.
3. Iterate over the sticks and draw lines between the connected points to render the simulation.

## The main Procedure

Let's proceed with our main procedure (pun not intended). First, we'll initialize a borderless window and store the screen's width and height for later use. We'll also set the target FPS to 60.

```odin
main :: proc() {
    rl.InitWindow(0, 0, "Cloth Simulation 2D")
    rl.ToggleBorderlessWindowed()
    screenWidth := rl.GetScreenWidth()
    screenHeight := rl.GetScreenHeight()
    rl.SetTargetFPS(60)
```

As you can see, initializing a window with raylib is extremely simple. We'll continue with preparing constants and variables we'll soon be passing as arguments to procedures we yet need to implement, starting with those related to cloth. One of these procedures is `MakeCloth`, which we call here, but we’ll start implementing it after we finish the `main` procedure.

```odin
// Cloth
clothWidth :: 150
clothHeight :: 75
clothSpacing :: 10
startX := (screenWidth - (clothWidth * clothSpacing)) / 2
startY := screenHeight / 12

cloth := MakeCloth(clothWidth, clothHeight, clothSpacing, startX, startY)
defer {
    for &point in cloth.points {
        free(point)
    }

    for &stick in cloth.sticks {
        free(stick)
    }
}
```

Our cloth will have a width of 150 units and a height of 75 units. This sets the number of points we’ll soon be updating in a loop. That's 112,500 points (150 × 75). It might seem like a lot, but it’s well within the capabilities of a modern CPU. However, if you encounter performance issues, try cutting `clothWidth` and `clothHeight` in half.

The `spacing` determines how far apart the points will be initially. This spacing will also define the distance we maintain between points via sticks, as described earlier. As a result, the display size of our cloth will be 1500 × 750 pixels, and it will be horizontally centered and hung 1/12 of the screen's height from the top, regardless of the resolution. This is why we previously stored `screenWidth` and `screenHeight`.

After creating a cloth with the `MakeCloth` procedure, we called `free` for each item in the `cloth.points` and `cloth.sticks` arrays. This is necessary because the procedure will create points and sticks using the `new` keyword, which allocates memory on the heap. The cleanup was placed inside a `defer` scope, ensuring the entire scope is executed at the end of the parent scope. The [defer statement](https://odin-lang.org/docs/overview/#defer-statement) in the Odin language is particularly useful as it allows memory deallocations to be written immediately after allocations, reducing the risk of forgetting them.

Now, we need a few constants related to physics.

```odin
// Physics
drag :: f32(0.005)
gravity :: rl.Vector2{0, 980}
elasticity :: f32(100.0)
```

We have `drag`, and we’ll use it to slowly stop the movement of our points. There’s also `elasticity`, set to `100`, meaning that if the distance between two points exceeds 100 (the initial distance is `spacing`, which we set to `10`), the stick will break (we set `isTeared` to true). We also have the standard Earth gravitational acceleration, which varies with latitude, increasing from about 9.780 m/s² at the equator to about 9.832 m/s² at the poles.

For this simulation, we can use any value that feels right, but `980` as the `y` component of our gravity vector approximates reality and works well.

Next, we need a constant and a variable for our fixed update loop.

```odin
// Update Loop
fixedDeltaTime :: f32(1.0 / 300)
accumulator: f32 = 0.0
```

Physics simulations are generally more stable when run in loops with a fixed time step, a practice followed by most game engines. I'll explain the purpose of the `accumulator` variable in a moment. The last variable we need is the initial size of the mouse cursor.

```odin
// Interaction
cursorSize: f32 = 30.0
```

We’re near the end of the main procedure. We just need to implement a main loop that will run until we tell the program we wish to close the window, which we can do by pressing ESC, since our window was set to borderless fullscreen mode. After exiting the loop, we simply close the window.

```odin
‎ ‎ ‎ ‎ for !rl.WindowShouldClose() { 
        HandleMouseInteraction(&cloth, &cursorSize)

        accumulator += rl.GetFrameTime()
        for accumulator >= fixedDeltaTime {
            UpdateCloth(&cloth, fixedDeltaTime, clothSpacing, drag, gravity, elasticity)
            accumulator -= fixedDeltaTime            
        }

        rl.BeginDrawing()
        rl.ClearBackground({33, 40, 48, 255})
        DrawCloth(&cloth, clothSpacing, elasticity)
        rl.EndDrawing()
    }

    rl.CloseWindow()
}
```

The `HandleMouseInteraction` is another procedure we still need to implement. We'll get to it later. In the few lines before `rl.BeginDrawing()`, we’re using our `accumulator` to keep track of time as the simulation runs. Each frame, we add the time since the last frame with `rl.GetFrameTime()`. Then, as long as the accumulator has enough time to match our `fixedDeltaTime`, we process the cloth simulation by calling `UpdateCloth`. This ensures the physics updates consistently. After each update, we reduce the accumulator by `fixedDeltaTime` to prepare for the next iteration.

And finally, we call our `DrawCloth` procedure, the last one we yet need to implement, between `BeginDrawing` and `EndDrawing` from raylib. We also use `ClearBackground` to set the background color in an RGBA format. The value is arbitrary; you can choose any color you like.

As you can see, raylib has been incredibly helpful here. If you want to see more of what it can do, check out this [cheatsheet](https://www.raylib.com/cheatsheet/cheatsheet.html).

## MakeCloth

Now it's time to implement the `MakeCloth` procedure, which constructs and returns our `Cloth`.

```odin
MakeCloth :: proc(width, height, spacing, startX, startY: i32) -> Cloth {
    cloth: Cloth

    for y := i32(0); y <= height; y += 1 {
        for x := i32(0); x <= width; x += 1 {
            point := new(Point)
            point.initPos = { f32(startX + x * spacing), f32(startY + y * spacing) }
            point.pos = point.initPos
            point.prevPos = point.initPos
            point.isPinned = y == 0
            append(&cloth.points, point)

            if x != 0 {
                stick := new(Stick)
                stick.p0 = cloth.points[len(cloth.points) - 2]
                stick.p1 = cloth.points[len(cloth.points) - 1]
                append(&cloth.sticks, stick)
            }

            if y != 0 {
                stick := new(Stick)
                stick.p0 = cloth.points[(y - 1) * (width + 1) + x]
                stick.p1 = cloth.points[y * (width + 1) + x]
                append(&cloth.sticks, stick)
            }
        }
    }

    return cloth
}
```

Here, we use nested for loops to iterate over a grid of initial positions for our points. We calculate the initial position for each point based on the current `x` and `y` indices in the loop, horizontal and vertical offsets (`startX` and `startY`), and the desired`spacing` between points.

Notice how, for the points in the first row, we set `isPinned` to `true` (`point.isPinned = y == 0`). This ensures that the cloth stays suspended from the top.

As we go, we not only create points, which we [append](https://odin-lang.org/docs/overview/#appending-to-a-dynamic-array) to the `cloth.points` dynamic array, but also create sticks, which we append to the `cloth.sticks` dynamic array. However, we only create these sticks if the row (`y`) and column (`x`) are not zero. This is because we always connect a point to the one on its left and the one above it, and the first row and first column have no points to their left nor above.

## UpdateCloth

The second key procedure is `UpdateCloth`, where we apply Verlet integration to calculate the trajectory of each point. Then, we iterate over the sticks and apply corrections to push the points back to their initial positions.

```odin
UpdateCloth :: proc(cloth: ^Cloth, deltaTime: f32, spacing: i32, drag: f32, acceleration: rl.Vector2, elasticity: f32) {
    for &point in cloth.points {
        UpdatePoint(point, deltaTime, spacing, drag, acceleration)
    }

    for &stick in cloth.sticks {
        UpdateStick(stick, spacing, elasticity)
    }

    UpdatePoint :: proc(point: ^Point, deltaTime: f32, spacing: i32, drag: f32, acceleration: rl.Vector2) {
        if point.isPinned {
            point.pos = point.initPos
            return
        }

        currentPos := point.pos
        point.pos += (point.pos - point.prevPos) * (1.0 - drag) + acceleration * deltaTime * deltaTime
        point.prevPos = currentPos
    }

    UpdateStick :: proc(stick: ^Stick, spacing: i32, elasticity: f32) {
        delta := stick.p1.pos - stick.p0.pos
        distance := rl.Vector2Length(delta)

        if distance > elasticity {
            stick.isTeared = true
            return
        }

        correction: rl.Vector2 = delta * ((distance - f32(spacing)) / distance * 0.5) * 0.5

        if !stick.p0.isPinned && !stick.isTeared {
            stick.p0.pos += correction
        }

        if !stick.p1.isPinned && !stick.isTeared  {
            stick.p1.pos -= correction
        }
    }
}
```

I decided to create nested procedures, `UpdatePoint` and `UpdateStick`. When I imagine someone reading this code for the first time, they can immediately understand what's happening from the higher perspective at the top. Then, they can examine details in these two procedures separately. I see this as self-documented code and generally prefer it over comments. You might disagree, and that's perfectly fine.

In `UpdatePoint`, notice how we skip points with `isPinned` set to `true`. For these points, we simply make sure their position remains the same.

The following three lines capture the gist of Verlet integration. First, we cache the current position of the point. Then, we calculate the difference between the current position and the previous position, multiplying it by a value slightly less than 1.0 (`1.0 - drag`) to gradually slow any movement over time, bringing it back to rest. Next, we add `acceleration` multiplied by the square of our fixed `deltaTime`, which gives us the new position for the point we immediately set to it. Finally, we set the previous position of the point cached in the `currentPos` variable.

In `UpdateStick`, we first calculate the distance between the points associated with the stick. If it exceeds the `elasticity`, we set `isTeared` to `true` and return from the procedure early.

Otherwise, we calculate the correction by multiplying the delta between the points by the difference between the `distance` and the `spacing`, divided by half of that distance. This result is then multiplied by `0.5`to avoid applying the correction too drastically. Applying only half in each update increases the stability of the simulation. Finally, we apply the correction to the points associated with sticks that are not torn; in the positive direction for the first point (`p0`) and in the negative direction for the second point (`p1`).

## DrawCloth

At this point, our simulation is complete, but we won't see any cloth unless we draw it. This will be the responsibility of the `DrawCloth` procedure.

```odin
DrawCloth :: proc(cloth: ^Cloth, spacing: int, elasticity: f32) {
    for &stick in cloth.sticks {
        DrawStick(stick, spacing, elasticity)
    }

    DrawStick :: proc(stick: ^Stick, spacing: int, elasticity: f32) {
        if (stick.isTeared) {
            return
        }

        distance := rl.Vector2Distance(stick.p0.pos, stick.p1.pos)
        color := stick.p0.isSelected || stick.p1.isSelected ? rl.BLUE : GetColorFromTension(distance, elasticity, spacing)
        rl.DrawLineV(stick.p0.pos, stick.p1.pos, color)
    }
}
```

It's fairly straightforward. We iterate over all the sticks and use raylib to draw a line from `p0` to `p1` from each stick. Just when the stick is actually torn, we skip the drawing by returning early from the nested `DrawStick` procedure.

As for the line color, in [the original C++/SDL implementation](https://github.com/marianpekar/cloth-simulation-2d) from 2022, the sticks were blue by default, and the selected ones were red. This time, I decided to calculate the color based on tension. To achieve that, we need to implement the `GetColorFromTension` procedure.

## GetColorFromTension

This procedure accepts `distance`, `elasticity`, and `spacing` between points, and returns a color sampled from a gradient that goes from green, over yellow, to red.

```odin
GetColorFromTension :: proc(distance: f32, elasticity: f32, spacing: int) -> rl.Color {
    if distance <= f32(spacing) {
        return {
             44,
            222,
            130,
            255
        } // Green
    } else if distance <= f32(spacing) * 1.33 {
        t := (distance - f32(spacing)) / (f32(spacing) * 0.33)
        return {
            Lerp(44,  255, t),
            Lerp(222, 255, t),
            Lerp(130,   0, t),
            255
        } // Gradual transition to yellow
    } else {
        t := (distance - f32(spacing) * 1.33) / (elasticity - f32(spacing) * 1.33)
        return {
            Lerp(255, 222, t),
            Lerp(255,  44, t),
            Lerp(0,    44, t),
            255
        } // Gradual transition to red
    }

    Lerp :: proc(a: f32, b: f32, t: f32) -> u8 {
        return u8(a + ((b - a) * t))
    }
}
```

At the bottom, we have a small helper function for [linear interpolation](https://en.wikipedia.org/wiki/Linear_interpolation) between two floats. While there is a `lerp` procedure in the `core:math` library, I decided to include a custom one since it's a very simple procedure, and this is an educational post.

The rest of this procedure uses `Lerp` and branching to sample a color from the green-yellow-red gradient in RGBA space, based on the deviation from initial spacing and elasticity. The numbers are adjusted so it feels right; when points are relatively still and maintain a distance close or the same as the spacing, the sticks are green. As they diverge, the color transitions to yellow, and if they diverge even more, it shifts through orange to red, just before disappearing as the sticks tear.

## HandleMouseInteraction

If you comment out the `HandleMouseInteraction` procedure in the `main`, you can type `odin run .` in the terminal within the same directory where `main.odin` resides, and you'll see the cloth rendered, but it will just hang there. That’s quite boring. So, let’s implement the `HandleMouseInteraction` procedure to make it more fun.

```odin
HandleMouseInteraction :: proc(cloth: ^Cloth, cursorSize: ^f32) {
    SetCursorSize(cursorSize)
    InteractWithPoints(cloth, cursorSize)

    SetCursorSize :: proc(cursorSize: ^f32) {
        stepSize :: 5
        if rl.GetMouseWheelMove() > 0 {
            cursorSize^ += stepSize 
        } else if rl.GetMouseWheelMove() < 0 && !(cursorSize^ <= stepSize) {
            cursorSize^ -= stepSize
        }
    }

    InteractWithPoints :: proc(cloth: ^Cloth, cursorSize: ^f32) {
        @(static)prevMousePos : rl.Vector2

        mousePos   := rl.GetMousePosition()
        maxDelta   := rl.Vector2(100)
        mouseDelta := rl.Vector2Clamp(mousePos - prevMousePos, rl.Vector2(0), maxDelta)

        for &point in cloth.points {
            distance := rl.Vector2Distance(mousePos, point.pos)
            if distance < cursorSize^ {

                if rl.IsMouseButtonDown(.LEFT) {
                    // Drag selected points
                    point.prevPos = point.prevPos + mouseDelta
                    point.pos = point.pos + mouseDelta
                }

                point.isSelected = true
            }
            else {
                point.isSelected = false
            }
        }

        prevMousePos = mousePos 
    }
}
```

The interaction is divided into two phases. First, we adjust the cursor size by scrolling the mouse wheel. Each scroll up increases and scroll down decreases the radius by 5 units (`stepSize`), except when the radius is 5 units exactly. In that case, we don't allow it to be scaled down any further. Notice we passed the `cursorSize` to the `SetCursorSize` procedure by reference.

In the `InteractWithPoints` procedure, we calculate the distance between the mouse position and the position of each point. If the distance is smaller than the cursor size, we set `isSelected` to `true` for that point; otherwise, we set it to `false`. This effectively makes all the points under the circle-shaped cursor selected (and we draw associated sticks in blue color).

We also use raylib to check if the left mouse button is pressed, and if so, we move the points by adding the `mouseDelta` to both their current and previous positions. The `mouseDelta` is just a difference between the current and previous mouse position, which we declared as `static` at the beginning of the procedure, and we set it to the current mouse position at the end.

That means the faster we move the mouse while holding the left mouse button, the farther the selected points will move, and the more rapidly they will be corrected in the `UpdateCloth` procedure, or the sticks may eventually tear if their distance exceeds the elasticity.

Notice that this delta is clamped between `[0, 0]` and `[100, 100]`. This also increases the stability of our simulation, as it could become unstable if the points were moved too much in one go.

## Conclusion

And that's it, just about 200 lines of Odin with raylib, and that makes the entire simulation. As usual, you can find [the implementation on GitHub](https://github.com/marianpekar/cloth-simulation-2d-odin/blob/main/main.odin). There is still room for improvement in both performance and stability. For example, different kinds of integrations can be used, or to significantly increase stability, you can place `UpdateCloth` inside a for loop to update it twice or more times. However, this approach comes at the high cost of reduced performance.

> Author: Marian Pekar - <https://marianpekar.com>
> (c) Marian Pekar. The posts stay freely readable on the author's site; this local copy is credited in `SOURCES.md` at the repo root. Please link back to the original article.

>Source: https://marianpekar.com/blog/2d-cloth-simulation-in-odin-with-raylib
