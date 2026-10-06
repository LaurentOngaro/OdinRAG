# Physics Engine in Odin from Scratch, Part VI

23rd September 2026 • 19 min read

In the sixth part, we'll add *mass*, *friction*, and *bounciness* to our physics simulation as properties of the `Rigidbody` struct. However, that would make this part quite short, so we'll make the rigidbody optional by changing its type in the `Model` struct from `Rigidbody` to `Maybe(Rigidbody)`. `Maybe(T)` is a union that either returns a type `T` or `nil`, as you can read in [Odin Docs](https://odin-lang.org/docs/overview/#maybet).

Later, we'll make `collider` optional too, but not with `Maybe(T)`. Since `BoxCollider` is an alias for `Vector3`, representing a box, and `SphereCollider` will be an alias for `f32`, representing a sphere radius, the `Collider` union will be able to contain either a `Vector3`, `f32`, or be `nil`.

Before we start talking more about *mass*, *friction*, and *bounciness*, let's first make rigidbody optional as described in the previous paragraph. Go to `model.odin` and change the type of the `rigidBody` to `Maybe(RigidBody)`.

```odin
Model :: struct {
    // ...
    rigidBody: Maybe(RigidBody),
    // ...
}
```

This change broke our implementation in a few places. While fixing it, we'll make the rigidbody truly optional, and models we don't add a rigidbody to will stay static. We'll implement a procedure for that, but first, in the `LoadModel` procedure, set `rigidBody` explicitly to `nil`.

```odin
LoadModel :: proc(meshPath: string, texturePath: cstring, color: rl.Color = rl.WHITE, wireColor: rl.Color = rl.GREEN) -> Model {
    return Model{
        // ...
        rigidBody = nil
        // ...
    }
}
```

Now, in `physics.odin`, we need to check in the `AddForceAtPoint` procedure whether a model has a rigidbody and return early if it doesn't.

```odin
AddForceAtPoint :: proc(model: ^Model, force: Vector3) {
    rb, has_rb := &model.rigidBody.(RigidBody)
    if !has_rb do return

    rb.force += force
}
```

As you can see, the pattern is simple; the `.(T)` call on `Maybe(T)` returns a tuple. The first value of this tuple is a pointer to an instance of T, since we used the & operator, and the second value is a bool that is set to `true` if the pointer is not `nil`. You might be wondering now why we couldn't do something like this instead:

```odin
rb := &model.rigidBody.(RigidBody)
if rb == nil do return
```

After all, such null checks are common in C++ and other languages. Though this would compile, it's not how `Maybe(T)` union works. We'd end up with the following runtime error, and our simulation would crash.

```odin
physics.odin(13:7) type assertion: Invalid type assertion from Maybe($T=RigidBody) to RigidBody
```

Line 13 is where we try to assign to `rb`. As you can see, the program doesn't even make it to the null check. So how about something like this instead?

```odin
rb := &model.rigidBody
if rb == nil do return
```

Again, this won't work, and this time, it won't even compile because on the following line where we try to add force to `rb.force`, we get a compile-time error:

```odin
physics.odin(16:5) Error: 'rb' of type '^Maybe($T=RigidBody)' has no field 'force' 
        rb.force += force 
        ^^
```

I think these examples of run-time and compile-time errors should help you solidify the knowledge of how `Maybe(T)` union works. Now, let's make a similar fix in the `ApplyPhysics` procedure:

```odin
ApplyPhysics :: proc(models: []Model, deltaTime: f32) {
    for &model in models {
        rb, has_rb := model.rigidBody.?
        if !has_rb || rb.isStatic do continue

        // ...
    }
}
```

In this case, instead of `.(RigidBody)` we wrote just `.?`, which is a syntactic shorthand that produces the same effect. I wanted to show you both syntaxes, but with `Maybe(T)` the `.?` might be more appropriate. Specifying the type explicitly will be important for us later, when we'll have that union of `BoxCollider` and `SphereCollider`. *Don't forget that `Maybe(T)` itself is a union*.

The last fixes in the `physics.odin` file are needed in the `ApplyGravity` and `IntegrateLinearForce` procedures, but since we already checked the presence of a rigidbody in the caller, the `ApplyPhysics` procedure, we don't need to check again. Every model that is passed to `ApplyGravity` and `IntegrateLinearForce` must have a rigidbody and thus is not static.

```odin
ApplyGravity :: proc(model: ^Model, deltaTime: f32) {
    rb := &model.rigidBody.(RigidBody)
    rb.velocity += GRAVITY * deltaTime
}

IntegrateLinearForce :: proc(model: ^Model, deltaTime: f32) {
    rb := &model.rigidBody.(RigidBody)
    rb.velocity += rb.force * deltaTime
    rb.force = {}
    rb.velocity *= LINEAR_DRAG
    model.translation += rb.velocity * deltaTime
}
```

Let's now hop over to the `collisions.odin` file to make similar changes. In the `ResolveCollisions` procedure, we check if the rigidbodies of both models are static, or if one of their colliders is too small, and if that's the case, we continue to the next pair. We now also need to check if both models have a rigidbody. We can also replace the original two if statements with just one:

```odin
rba, has_rba := a.rigidBody.?
rbb, has_rbb := b.rigidBody.?
if (!has_rba || rba.isStatic) && (!has_rbb || rbb.isStatic) || 
    (a.collider.x * a.collider.y * a.collider.z < 1e-6 || b.collider.x * b.collider.y * b.collider.z < 1e-6) {
        continue
    }
```

And the same pattern goes into`Correct` and `Push` procedures, which concludes all changes in the `collision.odin` file.

```odin
Correct :: proc(a, b: ^Model, result: CollisionResult) {
        correction := result.normal * max(result.depth, 0.0)

        rba, has_rba := a.rigidBody.?
        rbb, has_rbb := b.rigidBody.?

        if (has_rba && !a.rigidBody.?.isStatic) && (has_rbb && !b.rigidBody.?.isStatic) {
            a.translation -= correction * 0.5
            b.translation += correction * 0.5
        } else if !has_rba || !a.rigidBody.?.isStatic {
            a.translation -= correction
        } else if !has_rbb || !b.rigidBody.?.isStatic {
            b.translation += correction
        }
    }

Push :: proc(model: ^Model, normal: Vector3) {
    rb, has_rb := &model.rigidBody.(RigidBody)
    if !has_rb || rb.isStatic do return

    rb.velocity -= Vector3DotProduct(rb.velocity, normal) * normal
}
```

In the `inputs.odin` file, we just need to fix a few lines at the bottom of the `HandleInputs` procedure, where we flip the `isStatic` property of a rigidbody. Again, with the same pattern:

```odin
rb, has_rb := &ray.model.rigidBody.(RigidBody)
if has_rb {
    rb.isStatic = !rb.isStatic
}
```

Let's now quickly hop back to the `model.odin` file to implement the `AddRigidbody` procedure. Since our ridigbody is now optional, we'll have to call this procedure from main for all objects we'd like to make in our physics simulation dynamic.

```odin
AddRigidbody :: proc(model: ^Model, isStatic: bool = false) {
    model.rigidBody = RigidBody{
        isStatic = isStatic
    }
}
```

Later in this part we're going to extend this procedure, but now let's go to `main.odin` remove `cubeFloor.rigidBody.isStatic = true` line and use the `AddRigidbody` procedure to add rigidbodies to `cubeL` and `cubeM`.

```odin
AddRigidbody(&cubeM)
AddRigidbody(&cubeL)
```

If you now compile and run our simulation (`odin run . -o:speed`), everything should work as before, with one small difference. The `cubeFloor`, the biggest cube at the bottom, is static and can't be switched to a non-static state because it doesn't have a rigidbody. If you want this cube to start as static, but you still want to be able to unfreeze it with the middle mouse button, you need to add another `AddRigidbody` procedure call, but this time with the `isStatic` parameter, which is false by default, set to true. This is optional:

```odin
AddRigidbody(&cubeFloor, isStatic = true)
```

I like to name the parameter explicitly here, so it's immediately clear what's being set to true, without having to check the signature.

Now we can proceed to add mass, friction, and bounciness to our physics simulation. You'll see it's a surprisingly simple task. First we need to add `massInverse`, `friction`, and `bounciness` to our `Rigidbody` struct:

```odin
RigidBody :: struct {
    force: Vector3,
    velocity: Vector3,
    isStatic: bool,
    bounciness: f32,
    friction: f32,
    massInverse: f32
}
```

And in the `model.odin` file, we can now extend the `AddRigidbody` procedure to set these properties. Let's use default values in the signature, so we can still call the procedure with just a reference to a model.

```odin
AddRigidbody :: proc(model: ^Model, isStatic: bool = false, bounciness: f32 = 1.0, friction: f32 = 0.5, mass: f32 = 1.0) {
    model.rigidBody = RigidBody{
        massInverse = 1.0 / mass,
        bounciness = bounciness,
        friction = friction,
        isStatic = isStatic
    }
}
```

You might be asking now why we're storing the inverse of the mass; that's calculated as 1.0 divided by mass. That's a good question, and I'll give you the answer right after the next step. Go to `physics.odin` and in the `IntegrateLinearForce` procedure replace the `rb.velocity += rb.force * deltaTime` with the following line.

```odin
rb.velocity += rb.force * rb.massInverse * deltaTime
```

And that's all we need to make mass affect the acceleration caused by forces. In fact, we had mass in our simulation all along; we just treated all objects as if they all had the same mass of 1.0. Remember the equations from the [Part II](https://marianpekar.com/blog/physics-engine-in-odin-from-scratch-part-ii) of this series:

F = ma

\displaystyle a = \frac{\Delta v}{\Delta t}

By storing `massInverse` instead of mass, we make the `IntegrateLinearForce` procedure more efficient. With `mass` we'd have to do this instead: `rb.velocity += rb.force * (1.0 / rb.mass) * deltaTime`. Since `IntegrateLinearForce` is a "hot" procedure we call every frame, and `AddRigidbody` is a "cold" one, we call it only once. Yes, a compiler can optimize a lot (that's why we compile with `-o:speed` flag); but when you can optimize yourself, do that. Take control and don't expect the compiler to solve all performance issues for you. It's your code.

