from pymodaq.utils.daq_utils import ThreadCommand
from pymodaq.utils.data import DataFromPlugins, Axis, DataToExport
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.parameter import Parameter


from pymodaq_plugins_baslercam.hardware.basler import Camera


class DAQ_2DViewer_BaslerCam(DAQ_Viewer_base):
    """ Instrument plugin class for basler cameras.
        
        This plugin is to be used with an acA1920-40gm camera, though it like is compatible with others.
    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library.
         

    """
    params = comon_parameters + [
        {'title': 'Camera:', 'name': 'camera_list', 'type': 'list', 'limits': []},
        {'title': 'Camera model:', 'name': 'camera_info', 'type': 'str', 'value': '', 'readonly': True},
        {'title': 'Timing', 'name': 'timing_opts', 'type': 'group', 'children':
            [{'title': 'Exposure Time (ms)', 'name': 'exposure_time', 'type': 'int', 'value': 1},
             {'title': 'Compute FPS', 'name': 'fps_on', 'type': 'bool', 'value': True},
             {'title': 'FPS', 'name': 'fps', 'type': 'float', 'value': 0.0, 'readonly': True}]
         },
        {'title': 'Automatic exposure:', 'name': 'auto_exposure', 'type': 'bool', 'value': False},
        {'title': 'Gain (dB)', 'name': 'gain', 'type': 'float', 'value': 0, 'limits': [0, 239]},

    ]

    def ini_attributes(self):
        self.controller: Camera = None


        #self.x_axis = None
        #self.y_axis = None
        #TODO default values?

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        # TODO for your custom plugin
        if param.name() == "a_parameter_you've_added_in_self.params":
            self.controller.your_method_to_apply_this_param_change()
        #elif ...

    def init_controller(self) -> Camera:
        camera_list = [cam.GetFriendlyName() for cam in Camera.list_cameras()]
        params[next((i for i, item in enumerate(params) if item["name"] == "camera_list"), None)]['limits'] = camera_list
        friendly_name = self.settings["camera_list"]
        self.emit_status(ThreadCommand('Update_Status', [f"Trying to connect to {friendly_name}", 'log']))
        camera_list = Camera.list_cameras()
        for cam in camera_list:
            if cam.GetFriendlyName() == friendly_name:
                name = cam.GetFullName()
                return Camera(name=name, callback=self.callback)
        self.emit_status(ThreadCommand('Update_Status', ["Camera not found", 'log']))
        raise ValueError(f"Camera with name {friendly_name} not found anymore.")

    def ini_detector(self, controller=None):
        """Detector communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator/detector by controller
            (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """
        self.ini_detector_init(old_controller=controller,
                               new_controller=self.init_controller())

        ## TODO for your custom plugin
        # get the x_axis (you may want to to this also in the commit settings if x_axis may have changed
        data_x_axis = self.controller.your_method_to_get_the_x_axis()  # if possible
        self.x_axis = Axis(data=data_x_axis, label='', units='', index=1)

        # get the y_axis (you may want to to this also in the commit settings if y_axis may have changed
        data_y_axis = self.controller.your_method_to_get_the_y_axis()  # if possible
        self.y_axis = Axis(data=data_y_axis, label='', units='', index=0)

        ## TODO for your custom plugin. Initialize viewers pannel with the future type of data
        self.dte_signal_temp.emit(DataToExport('myplugin',
                                               data=[DataFromPlugins(name='Mock1', data=["2D numpy array"],
                                                                     dim='Data2D', labels=['dat0'],
                                                                     axes=[self.x_axis, self.y_axis]), ]))

        info = "Whatever info you want to log"
        initialized = True
        return info, initialized

    def close(self):
        """Terminate the communication protocol"""
        ## TODO for your custom plugin
        raise NotImplemented  # when writing your own plugin remove this line
        #  self.controller.your_method_to_terminate_the_communication()  # when writing your own plugin replace this line

    def grab_data(self, Naverage=1, **kwargs):
        """Start a grab from the detector

        Parameters
        ----------
        Naverage: int
            Number of hardware averaging (if hardware averaging is possible, self.hardware_averaging should be set to
            True in class preamble and you should code this implementation)
        kwargs: dict
            others optionals arguments
        """
        ## TODO for your custom plugin: you should choose EITHER the synchrone or the asynchrone version following

        ##synchrone version (blocking function)
        data_tot = self.controller.your_method_to_start_a_grab_snap()
        self.dte_signal.emit(DataToExport('myplugin',
                                          data=[DataFromPlugins(name='Mock1', data=data_tot,
                                                                dim='Data2D', labels=['label1'],
                                                                x_axis=self.x_axis,
                                                                y_axis=self.y_axis), ]))

        ##asynchrone version (non-blocking function with callback)
        self.controller.your_method_to_start_a_grab_snap(self.callback)
        #########################################################

    def callback(self):
        """optional asynchrone method called when the detector has finished its acquisition of data"""
        data_tot = self.controller.your_method_to_get_data_from_buffer()
        self.dte_signal.emit(DataToExport('myplugin',
                                          data=[DataFromPlugins(name='Mock1', data=data_tot,
                                                                dim='Data2D', labels=['label1'],
                                                                x_axis=self.x_axis,
                                                                y_axis=self.y_axis), ]))
    def stop(self):
        """Stop the current grab hardware wise if necessary"""
        ## TODO for your custom plugin
        raise NotImplemented  # when writing your own plugin remove this line
        self.controller.your_method_to_stop_acquisition()  # when writing your own plugin replace this line
        self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))
        ##############################
        return ''


if __name__ == '__main__':
    main(__file__)
