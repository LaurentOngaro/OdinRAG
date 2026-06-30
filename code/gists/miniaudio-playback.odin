// Source: https://gist.github.com/p1xelHer0/abed4728096ea3a88af7802cbe46cf08
// Play audio files from memory with Odin #load | By p1xelHer0
package audio

import "core:fmt"

// https://miniaud.io/docs/
import ma "vendor:miniaudio"

// 0 - Use native channel count of the device
AUDIO_CHANNELS :: 0
AUDIO_SAMPLE_RATE :: 0
// miniaudio supports decoding WAV, MP3 and FLAC out of the box
AUDIO_FILE :: #load("./audio.wav")

// Engine - high level API
engine: ma.engine
// We will use the decoder to create a sound
// NOTE: Keep your decoder alive for the life of your sound object
decoder: ma.decoder
// The sound we will play
sound: ma.sound

main :: proc() {
    // We'll use the engine API to play our sound
    engine_config := ma.engine_config_init()
    engine_config.channels = AUDIO_CHANNELS
    engine_config.sampleRate = AUDIO_SAMPLE_RATE
    engine_config.listenerCount = 1

    engine_init_result := ma.engine_init(&engine_config, &engine)
    if engine_init_result != .SUCCESS {
        fmt.panicf("failed to init miniaudio engine: %v", engine_init_result)
    }
    engine_start_result := ma.engine_start(&engine)
    if engine_start_result != .SUCCESS {
        fmt.panicf("failed to start miniaudio engine: %v", engine_start_result)
    }

    // Configure our decoder
    decoder_config := ma.decoder_config_init(
        outputFormat = .f32,
        outputChannels = AUDIO_CHANNELS,
        outputSampleRate = AUDIO_SAMPLE_RATE,
    )
    // This example uses a WAV file
    // Form the docs:
    // When loading a decoder, miniaudio uses a trial and error technique to find the appropriate decoding backend. This can be unnecessarily inefficient if the type is already known. In this case you can use encodingFormat variable in the device config to specify a specific encoding format you want to decode: 
    decoder_config.encodingFormat = .wav

    // Initialize a decoder from memory, decoding our `#load`-ed audio file
    decoder_result := ma.decoder_init_memory(
        pData = raw_data(AUDIO_FILE),
        dataSize = len(AUDIO_FILE),
        pConfig = &decoder_config,
        pDecoder = &decoder,
    )
    if decoder_result != .SUCCESS {
        fmt.eprintf("failed to init decoder: %v", decoder_result)
    }

    // A `decoder` is a `data_source` thus we can init a sound from it
    sound_result := ma.sound_init_from_data_source(
        pEngine = &engine,
        // Pass the decoders data_source
        pDataSource = decoder.ds.pCurrent,
        flags = 0,
        pGroup = nil,
        pSound = &sound,
    )
    if sound_result != .SUCCESS {
        fmt.panicf("failed to init sound file from memory: %v", sound_result)
    }

    // Play the sound using the high level API of the engine
    ma.sound_start(&sound)

    // Don't terminate so we can listen to the sound lol
    for {}
}