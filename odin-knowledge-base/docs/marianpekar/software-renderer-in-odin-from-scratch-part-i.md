# Software Renderer in Odin from Scratch, Part I

2nd March 2025 • 17 min read

In the first part of the longest tutorial series yet, I'll outline what's coming in the next nine parts, and we'll lay a cornerstone for a 3D software renderer that we're going to write from scratch.

![Showcase of all render modes our 3D software renderer will support.](/uploads/sw_renderer_i_render_modes.png)

If you look at the picture above, you might now see a monkey's head rendered in different lighting and modes, but when we're done with all ten parts, if you follow along and really let the knowledge soak in, I can guarantee that when you look at this picture again, you'll see something different. You'll understand why every single pixel has the color and position it does, and even more. And it will feel great!

So, what exactly are we going to do? In this part, we're going to primarily set expectations, talk in broad terms about how a 3D software rendering pipeline work and in the end, we'll make a few baby steps on a journey to implementing such a pipeline. But first, let's answer the question with a capital W.

## Why Implement a Software Renderer from Scratch?

Why build a rendering pipeline that calculates what GPUs are designed for, on a CPU? Isn't that completely useless? Well, it might not have many practical use cases these days, but it's a project packed with interesting algorithms and heavy use of linear algebra. Personally, I find it quite satisfying to have this knowledge simply because it's extremely fascinating.

However, if that's not your case, and you're only looking for practical knowledge, something directly applicable to real-world projects, you can stop reading now. I really don’t want to waste more of your time. For the rest, the second yet no less important question is…

## Why Odin?

