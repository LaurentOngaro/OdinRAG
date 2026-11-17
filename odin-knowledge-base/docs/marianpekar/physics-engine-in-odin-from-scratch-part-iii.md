---
title: "Physics Engine in Odin from Scratch, Part III"
date: 2026-06-20
source: "https://marianpekar.com/blog/physics-engine-in-odin-from-scratch-part-iii"
tags: [OdinRAG, kb, source/marianpekar, topic/collision]
type: reference
status: active
---

# Physics Engine in Odin from Scratch, Part III

20th June 2026 • 9 min read

In the previous part, we've laid a theoretical foundation as we talked about Newtonian physics, the basics of calculus, and built a very simple physics simulation in a few lines of code, with just a single particle, no collision. Today, we're going back to our original project. We're going to add a new file, `physics.odin`, with the `RigidBody` struct and the first physics simulation procedures: `ApplyPhysics`, `ApplyGravity`, and `IntegrateLinearForce`. We'll call the last two from `ApplyPhysics` for each model that is not static.

At the end of this part, our cubes will fall under the influence of gravity. We'll have a solid fixed-time physics loop in the `main.odin` file, and we'll be ready for the next part, where we tackle collisions. All code in this part is based on the theoretical foundation from the previous part, so let's jump straight into coding.

First, let's add a few constants that we need today to our `constants.odin` file.

```odin
PHYSICS_TIMESTEP :: 1.0 / 60.0
GRAVITY :: Vector3{0.0, -9.8, 0.0}
LINEAR_DRAG :: f32(0.98)
```

The first one we're going to use for our fixed-time physics update loop. We're going to set it to run 60 times per second; in other words, the positions of all objects will be updated based on forces applied to them every 16.6 ms (1.0 / 60.0 = 0.0166)

The acceleration of gravity on Earth is ~9.8 m⋅s⁻², and in our coordinate system, the Y axis is pointing up in the positive direction. We naturally want our objects to be pulled down by gravity, hence the value `Vector3{0.0, -9.8, 0.0}`.

And finally, `LINEAR_DRAG` is a number we're going to multiply the velocity of our objects every iteration of that fixed-time physics loop. Since it's the number smaller than 1.0, it effectively "cuts off" 2% (1.0 - 0.98 = 0.02) of the velocity every update. We've seen that in action in the previous part, where we named this constant in our simple simulation as `DAMPING`. We named the constant `LINEAR_DRAG` instead of naming it simply `DRAG` because we'll add `ANGULAR_DRAG` once we get to angular movement.

Now, add a new file into the project and name it `physics.odin`. We're going to write many more lines of code into this file in the upcoming parts. In this file, after the usual package definition, add a new struct named `RigidBody`, for now with just `force` (a force accumulator for a particular object with a rigidbody), `velocity`, and a flag we're going to call `isStatic`.

```odin
package main

RigidBody :: struct {
  force:    Vector3,
  velocity: Vector3,
  isStatic: bool,
}
```

