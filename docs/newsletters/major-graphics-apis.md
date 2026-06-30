Odin now officially supports both the [Metal](https://developer.apple.com/metal/) API and [Direct3D](https://docs.microsoft.com/en-us/windows/win32/direct3d) 11 & 12 out-of-the box! This makes Odin currently the only language that officially supports all of the major graphics APIs: [OpenGL](https://pkg.odin-lang.org/vendor/OpenGL/), [Vulkan](https://pkg.odin-lang.org/vendor/vulkan/), [Direct3D11](https://pkg.odin-lang.org/vendor/directx/d3d11/), [Direct3D12](https://pkg.odin-lang.org/vendor/directx/d3d12/), [Metal](https://pkg.odin-lang.org/vendor/darwin/Metal/), [wgpu](https://pkg.odin-lang.org/vendor/wgpu) and [WebGL 1 & 2](https://github.com/odin-lang/Odin/tree/master/vendor/wasm/WebGL).

## Metal [#](#metal)

![Metal](/vendor/companies/Metal_2_Logo.png)

Odin now has *NATIVE* Metal support, and it is even cleaner than writing it in Objective-C in numerous cases!

Native support means that Odin is *directly* caling the Objective-C runtime, and not through a wrapper of another language. This means that the Metal package in Odin will have virtually the same performance as Objective-C code. This means you can now write Metal code without being locked into using an Apple-specific language.

### Example and Documentation [#](#example-and-documentation)

You can check out a minimal demonstration of Metal in Odin here: <https://gist.github.com/gingerBill/e1270f60a1739c266934599c2bee46f5>.

And the automatically generated package documentation here: [`package vendor:darwin/Metal` documentation](https://pkg.odin-lang.org/vendor/darwin/Metal/).

> Metal in Native Odin!!! No need for Objective-C or Swift any more it seems.<https://t.co/v5D2FP1LlB> (I had to do the obligatory RGB triangle)
>
> This means that Odin will ship out of the box with Metal, Vulkan, and OpenGL, and libraries such as GLFW and SDL!
>
> Only D3D to go! [pic.twitter.com/r6BnzDBXXO](https://t.co/r6BnzDBXXO)
>
> - gingerBill (@TheGingerBill) [February 15, 2022](https://twitter.com/TheGingerBill/status/1493581485919678472?ref_src=twsrc%5Etfw)

### Metal in Objective-C [#](#metal-in-objective-c)

```odin
MTLSamplerDescriptor *samplerDescriptor = [[MTLSamplerDescriptor alloc] init];

[samplerDescriptor setSAddressMode: MTLSamplerAddressModeRepeat];
[samplerDescriptor setTAddressMode: MTLSamplerAddressModeRepeat];
[samplerDescriptor setRAddressMode: MTLSamplerAddressModeRepeat];
[samplerDescriptor setMagFilter: MTLSamplerMinMagFilterLinear];
[samplerDescriptor setMinFilter: MTLSamplerMinMagFilterLinear];
[samplerDescriptor setMipFilter: MTLSamplerMipFilterLinear];
[samplerDescriptor setSupportArgumentBuffers: YES];

id< MTLSamplerState > samplerState = [device newSamplerStateWithDescriptor:samplerDescriptor];

[samplerDescriptor release];

// ...

[samplerState release];
```odin
### Metal in Odin [#](#metal-in-odin)

```odin
samplerDescriptor := MTL.SamplerDescriptor.alloc()->init()

samplerDescriptor->setSAddressMode(.Repeat)
samplerDescriptor->setTAddressMode(.Repeat)
samplerDescriptor->setRAddressMode(.Repeat)
samplerDescriptor->setMagFilter(.Linear)
samplerDescriptor->setMinFilter(.Linear)
samplerDescriptor->setMipFilter(.Linear)
samplerDescriptor->setSupportArgumentBuffers(true)

samplerState := device->newSamplerState(samplerDescriptor)

samplerDescriptor->release()

// ...

samplerState->release()
```odin
## DirectX [#](#directx)

![DirectX](/vendor/companies/DirectX_logo.svg)

### Example and Documentation [#](#example-and-documentation-1)

You can check out a minimal demonstration of Direct3D11 in Odin here: <https://gist.github.com/gingerBill/b7b75772f92c5511a9cd3ca2e28eca37>.

And the automatically generated package documentation here for both D3D11 and D3D12:

- [`package vendor:directx/d3d11` documentation](https://pkg.odin-lang.org/vendor/directx/d3d11/)
- [`package vendor:directx/d3d12` documentation](https://pkg.odin-lang.org/vendor/directx/d3d12/)

> I got Metal working natively in [@odinlang](https://twitter.com/odinlang?ref_src=twsrc%5Etfw) the other day. I've now gone and got D3D11 and D3D12 working in Odin!<https://t.co/cHzyfmeBLG>
>
> Odin shipping out-of-the-box will all of major graphics APIs: Metal, D3D11, D3D12, Vulkan, OpenGL, and WebGL! [pic.twitter.com/60sau6BRqt](https://t.co/60sau6BRqt)
>
> - gingerBill (@TheGingerBill) [February 17, 2022](https://twitter.com/TheGingerBill/status/1494429405640335363?ref_src=twsrc%5Etfw)

Writing Direct3D code is Odin is really simple! The code will be nearly the same as writing it as if you were using the APIs in native C++ with thanks to the [`->` operator](/docs/overview/#--operator-selector-call-expressions):

```odin
depth_buffer_desc: D3D11.TEXTURE2D_DESC
framebuffer->GetDesc(&depth_buffer_desc)
depth_buffer_desc.Format = .D24_UNORM_S8_UINT
depth_buffer_desc.BindFlags = .DEPTH_STENCIL

depth_buffer: ^D3D11.ITexture2D
device->CreateTexture2D(&depth_buffer_desc, nil, &depth_buffer)

depth_buffer_view: ^D3D11.IDepthStencilView
device->CreateDepthStencilView(depth_buffer, nil, &depth_buffer_view)
```odin
```odin
sampler_desc := D3D11.SAMPLER_DESC{
	Filter         = .MIN_MAG_MIP_POINT,
	AddressU       = .WRAP,
	AddressV       = .WRAP,
	AddressW       = .WRAP,
	ComparisonFunc = .NEVER,
}
sampler_state: ^D3D11.ISamplerState
device->CreateSamplerState(&sampler_desc, &sampler_state)
```

>Source: https://odin-lang.org/news/major-graphics-apis