Adding friction is a little bit more complicated, but not much. Before applying friction, we first need to check if any object is below the one we want to adjust forces on. We're going to use raycasting to cast a ray downward from the center of our model, far enough to reach its bottom plus a small probe distance. If there's a hit, we can use the model that was hit to determine the friction of the surface underneath. In the next part of this series, we'll use a slightly different approach for this check, but for now a simple raycast is sufficient.

However, our `CastRay` procedure expects screen positions. We'll have to refactor raycasting a bit. From the `CastRay` procedure, cut the core logic into its own procedure and name it `CastRayFromWorldPosition`:

```odin
CastRayFromWorldPosition :: proc(origin: Vector3, direction: Vector3, models: []Model, maxLenght: f32 = max(f32), ignore: ^Model = nil) -> Ray {
    ray: Ray
    ray.direction = direction
    closestDist := max(f32)

    for &model in models {
        if &model == ignore do continue

        center := model.translation
        delta := center - origin

        axes := GetAxesFromRotationMatrix(model.rotationMatrix)
        size := model.collider * model.scale

        tMin :=  f32(0)
        tMax :=  maxLenght
        hit := true

        for i in 0..<3 {
            axis := axes[i]
            e := Vector3DotProduct(axis, delta)
            f := Vector3DotProduct(axis, ray.direction)

            if abs(f) < 1e-6 {
                if e < -size[i] || e > size[i] {
                    hit = false
                    break
                }
                continue
            }

            t1 := (e + size[i]) / f
            t2 := (e - size[i]) / f

            if t1 > t2 {
                t1, t2 = t2, t1 
            }

            tMin = max(tMin, t1)
            tMax = min(tMax, t2)

            if tMin > tMax {
                hit = false
                break
            }
        }

        if hit && tMin < closestDist {
            closestDist = tMin
            ray.hit = true
            ray.direction = direction
            ray.model = &model
        }
    }

    return ray
}
```