There will be a lot more members in this struct later, for example, `torque` and `angularVelocity`, once we start adding rotations. In some older games, i.e., Half-Life, you can push some crates, and they fall when you push them over an edge, but then never rotate along any axis. A few years later, before Half-Life 2 came out in late 2004, I remember how absolutely astonished I was by a [tech demo](https://www.youtube.com/watch?v=CaHtOISsLT4&t=126s) where developers presented very realistic physics from the upcoming sequel. At first, our physics simulation will be more like the first Half-Life. Later, we'll add rotations and other cool features as well.

Now let's add the `ApplyPhysics` procedure, sort of an entry point for the entire simulation. In this procedure, we iterate over all objects and call `ApplyGravity` and `IntegrateLinearForce`, procedures we need to implement, when the current object is not static. Later, we'll use the biggest static cube as a floor to prevent our objects from falling into a void.

```odin
ApplyPhysics :: proc(models: []Model, deltaTime: f32) {
    for &model in models {
        if model.rigidBody.isStatic do continue

        ApplyGravity(&model, deltaTime)
        IntegrateLinearForce(&model, deltaTime)
    }
}
```

The `ApplyGravity` is almost embarrassingly simple (this is not a technical term, unlike _embarrassingly parallel_, which surprisingly is).

```odin
ApplyGravity :: proc(model: ^Model, deltaTime: f32) {
    model.rigidBody.velocity += GRAVITY * deltaTime
}
```

Again, this should be obvious to you now from the previous part, which I hope you didn't skip. The last procedure we'll implement today in `physics.odin` should also make sense to you. It's the procedure for integrating the accumulated forces and velocity to update the model's position. Very similar to what we've done in the previous part.

```odin
IntegrateLinearForce :: proc(model: ^Model, deltaTime: f32) {
    model.rigidBody.velocity += model.rigidBody.force * deltaTime
    model.rigidBody.force = {}
    model.rigidBody.velocity *= LINEAR_DRAG
    model.translation += model.rigidBody.velocity * deltaTime
}
```

Notice that after we integrate the force into velocity, we zero out the accumulator and apply linear drag to velocity before updating the position. We also don't have mass, but this implementation works, assuming every object has a mass of 1.0. We're going to add mass to `RidigBody` later, so as the friction.

Now, before we wrap up today's rather shorter and simpler part, let's quickly add rigidbody into our Model struct in the `model.odin` file.

```odin
Model :: struct {
    mesh: Mesh,
    texture: Texture,
    color: rl.Color,
    wireColor: rl.Color,
    translation: Vector3,
    rotationMatrix: Matrix4x4,
    scale: f32,
    rigidBody: RigidBody // this is new
}
```

With that done, in the `main.odin`, right after we create `cubeFloor`, set the `isStatic` flag of its `rigidBody` to `true`.

```odin
cubeFloor.rigidBody.isStatic = true
```

And before our final change in the `main.odin` file for today, let's also adjust the `HandleInputs` procedure in the `inputs.odin` file. In Part V, we'll have a different way of selecting objects with the mouse. For now, we're just going to strip `modelIdx` and `modelCount` from the arguments, and the part where we use up and down arrow keys to cycle through models. After these adjustments, our `HandleInputs` procedure will look like this:

```odin
// modelIdx and modelCount were removed
HandleInputs :: proc(
    model: ^Model,
    renderMode: ^i8, renderModesCount: i8,
    projType: ^ProjectionType,
    deltaTime: f32
) {
    linearStep: f32 = (rl.IsKeyDown(rl.KeyboardKey.LEFT_SHIFT) ? 0.25 : 1) * deltaTime

    if rl.IsKeyDown(rl.KeyboardKey.W) do model.translation.z += linearStep
    if rl.IsKeyDown(rl.KeyboardKey.S) do model.translation.z -= linearStep
    if rl.IsKeyDown(rl.KeyboardKey.A) do model.translation.x += linearStep
    if rl.IsKeyDown(rl.KeyboardKey.D) do model.translation.x -= linearStep
    if rl.IsKeyDown(rl.KeyboardKey.E) do model.translation.y += linearStep
    if rl.IsKeyDown(rl.KeyboardKey.Q) do model.translation.y -= linearStep

    if rl.IsKeyDown(rl.KeyboardKey.KP_ADD) do model.scale += linearStep
    if rl.IsKeyDown(rl.KeyboardKey.KP_SUBTRACT) do model.scale -= linearStep

    if rl.IsKeyPressed(rl.KeyboardKey.LEFT) {
        renderMode^ = (renderMode^ + renderModesCount - 1) % renderModesCount
    } else if rl.IsKeyPressed(rl.KeyboardKey.RIGHT) {
        renderMode^ = (renderMode^ + 1) % renderModesCount
    }

    if rl.IsKeyPressed(rl.KeyboardKey.KP_0) {
        projType^ = .Perspective
    }
    if rl.IsKeyPressed(rl.KeyboardKey.KP_1) {
        projType^ = .Orthographic
    }

    // The rest of the procedure was removed
}
```

Later, we'll change the `HandleInputs` procedure even more. Next, in the `main.odin` right before the main loop that starts with `for rl.WindowsShouldClose()` remove `selectedModelIdx` and `modelCount` and instead, after `selectedModel,` define a new variable for accumulating delta time.

```odin
physicsAccumulator: f32
```

Now, inside the main loop, fix the call of the `HandleInputs` procedure by removing non-existent parameters `ModelIdx` and `modelCount`. Then, right after this call, let's finally implement that fixed-time physics update loop.

```odin
physicsAccumulator += deltaTime
for physicsAccumulator >= PHYSICS_TIMESTEP {
    ApplyPhysics(models, PHYSICS_TIMESTEP)
    physicsAccumulator -= PHYSICS_TIMESTEP
}
```

We defined `PHYSICS_TIMESTEP` as 1.0 / 60.0 in `constants.odin`, or 0.0166, so every frame, and now I'm talking about the outer loop, we add delta time, the time it took to run one entire step of our application, where we now do both physics and rendering to `physicsAccumulator`. But the for loop where we apply physics only runs when `physicsAccumulator` is bigger than or equal to `PHYSICS_TIMESTEP`, and by subtracting `PHYSICS_TIMESTEP` from the `physicsAccumulator` at the end of the inner loop, we make sure our physics simulation runs at discreet timesteps with equal size, which is also why we pass `PHYSICS_TIMESTEP` as deltatime to the `ApplyPhysics` procedure. This is a classic fixed-timestep accumulator pattern.

The last thing we need to do is apply transformations to all models in each frame, because now with physics, they could potentially all change their position and not just the selected one, as that was the case in the original software renderer implementation, where we were able to move, rotate, and scale only the selected object. So, instead of calling `ApplyTransformations` for all models outside the main loop and only for the selected inside the main loop, remove the `ApplyTransformations(selectedModel, camera)` call and instead, move to its former place from the outside of the main loop, that short loop where we apply transformations for all models.

To avoid any confusion, here's what the part of the implementation in `main.odin` around the beginning of the main loop should look like after all these changes.

```odin
selectedModel := &models[0]
physicsAccumulator: f32

for !rl.WindowShouldClose() {
    deltaTime := rl.GetFrameTime()

    HandleInputs(selectedModel, &renderMode, renderModesCount, &projectionType, deltaTime)

    physicsAccumulator += deltaTime
    for physicsAccumulator >= PHYSICS_TIMESTEP {
        ApplyPhysics(models, PHYSICS_TIMESTEP)
        physicsAccumulator -= PHYSICS_TIMESTEP
    }

    for &model in models {
        ApplyTransformations(&model, camera)
    }
```

If you now compile and run the program (`odin run . -o:speed`). You should see the medium and small cubes fall and pass through the biggest one, which is static, just as in the video below. They pass through because we still need to implement collisions, or to be more precise, _collision detection and resolution_, which we're going to learn about in the next part.

[](/uploads/phys_eng_iii_gravity_no_collision.mp4)

Until then, you can test your understanding of this and the previous part by implementing a wind, strong enough to push falling boxes to the side (but don't just change the value of the `GRAVITY` constant).

If something doesn't work as expected, you can always compare your implementation with the implementation for the corresponding part in [this GitHub repository](https://github.com/marianpekar/software-renderer-with-physics-odin-tutorials).

## Other Parts of This Series

- [Physics Engine in Odin from Scratch, Part I](physics-engine-in-odin-from-scratch-part-i)
- [Physics Engine in Odin from Scratch, Part II](physics-engine-in-odin-from-scratch-part-ii)
- Physics Engine in Odin from Scratch, Part III
- [Physics Engine in Odin from Scratch, Part IV](physics-engine-in-odin-from-scratch-part-iv)
- [Physics Engine in Odin from Scratch, Part V](physics-engine-in-odin-from-scratch-part-v)
- [Physics Engine in Odin from Scratch, Part VI](physics-engine-in-odin-from-scratch-part-vi)

> Author: Marian Pekar - <https://marianpekar.com>
> (c) Marian Pekar. The posts stay freely readable on the author's site; this local copy is credited in `SOURCES.md` at the repo root. Please link back to the original article.

> Source: https://marianpekar.com/blog/physics-engine-in-odin-from-scratch-part-iii