You might not have even heard about the [Odin programming language](https://odin-lang.com/) yet, and I won't blame you. Originally, when I was learning about software rendering, I implemented it in C.

C is a very powerful but also quite old and cumbersome language. Yet, for implementing a software renderer, we really need to be close to the metal. Meaning we need a language with minimal overhead and a high level of control. It wouldn't be wise to implement a software renderer in C# or Java, for example. These languages run on top of managed runtimes and use garbage collection, which introduces performance overhead and reduces control.

Don’t get me wrong, I think automatic memory management is a great thing, and I wrote a lot of C# code. I wouldn’t want to develop, say, a Web API or an Android app in C. But when it comes to a software renderer, C is a natural choice. But wait a minute, we're going to implement our software renderer in Odin, not C, right? Yes! According to its official website, Odin is:

*"A general-purpose programming language with distinct typing, built for high performance, modern systems, and data-oriented programming. Odin is the C alternative for the Joy of Programming."*

I have to admit I was a bit sceptical when I was reading this statement for the first time, especially after my disappointment with Rust. Rust claims to solve many issues of C++, but in my opinion, it does so just by replacing them with a different set of even worse issues.

Anyway, back to the subject. Odin is a perfect fit for this project because those statements are actually very true. It also has something called array programming, which will be particularly useful for us. Additionally, it offers out-of-the-box bindings for [raylib](https://www.raylib.com/), which I’ll get back to in a moment.

## What about raylib?

It's a powerful library for creating graphical applications and games, but we're only going to use a small part of it. We'll rely on raylib for:

- Creating a window
- Handling keyboard inputs
- Rendering pixels at specific screen coordinates, like this: `rl.DrawPixel(x, y, color)`
- Reading pixel data from an image file

Everything else will be custom-made. We won’t even use raylib's `DrawLine` function to draw lines between points. We're going to write our own procedure.

It would be relatively easy to swap raylib for another library with similar capabilities, like SDL or any other that can draw a point on the screen. We could implement this ourselves, but I decided to draw the line here (pun not intended). I still believe we can say we're building a software renderer from scratch because creating a window, drawing a pixel, and handling inputs are things common to many applications.

Plus, writing everything on our own would require platform-specific implementations for Windows, Linux, and macOS to make the project run on most machines. That's something raylib gives us for free, so we can focus solely on implementing our rendering pipeline.

## What to Expect in This Series

Now that you know why Odin and raylib were chosen and that nothing important will be hidden from you, let's talk about what we're going to learn in the upcoming parts.

After discussing how the software rendering pipeline works and laying a cornerstone in Part I, Part II will be a math primer, where we'll cover vectors and matrices, the fundamental building blocks of rendering pipelines.

Part III will be dedicated to projections and transformations, and in Part IV, we're going to construct a hard-coded cube, which we'll render in Part V in wireframe mode. In that part, we're also going to implement input handling to move, scale, and rotate our cube at runtime.

In Part VI, we'll talk about backface culling, triangle rasterization, and the Z-buffer. If these terms are new to you, don’t worry, I’ll explain everything in detail once we get there. By this point, we'll have a solid cube that we can rotate, scale, and move around.

In Part VII, we'll apply flat shading on our cube, using an ambient and a global directional light. This will give our cube a more 3D appearance.

In Part VIII, we're going to introduce textures. We’ll load an image and project it onto the surface of our cube. While doing so, we'll learn about texture sampling and UV mapping. To ensure spatially accurate mapping, we’ll also discuss perspective-correct interpolation, which prevents distortion when mapping textures onto 3D surfaces. This distortion was common in PlayStation 1 games because the correction was too computationally expensive back in those days.

In Part IX, we'll write a loader for Wavefront OBJ files, which is a simple format for storing 3D models. This will allow us to load meshes created in Blender, for example, as long as they are triangulated and exported into this format, which is something Blender can do out of the box.

In Part X, we'll implement rendering modes with [Phong shading](https://en.wikipedia.org/wiki/Phong_shading) while introducing a point light. Unlike flat shading, Phong shading gives us smooth lighting transitions across the surface.

![Phong shading (left) vs. flat shading (right)](/uploads/sw_renderer_i_phong_vs_flat.png)

By this point, you'll have a strong understanding of how a software rendering pipeline works. While rendering pipelines in DirectX, OpenGL, or Vulkan are far more complex and run in parallel on thousands of GPU cores, they share the same fundamental principles. So when you start learning more about these technologies, you'll have a significant advantage.

In Part XI, we'll be talking about profiling and implementing an optimization technique that significantly improves the performance of our renderer.

In Part XII, we're going to implement switching between orthographic and perspective projection at runtime, and in Part XIII, we're going to add multiple lights with different colors, and we'll learn how to blend them.

Finally, in Part XIV, we're going to introduce the concept of a model, and we'll be able to render multiple models in our scene.

![Two different models with different textures illuminated by two lights of different collors.](/uploads/sw_rend_xiv_multiple_models.png)

## How a 3D Software Rendering Pipeline Works

At the end of the day, it's all really just about transforming data from one form to another. You have a text file on your disk, let's say it's called `cube.obj`, and an image. They might look like this.

```odin
v -1.000000 -1.000000 -1.000000
v -1.000000 1.000000 -1.000000
v 1.000000 1.000000 -1.000000
v 1.000000 -1.000000 -1.000000
v 1.000000 1.000000 1.000000
v 1.000000 -1.000000 1.000000
v -1.000000 1.000000 1.000000
v -1.000000 -1.000000 1.000000
vn 0.0000 0.0000 -1.0000
vn 1.0000 0.0000 0.0000
vn 0.0000 0.0000 1.0000
vn -1.0000 0.0000 0.0000
vn 0.0000 1.0000 0.0000
vn 0.0000 -1.0000 0.0000
vt 1.000000 1.000000
vt 1.000000 0.000000
vt 0.000000 0.000000
vt 0.000000 1.000000
f 1/1/1 2/2/1 3/3/1
f 1/1/1 3/3/1 4/4/1
f 4/1/2 3/2/2 5/3/2
f 4/1/2 5/3/2 6/4/2
f 6/1/3 5/2/3 7/3/3
f 6/1/3 7/3/3 8/4/3
f 8/1/4 7/2/4 2/3/4
f 8/1/4 2/3/4 1/4/4
f 2/1/5 7/2/5 5/3/5
f 2/1/5 5/3/5 3/4/5
f 6/1/6 8/2/6 1/3/6
f 6/1/6 1/3/6 4/4/6
```

![](/uploads/uv_checker_512.png)

Your program loads these files, this data, into memory, processes it through the pipeline along with some parameters, and displays something like this on the screen.

[](/uploads/sw_renderer_i_cube.mp4)

When you think about it, it's dead simple… well, that's a huge oversimplification, of course. But really, it's not that complicated; it just requires processing the data correctly.

![That’s easier said than done and I have plenty of outtakes like this :-).](/uploads/sw_renderer_i_fail.png)

So, let's now break down a software rendering pipeline. We're not going into too much detail right now. The goal is just to give you a brief overview before we start actually building the pipeline.

The first step is typically reading a file that contains data that defines a 3D object and an image file that will be mapped onto the object's surface. We usually call such a file a *texture*. However, in our implementation, we first hard-code a cube definition for testing purposes and write the file loader later. A 3D object itself is typically called a *mesh*.

If you look at the content of the `cube.obj` file more closely, you'll see that every line starts with one or two characters followed by numbers and eventually some slashes. The first group starts with `v`, which stands for vertices. Vertices are points in 3D space, for example, `1.000000 1.000000 1.000000` represents a point that is one unit away from the origin along the `X`, `Y`, and `Z` axes.

But in which directions? That depends on the handedness of the coordinate system. In a right-handed system, positive X is to the right, positive Y is up, and positive Z is forward. In a left-handed system, positive Z is backward. The important thing is that once a handedness is chosen, it must remain consistent throughout the entire pipeline.

Let's assume our system is right-handed, where `1.000000 1.000000 1.000000` means one to the right, one forward, and one up. If you look at all the lines starting with `v` and plot them in a 3D space, you'll see that they resemble a cube, as they form eight corners that are uniformly spaced from each other.

The lines starting with `vn` and `vt` define vertex normals and UV coordinates, respectively. Vertex normals indicate the direction a surface is facing, which is used for various purposes, such as for optimizations or lighting calculations. UV coordinates define how a texture should be mapped onto the object's surface.

The last group starts with `f`, which stands for face. These lines reference data defined in the previous groups and, as such defines faces of a 3D model. In our case, the faces are always triangles; in other words, each face consists of 3 vertices, these vertices have 3 normals and 3 UV-coordinates. The format follows this pattern: `f v1/vt1/vn1 v2/vt2/vn2 v3/vt3/vn3`.

What I just described is the main part of the [Wavefront OBJ file format](https://en.wikipedia.org/wiki/Wavefront_.obj_file). We'll learn how to parse it in one of the upcoming parts. You don't need to worry too much about the details right now. What's important is that you now have a broad understanding of how a 3D mesh will be defined so that our program, our rendering pipeline, can understand it. There are many file formats for 3D models, but this one, as you'll see, can be very easily parsed.

When files are parsed and all data is loaded into memory, usually in a set of arrays, the fun really begins. We typically want to transform these points to *rotate*, *move*, or *scale* the 3D object before rendering it. This can be achieved elegantly by using 4×4 transformation matrices for *rotation*, *translation*, and *scaling*. These matrices are optional; if you don't need all transformations, you can apply only rotation and translation, for example. However, we always need to consider the observer, which is also represented as a 4×4 matrix. This matrix is commonly called the *view matrix*, but in some implementations, you might see this matrix stored in a variable called `eye`.

The cool thing about these transformations is that they are just linear algebra. Each vertex from our set of vertices is multiplied by a final transformation matrix, which is the product of multiplying all the individual transformation matrices together. The order of multiplication matters, as it determines how transformations are applied, but in the end, they are all applied as expected using that single final matrix.

Again, this is a very simple explanation. We'll return to this topic and cover it in much more detail in the later part dedicated to transformations. That part will come after the math primer, in which we'll also cover matrix multiplication.

Now that we have our vertices transformed to their final positions, we need to render them on the screen. In other words, project their 3D space coordinates onto 2D screen coordinates.

In this series, we’ll start with drawing a wireframe model. This will be very simple since we’ll just draw lines between the points of the triangles that form a 3D model. Then, we’re going to build on top of that by filling these triangles with pixels. Initially, with a solid white color. Later, we’ll modify this color per triangle based on the angle between a light direction and the triangle’s orientation. This creates a simple illusion of lighting and is commonly referred to as *flat shading*.

![From the top-left, clockwise: wireframe, solid color without lighting, solid color with flat shading, and textured with flat shading.](/uploads/sw_renderer_i_render_modes_2.png)

Next, we’ll introduce textures, both with and without flat shading, and finally, in the last part, we’ll implement Phong shading, a more advanced lighting technique where we calculate the intensity per pixel rather than per triangle, as is the case in flat shading.

This process is also known as [rasterization](https://en.wikipedia.org/wiki/Rasterisation), and it is the essence of the renderer. It's a process of converting an image described with vectors into a raster image, an image composed of dots on the screen. We usually call these dots *pixels*. When I mentioned at the very beginning that you would understand every pixel, this is what I meant.

I should emphasize again that this is a huge simplification. I’ve skipped many details, which we’ll cover much more throughout this series. But enough theory for now, even if that was just a very high-level overview, and…

## Let's Get Started!

If this is your first encounter with Odin, I highly recommend that you familiarize yourself with the basics, read the [Odin documentation](https://odin-lang.org/docs/), [download Odin](https://odin-lang.org/docs/install/), and set up your environment.

By the time I implemented the software renderer, I was using the [dev-2024-12](https://github.com/odin-lang/Odin/releases/tag/dev-2024-12) version, and I'm using [Visual Studio Code](https://code.visualstudio.com/) as my IDE when writing Odin, with the [Odin Language Support](https://marketplace.visualstudio.com/items?itemName=DanielGavin.ols) plugin by Daniel Gavin.

Now, to start a project, create a new directory and add a new file `constants.odin` with the following content.

```odin
package main

SCREEN_WIDTH :: 800
SCREEN_HEIGHT :: 600
```

Notice the `::` operator we used to declare and, in this case, also define a constant. This constant is of type `untyped integer`. You can read more about this and other topics in a comprehensive [Introduction to the Odin Programming Language](https://zylinski.se/posts/introduction-to-odin/#variables-and-constants) by Karl Zylinski.

Now, create another file, `main.odin`, and type in the following:

```odin
package main

import rl "vendor:raylib"

main :: proc() {
    rl.InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "Renderer")

    for !rl.WindowShouldClose() {

        // TODO

        rl.EndDrawing()
    }

    rl.CloseWindow()
}
```

If you compile and run the application now by entering `odin run .` to the console, you should see a black window, 800x600 pixels, titled `Renderer`. And that's all you need to do to create a window. Amazing, right? If you ever worked before with raylib or with other libraries, like SDL2, in C++, you surely must appreciate how simple working with raylib in Odin is. Let's go over these few lines step by step.

```odin
package main

import rl "vendor:raylib"
```

Odin lets you organize your code into packages. In our project, we put all our implementation into a single package called `main`, thus every file we'll add needs to start with `package main`. Notice that `constants.odin` starts with this line too.

And a different package we're going to use in our implementation is `vendor:raylib`. If you navigate to the directory where you extracted Odin during installation (e.g., `C:\odin`), you'll find a `vendor` directory, and inside, a `raylib` directory. This provides bindings to the popular raylib library, which is already included with Odin. We specified `rl` as an alias so that we can access everything exposed in this package using the `rl.` notation.

In our main procedure, we use raylib to initialize a window with a width and height specified by our constants.

```odin
rl.InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "Renderer")
```

Then, we keep the program running until the user intentionally closes the window. Later, I'll refer to one iteration over this loop as a **frame**. So, for example, when I say 60 frames per second, it means everything inside this loop is executed 60 times in one second.

```odin
for !rl.WindowShouldClose() {

    // TODO

    rl.EndDrawing()
}
```

When the program jumps out of the main loop, or in other words, when `rl.WindowShouldClose()` returns `true`, we close the window, and the program ends.

```odin
rl.CloseWindow()
```

Before we wrap this part up, let's just add this line of code inside the loop, instead of that `// TODO` comment.

```odin
rl.DrawPixel(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, rl.RED)
```

I bet you already know you're going to see when you run the program… Yes, you'll see a single red pixel in the center of the window. That's already most of what we're going to use raylib for; everything else, except input handling, will be implemented from scratch.

## Conclusion

In this part, you got an outline of what we'll build over the remaining nine parts, and you also learned, in a simplified way, how a software rendering pipeline works. I also explained why I chose Odin and raylib for this project, and that our use of raylib will be limited to creating a window, handling input, and drawing pixels. Even though raylib offers much more, our goal is to learn, and that is best achieved by implementing things from scratch. Then, we set up our IDE and project so that in the next part, we can continue by building our software renderer step by step.

And before we wrap this up, I’ve created a [GitHub repository](https://github.com/marianpekar/software-renderer-odin-tutorials) where each directory contains a working implementation up to the point we’ve covered so far. If you're following along, you can always compare your implementation in case something isn’t working as expected, and use it to fix any issues.

## Other Parts of This Series

- Software Renderer in Odin from Scratch, Part I
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
- [Software Renderer in Odin from Scratch, Part XIII](software-renderer-in-odin-from-scratch-part-xiii)
- [Software Renderer in Odin from Scratch, Part XIV](software-renderer-in-odin-from-scratch-part-xiv)

> Author: Marian Pekar - <https://marianpekar.com>
> (c) Marian Pekar. The posts stay freely readable on the author's site; this local copy is credited in `SOURCES.md` at the repo root. Please link back to the original article.

>Source: https://marianpekar.com/blog/software-renderer-in-odin-from-scratch-part-i