Notice we also added the `ignore` parameter. This will be used later to prevent the model from which position we'll cast a ray to be returned as the first hit. Now call `CastRayFromWorldPosition`, where the core logic was previously implemented in `CastRay`. I'd also suggest renaming `CastRay` to `CastRayFromScreenPosition`:

```odin
CastRayFromScreenPosition :: proc(screenX, screenY: f32, camera: Camera, projType: ProjectionType, models: []Model) -> Ray {
    ndcX := (screenX / f32(SCREEN_WIDTH)) * 2.0 - 1.0
    ndcY := (screenY / f32(SCREEN_HEIGHT)) * 2.0 - 1.0

    rayOrigin := GetRayOrigin(ndcX, ndcY, camera, projType)
    rayDirection := GetRayDirection(ndcX, ndcY, camera, projType)
    ray := CastRayFromWorldPosition(rayOrigin, rayDirection, models)

    return ray

    GetRayOrigin :: proc(ndcX, ndcY: f32, camera: Camera, projType: ProjectionType) -> Vector3 {
        if projType == .Perspective do return camera.position

        aspect := f32(SCREEN_WIDTH) / f32(SCREEN_HEIGHT)
        return camera.position + camera.right * (ndcX * aspect) + camera.up * (-ndcY)
    }

    GetRayDirection :: proc(ndcX, ndcY: f32, camera: Camera, projType: ProjectionType) -> Vector3 {
        if projType == .Orthographic do return camera.forward

        aspect := f32(SCREEN_WIDTH) / f32(SCREEN_HEIGHT)
        tanHalfFov := math.tan_f32(FOV * 0.5 * DEG_TO_RAD)

        return Vector3Normalize (
            camera.forward +
            camera.right * (ndcX * aspect * tanHalfFov) +
            camera.up * (-ndcY * tanHalfFov)
        )
    }
}
```

