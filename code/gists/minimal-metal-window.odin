// Source: https://gist.github.com/Lperlind/1bb993a1c0f1acdd49080fd4852f95c5
// Minimal Cocoa Window with Metal API | By Lperlind
/*
	Minmal Cocoa Window with Metal API
	No error handling intentionally to just show the happy path
	
	IMPORTANT: you odin version needs to be using the commit edcd335 or later!
        Otherwise you will get a silent error at runtime as Cocoa would have not been linked!
*/
package minimal_metal_window

import NS "vendor:darwin/Foundation"
import MTL "vendor:darwin/Metal"
import CA "vendor:darwin/QuartzCore"

main :: proc() {
	// Setup NS app and window
	app: ^NS.Application
	wnd: ^NS.Window
	{
		app = NS.Application.sharedApplication()
		app->setActivationPolicy(.Regular)
		delegate := NS.application_delegate_register_and_alloc({
			applicationShouldTerminateAfterLastWindowClosed = proc(^NS.Application) -> NS.BOOL { return true },
		}, "app_delegate", context)
		app->setDelegate(delegate)

		frame_rect := NS.Rect { { 0, 0 }, { 800, 600 } }
		wnd = NS.Window_alloc()
		wnd->initWithContentRect(frame_rect, { .Resizable, .Closable, .Titled }, .Buffered, false)
		wnd->setTitle(NS.AT("Hello Metal"))
		wnd->makeKeyAndOrderFront(nil)
		app->activateIgnoringOtherApps(true)
	}
	defer app->release()
	defer wnd->release()

	// setup metal
	device: ^MTL.Device
	swapchain: ^CA.MetalLayer
	{
		device = MTL.CreateSystemDefaultDevice()
		swapchain = CA.MetalLayer.layer()

		swapchain->setDevice(device)
		swapchain->setPixelFormat(.BGRA8Unorm_sRGB)
		swapchain->setFramebufferOnly(true)
		swapchain->setFrame(wnd->frame())

		wnd->contentView()->setLayer(swapchain)
		wnd->setOpaque(true)
		wnd->setBackgroundColor(nil)
	}
	defer device->release()
	defer swapchain->release()

	// compile shader
	pso: ^MTL.RenderPipelineState
	{
		shader_src := `
		struct v2f {
			float4 position [[position]];
			half3 color;
		};

		v2f vertex vertex_main(uint vertex_id [[vertex_id]]) {
			float2 positions[3] = { float2(-0.5, -0.5), float2(0.0, 0.5), float2(0.5, -0.5) };
			half3 colours[3] = { half3(1.0, 0.0, 0.0), half3(0.0, 1.0, 0.0), half3(0.0, 0.0, 1.0) };

			v2f o;
			o.position = float4(positions[vertex_id], 0.0, 1.0);
			o.color = colours[vertex_id];
			return o;
		}

		half4 fragment fragment_main(v2f in [[stage_in]]) {
			return half4(in.color, 1.0);
		}
		`
		shader_src_str := NS.String.alloc()->initWithOdinString(shader_src)
		defer shader_src_str->release()

		library, err := device->newLibraryWithSource(shader_src_str, nil)
		defer library->release()

		vertex_function   := library->newFunctionWithName(NS.AT("vertex_main"))
		fragment_function := library->newFunctionWithName(NS.AT("fragment_main"))
		defer vertex_function->release()
		defer fragment_function->release()

		desc := MTL.RenderPipelineDescriptor.alloc()->init()
		defer desc->release()

		desc->setVertexFunction(vertex_function)
		desc->setFragmentFunction(fragment_function)
		desc->colorAttachments()->object(0)->setPixelFormat(.BGRA8Unorm_sRGB)

		pso, err = device->newRenderPipelineStateWithDescriptor(desc)
	}
	defer pso->release()

	// draw and present framebuffer
	{
		command_queue := device->newCommandQueue()
		defer command_queue->release()

		drawable := swapchain->nextDrawable()
		defer drawable->release()

		pass := MTL.RenderPassDescriptor.renderPassDescriptor()
		defer pass->release()

		color_attachment := pass->colorAttachments()->object(0)
		color_attachment->setClearColor(MTL.ClearColor{0.25, 0.5, 1.0, 1.0})
		color_attachment->setLoadAction(.Clear)
		color_attachment->setStoreAction(.Store)
		color_attachment->setTexture(drawable->texture())

		command_buffer := command_queue->commandBuffer()
		defer command_buffer->release()

		render_encoder := command_buffer->renderCommandEncoderWithDescriptor(pass)
		defer render_encoder->release()

		render_encoder->setRenderPipelineState(pso)
		render_encoder->drawPrimitives(.Triangle, 0, 3)

		render_encoder->endEncoding()

		command_buffer->presentDrawable(drawable)
		command_buffer->commit()
	}

	// wait for user to close the screen
	app->run()
}
