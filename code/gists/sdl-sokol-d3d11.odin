// Source: https://gist.github.com/jakubtomsu/470e33d477936ba9c772e2395f661b5f
// Minimal D3D11 device and swapchain setup when using SDL with sokol_gfx | By Jakub Tomsu
// This is a minimal example of setting up an app with SDL and sokol_gfx with D3D11 as the backend.
// SDL and Sokol do all the heavy lifting, we just need to set up the device and frame buffers on our own.
//
// By Jakub Tomšů (x.com/jakubtomsu_)
//
// Note: I just copy&pasted parts of my engine code because some people were asking for it,
// and didn't do much more checking than that. So let me know if there are any issues.
//
// More resources:
// https://gist.github.com/d7samurai/261c69490cce0620d0bfc93003cd1052
// https://pkg.odin-lang.org/vendor/sdl2/
// https://github.com/floooh/sokol-odin/tree/main/examples
package game

import sg "../sokol/gfx"
import sdl "vendor:sdl2"
import "vendor:directx/d3d11"
import "vendor:directx/dxgi"

_main :: proc() {
    sdl.Init({.VIDEO})

    window := sdl.CreateWindow(
        title = "title",
        x = sdl.WINDOWPOS_CENTERED,
        y = sdl.WINDOWPOS_CENTERED,
        w = 1920,
        h = 1080,
        flags = {.BORDERLESS},
    )

    //
    // D3D11 Setup
    //

    window_system_info: sdl.SysWMinfo
    sdl.GetVersion(&window_system_info.version)
    sdl.GetWindowWMInfo(window, &window_system_info)
    assert(window_system_info.subsystem == .WINDOWS)

    native_window := dxgi.HWND(window_system_info.info.win.window)

    base_device: ^d3d11.IDevice
    base_device_context: ^d3d11.IDeviceContext

    feature_levels := [?]d3d11.FEATURE_LEVEL{._11_0}
    device_flags: d3d11.CREATE_DEVICE_FLAGS = {.SINGLETHREADED}
    if ODIN_DEBUG {
        device_flags += {.DEBUG}
    }

    d3d11.CreateDevice(
        pAdapter = nil,
        DriverType = .HARDWARE,
        Software = nil,
        Flags = device_flags,
        pFeatureLevels = &feature_levels[0],
        FeatureLevels = len(feature_levels),
        SDKVersion = d3d11.SDK_VERSION,
        ppDevice = &base_device,
        pFeatureLevel = nil,
        ppImmediateContext = &base_device_context,
    )

    device: ^d3d11.IDevice
    base_device->QueryInterface(d3d11.IDevice_UUID, cast(^rawptr)&device)

    device_context: ^d3d11.IDeviceContext
    base_device_context->QueryInterface(d3d11.IDeviceContext_UUID, cast(^rawptr)&device_context)

    dxgi_device: ^dxgi.IDevice1
    device->QueryInterface(dxgi.IDevice1_UUID, cast(^rawptr)&dxgi_device)

    dxgi_adapter: ^dxgi.IAdapter
    dxgi_device->GetAdapter(&dxgi_adapter)

    dxgi_factory: ^dxgi.IFactory2
    dxgi_adapter->GetParent(dxgi.IFactory2_UUID, cast(^rawptr)&dxgi_factory)

    dxgi_device->SetMaximumFrameLatency(1) // Optional

    swapchain_desc := dxgi.SWAP_CHAIN_DESC1 {
        Width = 0,
        Height = 0,
        Format = .B8G8R8A8_UNORM,
        Stereo = false,
        SampleDesc = {Count = 1, Quality = 0},
        BufferUsage = {.RENDER_TARGET_OUTPUT},
        BufferCount = 2,
        Scaling = .STRETCH,
        SwapEffect = .FLIP_DISCARD,
        AlphaMode = .UNSPECIFIED,
        Flags = {},
    }

    swapchain: ^dxgi.ISwapChain1
    dxgi_factory->CreateSwapChainForHwnd(device, native_window, &swapchain_desc, nil, nil, &swapchain)

    render_target: ^d3d11.ITexture2D
    swapchain->GetBuffer(0, d3d11.ITexture2D_UUID, cast(^rawptr)&render_target)
    
    render_target_view: ^d3d11.IRenderTargetView
    device->CreateRenderTargetView(render_target, nil, &render_target_view)

    {
        env: sg.Environment

        env.defaults.color_format = .RGBA8
        env.defaults.depth_format = .NONE
        env.defaults.sample_count = 1
        env.d3d11.device = device
        env.d3d11.device_context = device_context

        sg.setup({
            environment = env,
            // Also set allocator and logger...
        })
    }
    
    should_close := false
    for !should_close {
        for event: sdl.Event; sdl.PollEvent(&event); {
            #partial switch event.type {
            case .QUIT:
                should_close = true
            }
        }
    
        window_size: [2]i32
        sdl.GetWindowSize(window, &window_size.x, &window_size.y)
    
        //
        // Do your sokol rendering passes here...
        //
    
        sg.commit()
    
        swapchain_info: sg.Swapchain
        swapchain_info.width = window_size.x
        swapchain_info.height = window_size.y
        swapchain_info.sample_count = 1
        swapchain_info.color_format = .BGRA8
        swapchain_info.depth_format = .NONE
        swapchain_info.d3d11.render_view = render_target_view
        swapchain_info.d3d11.resolve_view = nil
        swapchain_info.d3d11.depth_stencil_view = nil
        
        device_context->OMSetRenderTargets(1, &render_target_view, nil)
        swapchain->Present(SyncInterval = 1, Flags = {})
    }
}