Since we renamed the procedure, we also need to go back to `inputs.odin` and fix the call at the bottom of `HandleInputs`. Now we can go back to `physics.odin` and use the new procedure at the end of `ApplyGravity`. We also have to add a new parameter to `ApplyGravity`, the collection of all models, which we then pass to `CastRayFromWorldPosition`. That means we also need to update the call to `ApplyGravity` in `ApplyPhysics`.

```odin
ApplyPhysics :: proc(models: []Model, deltaTime: f32) {
    for &model in models {
        rb, has_rb := model.rigidBody.?
        if !has_rb || rb.isStatic do continue

        ApplyGravity(&model, models, deltaTime)
        IntegrateLinearForce(&model, deltaTime)
    }
}

ApplyGravity :: proc(model: ^Model, models: []Model, deltaTime: f32) {
    rb := &model.rigidBody.(RigidBody)
    rb.velocity += GRAVITY * deltaTime

    ray := CastRayFromWorldPosition(model.translation.y, -WORLD_UP, models, model.scale * 0.5 + GROUND_PROBE_DIST, model)
    if ray.hit {
        ApplyFriction(model, ray.model^)
    }
}
```

We're still missing the implementation of the `ApplyFriction` procedure, and the `GROUND_PROBE_DIST` constant is not defined yet. Let's first define the constant in `constants.odin`. It's just a tiny distance for a small raycast; remember we're trying to find out whether one model sits on top of another.

```odin
GROUND_PROBE_DIST :: 0.05
```

Finally, add the `ApplyFriction` procedure in `physics.odin`.

