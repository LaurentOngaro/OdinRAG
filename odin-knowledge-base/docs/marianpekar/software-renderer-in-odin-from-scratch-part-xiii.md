# Software Renderer in Odin from Scratch, Part XIII

26th February 2026 • 18 min read

In [Part XII](https://marianpekar.com/blog/software-renderer-in-odin-from-scratch-part-xii), we implemented support for orthographic projection. Today, we're going to extend our already feature-rich software renderer even more. If you open the `light.odin` file, you'll see that our `Light` can have position, direction, and strength, but there's no color; our light is always white.

Another limitation of our software renderer is that we can only have one light in the scene, which is something we're also going to address in this part. At the end of this part, we'll be able to place multiple lights with different colors in different positions, plus we'll also be able to change the color of the ambient lighting, as you can see in the video below. Notice the subtle blue tint when the monkey is too far from both green and red lights to be illuminated in Phong shading mode.

[](/uploads/sw_rend_xiii_multiple_lights.mp4)

Also, notice how the different light colors are blended together with the texture, while the triangles are moving through the scene, where we have the two lights positioned close to our camera, the red on the left and the green on the right.

## Updating light.odin

Let's start in the `light.odin` file you have already opened and replace the `strength` 32-bit float parameter with the `color` of type `Vector4` in both `Light` struct definition and `MakeLight` factory procedure:

```odin
package main

Light :: struct {
    position: Vector3,
    direction: Vector3,
    color: Vector4,
}

MakeLight :: proc(position, direction: Vector3, color: Vector4, viewMatrix: Matrix4x4) -> Light {
    return { 
        Mat4MulVec3(viewMatrix, position), 
        Vector3Normalize(direction), 
        color
    }
}
```

If you're asking right now, why the `Vector4` and why we're removing strength, then that's a great question. `Vector4` is just our alias for `[4]f32` that we defined in vectors.odin file, and we already know from previous parts that color can be represented in RGB space by 3 numbers, so instead of keeping `strength` and having color as `Vector3` or even as three individual parameters r, g, and b, we can pack everything into a `Vector4`. The first three elements will represent the amount of red, green, and blue, respectively, and we can use the fourth for strength, or intensity of the light, if you prefer this term.

## Updating draw.odin

This change obviously broke our call of the `MakeLight` procedure in the `main.odin` file, but before we fix that, let's open the `draw.odin` file, where most of today's work is waiting for us. Since we want to support more than a single light, we'll have to adjust all rendering pipelines to which we're currently passing our single `light` instance. Specifically, pipelines that start with `DrawFlatShaded`, `DrawPhongShaded`, `DrawTexturedFlatShaded`, and `DrawTexturedPhongShaded` procedures.

Let's start with the `DrawFlatShaded` procedure. This is the simplest change; we rename the `light` parameter to `lights` and change its type from `Light` to `[]Light`. We also changed the type of the ambient parameter from `f32` to `Vector3`. For the ambient light, we're not going to specify intensity, just RGB color. The updated signature looks like this:

```odin
DrawFlatShaded :: proc(
    vertices: []Vector3, 
    triangles: []Triangle,
    projMat: Matrix4x4,
    projType: ProjectionType,
    lights: []Light, 
    color: rl.Color, 
    zBuffer: ^ZBuffer,
    image: ^rl.Image,
    ambient: Vector3
)
```

Inside the procedure, we're now going to remove the `intensity,` and instead, we're going to define a new variable for *accumulated light*, `lightAccum`, that we initialize using the `ambient` light. Then, inside a for loop over all lights, we're going to add to each color channel of `lightAccum`, the result of the respective color channel from each light multiplied by `diffuse`, that is, the color of the entire triangle calculated for flat shading as before, but now we calculate it for each light. We also multiply each color channel by the alpha channel of the light, the 4th component, since we decided to pack the strength of our light there.

```odin
lightAccum := ambient
for &light in lights {
    diffuse := math.max(0.0, Vector3DotProduct(crossNorm, light.direction))
    lightAccum.r += diffuse * light.color.r * light.color.a
    lightAccum.g += diffuse * light.color.g * light.color.a
    lightAccum.b += diffuse * light.color.b * light.color.a
}
```

Now, after this for loop, some or all color channels might be over 1.0, which is the maximum value each channel of the accumulated light should have. We use the `math.min` procedure to effectively clamp the value if it exceeds 1.0.

```odin
lightAccum.r = math.min(lightAccum.r, 1.0)
lightAccum.g = math.min(lightAccum.g, 1.0)
lightAccum.b = math.min(lightAccum.b, 1.0)
```

And that's it. The last thing we need to do is update `shadedColor`. Where we previously multiplied each channel by `intensity`, we now multiply these channels by the respective channels of accumulated light.

```odin
shadedColor := rl.Color{
    u8(f32(color.r) * lightAccum.r),
    u8(f32(color.g) * lightAccum.g),
    u8(f32(color.b) * lightAccum.b),
    color.a
}
```

Changes in the other rendering pipelines are analogous. Let's proceed with Phong shading pipeline, where we calculate lighting per pixel. We're going to have to update more procedures this time, but the change is fundamentally the same as we just did in the `DrawFlatShaded`, and you probably already guessed that we're going to update the `DrawPixelPhongShaded` procedure.

Again, let's start with the signature. We're going to pass in more `lights` and `ambient` will be `Vector3` instead of just a single `f32`.

```odin
DrawPixelPhongShaded :: proc(
    x, y: f32,
    v1, v2, v3: ^Vector3,
    n1, n2, n3: ^Vector3,
    p1, p2, p3: ^Vector3,
    color: rl.Color,
    lights: []Light,
    zBuffer: ^ZBuffer,
    image: ^rl.Image,
    ambient: Vector3
)
```

Now, remove the `rayDir`, which will be replaced with the `lightVec` for each light in a for loop, and also remove `intensity`. Instead, we once again create `lightAccum` to calculate and accumulate values from multiple light sources.

```odin
lightAccum := ambient
for &light in lights {
    lightVec := Vector3Normalize(light.position - interpPos)
    diffuse  := math.max(Vector3DotProduct(interpNormal, lightVec), 0.0)
    lightAccum.r += diffuse * light.color.r * light.color.a
    lightAccum.g += diffuse * light.color.g * light.color.a
    lightAccum.b += diffuse * light.color.b * light.color.a
}
lightAccum.r = math.min(lightAccum.r, 1.0)
lightAccum.g = math.min(lightAccum.g, 1.0)
lightAccum.b = math.min(lightAccum.b, 1.0)
```

As you can see, the logic behind Phong shading hasn't changed; we now just work with more lights and separated color channels so we can blend them individually with the color. This is the same as in the `DrawFlatShaded`; we just calculate color per-pixel instead of per entire triangle.

```odin
shadedColor := rl.Color{
    u8(f32(color.r) * lightAccum.r),
    u8(f32(color.g) * lightAccum.g),
    u8(f32(color.b) * lightAccum.b),
    color.a
}
```

The change in the `DrawTrianglePhongShaded` procedure, where we call `DrawPixelPhongShaded`, is trivial. We update the signature and pass `lights` to both `DrawPixelPhongShaded` calls, one for flat-top, the other for flat-bottom triangle, where we previously passed just a single `light`.

```odin
DrawTrianglePhongShaded :: proc(
    v1, v2, v3: ^Vector3,
    p1, p2, p3: ^Vector3,
    n1, n2, n3: ^Vector3,
    color: rl.Color,
    lights: []Light,
    zBuffer: ^ZBuffer,
    image: ^rl.Image,
    ambient: Vector3
) {

    // Here's the rest of the procedure that remains unchanged.

    DrawPixelPhongShaded(
        x, y,
        v1, v2, v3, 
        n1, n2, n3,
        p1, p2, p3,
        color, lights, zBuffer, image, ambient
    )

    // Here's the rest of the procedure that remains unchanged.

    DrawPixelPhongShaded(
        x, y,
        v1, v2, v3, 
        n1, n2, n3,
        p1, p2, p3,
        color, lights, zBuffer, image, ambient
    )

    // Here's the rest of the procedure that remains unchanged.
}
```

And `DrawPhongShaded`, our entry procedure for this pipeline, which we call from `main.odin`, needs the same trivial change.

```odin
DrawPhongShaded :: proc(
    vertices: []Vector3, 
    triangles: []Triangle, 
    normals: []Vector3, 
    lights: []Light,
    color: rl.Color, 
    zBuffer: ^ZBuffer,
    projMat: Matrix4x4,
    projType: ProjectionType,
    image: ^rl.Image,
    ambient: Vector3
) {

    // Here's the rest of the procedure that remains unchanged.

    DrawTrianglePhongShaded(
        &v1, &v2, &v3, 
        &p1, &p2, &p3,
        &n1, &n2, &n3,
        color, lights, zBuffer, image, ambient
    )
}
```

Changes for the flat shading rendering pipeline with a texture are a little bit different; it's still fundamentally the same, but since we calculate light once for each triangle and then apply it per texel, what we're doing in regular flat shading without texture needs to be divided into more stages.

Let's start again from the bottom, by updating the `DrawTexelFlatShaded` procedure. Here, we just remove from the signature the `intensity` parameter, replacing it with a `light` of type `Vector3`, which will be our accumulated light.

```odin
DrawTexelFlatShaded :: proc(
    x, y: f32,
    p1, p2, p3: ^Vector3,
    uv1, uv2, uv3: ^Vector2,
    texture: Texture,
    light: Vector3,
    zBuffer: ^ZBuffer,
    image: ^rl.Image
)
```

In the body of the procedure, all we need to do is update the `shadedTex`; instead of intensity, we multiply each channel of a pixel sampled from the texture by the respective channel of the accumulated light.

```odin
shadedTex := rl.Color{
    u8(f32(tex.r) * light.r),
    u8(f32(tex.g) * light.g),
    u8(f32(tex.b) * light.b),
    tex.a,
}
```

The change in the `DrawTexturedTriangleFlatShaded` is also trivial, since we replaced `intensity` with `light`, we need to reflect this change when calling `DrawTexelFlatShaded` to draw flat-top and flat-bottom triangles.

```odin
DrawTexturedTriangleFlatShaded :: proc(
    p1, p2, p3: ^Vector3,
    uv1, uv2, uv3: ^Vector2,
    texture: Texture,
    light: Vector3,
    zBuffer: ^ZBuffer,
    image: ^rl.Image
) {
    // Here's the rest of the procedure that remains unchanged.

    DrawTexelFlatShaded(
        x, y,
        p1, p2, p3, 
        uv1, uv2, uv3, 
        texture, light, zBuffer, image
    )

    // Here's the rest of the procedure that remains unchanged.

    DrawTexelFlatShaded(
        x, y,
        p1, p2, p3, 
        uv1, uv2, uv3, 
        texture, light, zBuffer, image
    )

    // Here's the rest of the procedure that remains unchanged.
}
```

And the last change for this rendering pipeline needs to be done in its entry procedure, `DrawTexturedFlatShaded`. Here, we actually calculate the accumulated light exactly as we did in the `DrawFlatShaded`, but instead of adjusting color, we just pass the accumulated light down the pipeline.

```odin
DrawTexturedFlatShaded :: proc(
    vertices: []Vector3, 
    triangles: []Triangle, 
    uvs: []Vector2, 
    lights: []Light, 
    texture: Texture, 
    zBuffer: ^ZBuffer,
    projMat: Matrix4x4,
    projType: ProjectionType,
    image: ^rl.Image,
    ambient: Vector3
) {
    for &tri in triangles {

        // Here's the rest of the procedure that remains unchanged.

        lightAccum := ambient
        for &light in lights {
            diffuse := math.max(0.0, Vector3DotProduct(crossNorm, light.direction))
            lightAccum.r += diffuse * light.color.r * light.color.a
            lightAccum.g += diffuse * light.color.g * light.color.a
            lightAccum.b += diffuse * light.color.b * light.color.a
        }
        lightAccum.r = math.min(lightAccum.r, 1.0)
        lightAccum.g = math.min(lightAccum.g, 1.0)
        lightAccum.b = math.min(lightAccum.b, 1.0)

        DrawTexturedTriangleFlatShaded(
            &p1, &p2, &p3,
            &uv1, &uv2, &uv3,
            texture, lightAccum, zBuffer, image
        )
    }
}
```

That done, only the last rendering pipeline remains to be updated, the one that renders mesh Phong shaded with a texture. Let's start again from the bottom, in the `DrawTexelPhongShaded` procedure, replace `light` with `lights` of type `[]Light` and change the type of `ambient` to `Vector3`, as before.

```odin
DrawTexelPhongShaded :: proc(
    x, y: f32,
    v1, v2, v3: ^Vector3,
    n1, n2, n3: ^Vector3,
    p1, p2, p3: ^Vector3,
    uv1, uv2, uv3: ^Vector2,
    texture: Texture,
    lights: []Light,
    zBuffer: ^ZBuffer,
    image: ^rl.Image,
    ambient: Vector3
)
```

In the body of the procedure, we calculate accumulated light just as we did in the `DrawPixelPhongShaded` procedure; we don't need `intensity` and `rayDir`, so remove them, and after texture sampling, add the now well-known piece of code for calculating accumulated light in a for loop. Then we blend it with the currently sampled texel `tex` to get a `shadedTex` that is then drawn on the screen.

```odin
lightAccum := ambient
for &light in lights {
    lightVec := Vector3Normalize(light.position - interpPos)
    diffuse  := math.max(Vector3DotProduct(interpNormal, lightVec), 0.0)
    lightAccum.r += diffuse * light.color.r * light.color.a
    lightAccum.g += diffuse * light.color.g * light.color.a
    lightAccum.b += diffuse * light.color.b * light.color.a
}
lightAccum.r = math.min(lightAccum.r, 1.0)
lightAccum.g = math.min(lightAccum.g, 1.0)
lightAccum.b = math.min(lightAccum.b, 1.0)

shadedTex := rl.Color{
    u8(f32(tex.r) * lightAccum.r),
    u8(f32(tex.g) * lightAccum.g),
    u8(f32(tex.b) * lightAccum.b),
    tex.a,
}
```

The change in the `DrawTexturedTrianglePhongShaded` is just as trivial as in the `DrawTrianglePhongShaded` procedure; we just update the signature and pass `lights` instead of `light` down the pipeline to the `DrawTexelPhongShaded` procedure.

```odin
DrawTexturedTrianglePhongShaded :: proc(
    v1, v2, v3: ^Vector3,
    p1, p2, p3: ^Vector3,
    uv1, uv2, uv3: ^Vector2,
    n1, n2, n3: ^Vector3,
    texture: Texture,
    lights: []Light,
    zBuffer: ^ZBuffer,
    image: ^rl.Image,
    ambient: Vector3
) { 

    // Here's the rest of the procedure that remains unchanged.

    DrawTexelPhongShaded(
        x, y,
        v1, v2, v3, 
        n1, n2, n3, 
        p1, p2, p3, 
        uv1, uv2, uv3, 
        texture, lights, zBuffer, image, ambient
    )

    // Here's the rest of the procedure that remains unchanged.

    DrawTexelPhongShaded(
        x, y,
        v1, v2, v3, 
        n1, n2, n3, 
        p1, p2, p3, 
        uv1, uv2, uv3, 
        texture, lights, zBuffer, image, ambient
    )

    // Here's the rest of the procedure that remains unchanged.
}
```

In our entry procedure for this pipeline, we just need to once again replace `light` with `lights` of type `[]Light` and change the type of `ambient` to `Vector3`, and pass `lights` instead of `light` down the pipeline to just updated `DrawTexturedTrianglePhongShaded` procedure.

```odin
DrawTexturedPhongShaded :: proc(
    vertices: []Vector3, 
    triangles: []Triangle, 
    uvs: []Vector2, 
    normals: []Vector3, 
    lights: []Light,
    texture: Texture, 
    zBuffer: ^ZBuffer,
    projMat: Matrix4x4,
    projType: ProjectionType,
    image: ^rl.Image,
    ambient: Vector3
) {
    for &tri in triangles {

        // Here's the rest of the procedure that remains unchanged.

        DrawTexturedTrianglePhongShaded(
            &v1, &v2, &v3, 
            &p1, &p2, &p3,
            &uv1, &uv2, &uv3,
            &n1, &n2, &n3,
            texture, lights, zBuffer, image, ambient
        )
    }
}
```

And that concludes all changes in the `draw.odin` file.

## Updating main.odin

We're almost done today. Let's open the `main.odin` file to make the final changes. Remove the `light` from the `main` procedure and replace it with two new light instances, one red and the other green, that you create using the updated `MakeLight` procedure, and then store them in a slice.

```odin
red_light  := MakeLight({-4.0,  0.0, 0.0}, { 1.0,  1.0, 0.0}, {1.0, 0.0, 0.0, 1.0}, viewMatrix)
green_light := MakeLight({ 4.0,  0.0, 0.0}, {-1.0, -1.0, 0.0}, {0.0, 1.0, 0.0, 1.0}, viewMatrix)
lights := []Light{red_light, green_light}
```

After that, create two ambient lights; we don't have a special type for them, these are just Vector3s for packing their red, green, and blue color channels.

```odin
ambient := Vector3{0.2, 0.2, 0.2}
ambient2 := Vector3{0.1, 0.1, 0.2}
```

And finally, in our switch over `renderMode` update calls of `DrawFlatShaded`, `DrawPhongShaded`, `DrawTexturedFlatShaded`, and `DrawTexturedPhongShaded` procedures, passing the lights we've just prepared.

```odin
switch renderMode {
    // ...
    case 3: DrawFlatShaded(mesh.transformedVertices, mesh.triangles, projectionMatrix, projectionType, lights, rl.WHITE, zBuffer, &renderImage, ambient)
    case 4: DrawPhongShaded(mesh.transformedVertices, mesh.triangles, mesh.transformedNormals, lights, rl.WHITE, zBuffer, projectionMatrix, projectionType, &renderImage, ambient2)
    // ...
    case 6: DrawTexturedFlatShaded(mesh.transformedVertices, mesh.triangles, mesh.uvs, lights, texture, zBuffer, projectionMatrix, projectionType, &renderImage, ambient)
    case 7: DrawTexturedPhongShaded(mesh.transformedVertices, mesh.triangles, mesh.uvs, mesh.transformedNormals, lights, texture, zBuffer, projectionMatrix, projectionType, &renderImage, ambient2)
}
```

## Conclusion

And that's all for today. If you now compile and run our renderer (`odin run . -o:speed`), you should see the mesh illuminated with both red and green lights, just as in the video at the beginning of this post. Try to rotate it and move it around in different rendering modes to observe how red and green light colors, and also the ambient color, are blended on the surface of our mesh.

If something doesn't work as expected, you can always compare your version with the implementation for this part in this [GitHub repository](https://github.com/marianpekar/software-renderer-odin-tutorials). In the next and final part, we're going to introduce the concept of a model, to pack together mesh and texture to be able to have more than one of them in the scene.

## Other Parts of This Series

- [Software Renderer in Odin from Scratch, Part I](software-renderer-in-odin-from-scratch-part-i)
- [Software Renderer in Odin from Scratch, Part II](software-renderer-in-odin-from-scratch-part-ii)
- [Software Renderer in Odin from Scratch, Part III](software-renderer-in-odin-from-scratch-part-iii)
- [Software Renderer in Odin from Scratch, Part IV](software-renderer-in-odin-from-scratch-part-iv)
- [Software Renderer in Odin from Scratch, Part V](software-renderer-in-odin-from-scratch-part-v)
- [Software Renderer in Odin from Scratch, Part VI](software-renderer-in-odin-from-scratch-part-vi)
- [Software Renderer in Odin from Scratch, Part VII](software-renderer-in-odin-from-scratch-part-vii)
- [Software Renderer in Odin from Scratch, Part VIII](software-renderer-in-odin-from-scratch-part-viii)
- [Software Renderer in Odin from Scratch, Part IX](software-renderer-in-odin-from-scratch-part-ix)
- [Software Renderer in Odin from Scratch, Part X](software-renderer-in-odin-from-scratch-part-x)
- [Software Renderer in Odin from Scratch, Part XI](software-renderer-in-odin-from-scratch-part-xi)
- [Software Renderer in Odin from Scratch, Part XII](software-renderer-in-odin-from-scratch-part-xii)
- Software Renderer in Odin from Scratch, Part XIII
- [Software Renderer in Odin from Scratch, Part XIV](software-renderer-in-odin-from-scratch-part-xiv)

> Author: Marian Pekar - <https://marianpekar.com>
> (c) Marian Pekar. The posts stay freely readable on the author's site; this local copy is credited in `SOURCES.md` at the repo root. Please link back to the original article.

>Source: https://marianpekar.com/blog/software-renderer-in-odin-from-scratch-part-xiii
