from onvif import ONVIFCamera

def media_profile_configuration():
    '''
    A media profile consists of configuration entities such as video/audio
    source configuration, video/audio encoder configuration,
    or PTZ configuration. This use case describes how to change one
    configuration entity which has been already added to the media profile.
    '''

    # Create the media service
    mycam = ONVIFCamera('192.168.0.103', 80, 'admin', 'SMSS@2022')
    media_service = mycam.create_media_service()

    profiles = media_service.GetProfiles()

    # Use the first profile and Profiles have at least one
    profile = profiles[0]  # Assuming the first profile is selected
    token = profile.token

    # Get all video encoder configurations
    configurations_list = media_service.GetVideoEncoderConfigurations()

    # Use the first profile and Profiles have at least one
    video_encoder_configuration = configurations_list[0]

    # Get video encoder configuration options
    options = media_service.GetVideoEncoderConfigurationOptions({'ProfileToken':token})
    print(options)
    # Setup stream configuration
    video_encoder_configuration.Encoding = 'H264'
    # Setup Resolution
    video_encoder_configuration.Resolution.Width = \
                    options.H264.ResolutionsAvailable[0].Width
    video_encoder_configuration.Resolution.Height = \
                    options.H264.ResolutionsAvailable[0].Height
    # Setup Quality
    video_encoder_configuration.Quality = options.QualityRange.Min
    # Setup FramRate
    video_encoder_configuration.RateControl.FrameRateLimit = \
                                    options.H264.FrameRateRange.Min
    # Setup EncodingInterval
    video_encoder_configuration.RateControl.EncodingInterval = \
                                    options.H264.EncodingIntervalRange.Min
    # Setup Bitrate
    #video_encoder_configuration.RateControl.BitrateLimit = \
                            #options.Extension.H264[0].BitrateRange[0].Min[0]
    if options.Extension is not None and options.Extension.H264 is not None and len(options.Extension.H264) > 0:
        bitrate_range = options.Extension.H264[0].BitrateRange
        if bitrate_range is not None and len(bitrate_range) > 0:
            min_bitrate = bitrate_range[0].Min[0]
            video_encoder_configuration.RateControl.BitrateLimit = min_bitrate
        else:
            raise ValueError("BitrateRange is empty or None.")
    else:
        raise ValueError("options.Extension.H264 is empty or None.")
                      

    # Create request type instance
    request = media_service.create_type('SetVideoEncoderConfiguration')
    request.Configuration = video_encoder_configuration
    # ForcePersistence is obsolete and should always be assumed to be True
    request.ForcePersistence = True

    # Set the video encoder configuration
    media_service.SetVideoEncoderConfiguration(request)

if __name__ == '__main__':
    media_profile_configuration()
