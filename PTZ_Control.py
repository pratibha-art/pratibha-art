import sys
from onvif import ONVIFCamera
from time import sleep

IP = "192.168.0.103"  # Camera IP address
PORT = 80  # Port
USER = "admin"  # Username
PASS = "SMSS@2022"  # Password

class ptzControl(object):
    def __init__(self):
        super(ptzControl, self).__init__()
        self.mycam = ONVIFCamera(IP, PORT, USER, PASS)
        # create media service object
        self.media = self.mycam.create_media_service()
        # Get target profile
        self.media_profile = self.media.GetProfiles()[0]
        # Use the first profile and Profiles have at least one
        token = self.media_profile.token
        # PTZ controls  -------------------------------------------------------------
        self.ptz = self.mycam.create_ptz_service()
        # Get available PTZ services
        request = self.ptz.create_type('GetServiceCapabilities')
        Service_Capabilities = self.ptz.GetServiceCapabilities(request)
        # Get PTZ status
        status = self.ptz.GetStatus({'ProfileToken': token})  

        # Get PTZ configuration options for getting option ranges
        request = self.ptz.create_type('GetConfigurationOptions')
        request.ConfigurationToken = self.media_profile.PTZConfiguration.token
        ptz_configuration_options = self.ptz.GetConfigurationOptions(request)  

        # get continuousMove request -- requestc
        self.requestc = self.ptz.create_type('ContinuousMove')
        self.requestc.ProfileToken = self.media_profile.token
        if self.requestc.Velocity is None:
            self.requestc.Velocity = self.ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position
            self.requestc.Velocity.PanTilt.space = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].URI
            self.requestc.Velocity.Zoom.space = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].URI  

        # get absoluteMove request -- requesta
        self.requesta = self.ptz.create_type('AbsoluteMove')
        self.requesta.ProfileToken = self.media_profile.token
        if self.requesta.Position is None:
            self.requesta.Position = self.ptz.GetStatus(
                {'ProfileToken': self.media_profile.token}).Position
        if self.requesta.Speed is None:
            self.requesta.Speed = self.ptz.GetStatus(
                {'ProfileToken': self.media_profile.token}).Position  

        # get relativeMove request -- requestr
        self.requestr = self.ptz.create_type('RelativeMove')
        self.requestr.ProfileToken = self.media_profile.token
        if self.requestr.Translation is None:
            self.requestr.Translation = self.ptz.GetStatus(
                {'ProfileToken': self.media_profile.token}).Position
            self.requestr.Translation.PanTilt.space = ptz_configuration_options.Spaces.RelativePanTiltTranslationSpace[0].URI
            self.requestr.Translation.Zoom.space = ptz_configuration_options.Spaces.RelativeZoomTranslationSpace[0].URI
        if self.requestr.Speed is None:
            self.requestr.Speed = self.ptz.GetStatus(
                {'ProfileToken': self.media_profile.token}).Position  

        self.requests = self.ptz.create_type('Stop')
        self.requests.ProfileToken = self.media_profile.token
        self.requestp = self.ptz.create_type('SetPreset')
        self.requestp.ProfileToken = self.media_profile.token
        self.requestg = self.ptz.create_type('GotoPreset')
        self.requestg.ProfileToken = self.media_profile.token
        self.stop()  

    # Stop pan, tilt and zoom
    def stop(self):
        self.requests.PanTilt = True
        self.requests.Zoom = True
        self.ptz.Stop(self.requests)  

    # Continuous move functions
    def perform_move(self, requestc):
        # Start continuous move
        ret = self.ptz.ContinuousMove(requestc)  

    def move_tilt(self, velocity):
        self.requestc.Velocity.PanTilt.x = 0.0
        self.requestc.Velocity.PanTilt.y = velocity
        self.perform_move(self.requestc)  

    def move_pan(self, velocity):
        self.requestc.Velocity.PanTilt.x = velocity
        self.requestc.Velocity.PanTilt.y = 0.0
        self.perform_move(self.requestc)  

    def move_continuous(self, pan, tilt):
        self.requestc.Velocity.PanTilt.x = pan
        self.requestc.Velocity.PanTilt.y = tilt
        self.perform_move(self.requestc)  

    def zoom(self, velocity):
        self.requestc.Velocity.Zoom.x = velocity
        self.perform_move(self.requestc) 

    def zoom_relative(self, zoom, velocity):
        self.requestr.Translation.PanTilt.x = 0
        self.requestr.Translation.PanTilt.y = 0
        self.requestr.Translation.Zoom.x = zoom
        self.requestr.Speed.PanTilt.x = 0
        self.requestr.Speed.PanTilt.y = 0
        self.requestr.Speed.Zoom.x = velocity
        ret = self.ptz.RelativeMove(self.requestr)  
    
    # Absolute move functions
    def move_abspantilt(self, pan, tilt, velocity, zoom):
        self.requesta.Position.PanTilt.x = pan
        self.requesta.Position.PanTilt.y = tilt
        self.requesta.Speed.PanTilt.x = velocity
        self.requesta.Speed.PanTilt.y = velocity
        self.requesta.Position.Zoom.x = zoom
        self.requesta.Speed.Zoom.x = velocity
        ret = self.ptz.AbsoluteMove(self.requesta) 

    # Sets preset set, query, and go to
    def set_preset(self, name):
        self.requestp.PresetName = name
        self.requestp.PresetToken = '1'
        self.preset = self.ptz.SetPreset(self.requestp)  # returns the PresetToken  

    def get_preset(self):
        self.ptzPresetsList = self.ptz.GetPresets(self.requestc)  

    def goto_preset(self):
        self.requestg.PresetToken = '1'
        self.ptz.GotoPreset(self.requestg)


if __name__ == '__main__':
    ptz = ptzControl()

    # Obtain desired pan, tilt, and zoom as input from the user
    pan_i = float(input("Give the desired pan: "))
    tilt_i = float(input("Give the desired tilt: "))
    zoom_i = float(input("Give the desired zoom: "))
    
    # Normalize pan
    normalized_pan = (pan_i / 360) * 2 - 1
    
    # Normalize tilt
    normalized_tilt = ((tilt_i + 15) / 105) * 2 - 1
    
    # Normalize zoom
    normalized_zoom = zoom_i / 32
    
    # Specify the desired pan, tilt, zoom velocities for continuous movement
    pan_velocity = 1.0  # Example value, adjust as needed
    tilt_velocity = 1.0  # Example value, adjust as needed
    zoom_velocity = 1.0  # Example value, adjust as needed
    
    # Perform absolute move to the desired position
    ptz.move_abspantilt(normalized_pan, normalized_tilt, pan_velocity, normalized_zoom)
    
    # Wait for the camera to reach the desired position
    sleep(5)
    print ("Position reached")
    # Perform relative zoom with the desired zoom velocity
    #ptz.zoom_relative(normalized_zoom, zoom_velocity)
    
    # Wait for the camera to finish the relative zoom movement
    #sleep(5)
    
    # Stop the camera movement
    ptz.stop()