```odin
ApplyFriction :: proc(model: ^Model, other: Model) {
    rbo, has_rbo := other.rigidBody.?
    avgFriction := (model.rigidBody.?.friction + rbo.friction) * 0.5 if has_rbo else (model.rigidBody.?.friction + 1.0) * 0.5

    rb := &model.rigidBody.(RigidBody)
    rb.force.x *= avgFriction
    rb.force.z *= avgFriction
}
```

As you can see, we get the average from both models; the `model` is the one on top and `other` is the one below it, but in case the bottom one doesn't have ridigbody, we average with 1.0. Then we use that average as a factor to scale the horizontal force acting on the top model (we only apply it to its x and z components). The bigger the average value, the more of the horizontal force is preserved, so the model on top will slide more easily and for longer. Though it's not a physically 100% accurate simulation of friction, it looks convincing enough and would be enough for a game.

You might also point out that the friction value is flipped over, and yes, you'd be correct; friction is a force that opposes relative motion between surfaces. But in our simplified simulation, I like the value 0.0 representing no friction; otherwise, we'd have to start with some maximum friction value and subtract from it. However, if you can't accept this inverted friction, I'd rather suggest renaming it to `slipperiness`, rather than subtracting from a maximum friction.

The last thing to add today is bounciness. That's very simple, but note that our bounciness value isn't the conventional coefficient of restitution; it's simply a parameter controlling how much of the normal velocity is removed and reversed. We go to the `collisions.odin` file, and in the `Push` procedure, where we directly modify velocity, we simply multiply everything by the bounciness. The bigger the bounciness, the more the object bounces in the opposite direction when it collides.

```odin
rb.velocity -= Vector3DotProduct(rb.velocity, normal) * normal * rb.bounciness
```

To test all of this, in `main.odin`, update both calls of the `AddRigidbody`procedure by setting a different bounciness, friction, and mass:

```odin
AddRigidbody(&cubeM, bounciness = 2.0, friction = 3.0)
AddRigidbody(&cubeL, mass = 4.0)
```

If you now compile and run the program (`odin run . -o:speed`), you should see `cubeM` bounce up when it hits `cubeL` or fall from `cubeL` to `cubeFloor`, and if you push or pull it with the mouse and then stop it should keep sliding for a while, as if the surface on which it moves is slippery. Contrary, the cubeL is much heavier now and has default bounciness and friction, so if you push or pull this one, you should see its movement is much more sluggish, exactly as we'd expect from moving a heavy object.

[](/uploads/phys_eng_vi_final.mp4)

And that's it for today. If something doesn't work as expected, you can always find complete implementation for this and all other parts in [this GitHub repository](https://github.com/marianpekar/software-renderer-with-physics-odin-tutorials). In the next part, we're going to tackle angular motion, and we'll be able to tip cubes over edges, and they land as expected on the side closest to the ground. Our physics simulation, though very simplified in many aspects, will start looking quite convincing, and our objects will even slide on tilted surfaces.

## Other Parts of This Series

- [Physics Engine in Odin from Scratch, Part I](physics-engine-in-odin-from-scratch-part-i)
- [Physics Engine in Odin from Scratch, Part II](physics-engine-in-odin-from-scratch-part-ii)
- [Physics Engine in Odin from Scratch, Part III](physics-engine-in-odin-from-scratch-part-iii)
- [Physics Engine in Odin from Scratch, Part IV](physics-engine-in-odin-from-scratch-part-iv)
- [Physics Engine in Odin from Scratch, Part V](physics-engine-in-odin-from-scratch-part-v)
- Physics Engine in Odin from Scratch, Part VI

> Author: Marian Pekar - <https://marianpekar.com>
> (c) Marian Pekar. The posts stay freely readable on the author's site; this local copy is credited in `SOURCES.md` at the repo root. Please link back to the original article.

>Source: https://marianpekar.com/blog/physics-engine-in-odin-from-scratch-part-vi
