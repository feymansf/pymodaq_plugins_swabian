import numpy as np

from pymodaq_utils.utils import ThreadCommand
from pymodaq_data.data import DataToExport
from pymodaq_gui.parameter import Parameter

from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.data import DataFromPlugins

#  Import Timetagger to communicate with timetagger

import TimeTagger

class DAQ_0DViewer_Counter(DAQ_Viewer_base):
    """ Instrument plugin class for a OD viewer.
    
    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Viewer module through inheritance via
    DAQ_Viewer_base. It makes a bridge between the DAQ_Viewer module and the Python wrapper of a particular instrument.

    TODO Complete the docstring of your plugin with:
        * The set of instruments that should be compatible with this instrument plugin.
        * With which instrument it has actually been tested.
        * The version of PyMoDAQ during the test.
        * The version of the operating system.
        * Installation instructions: what manufacturer’s drivers should be installed to make it run?

    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library.
         
    # TODO add your particular attributes here if any

    """
    params = comon_parameters+[ {'title': 'Channel 1:', 'name': 'channel_1', 'type': 'int', 'value': 1},
        {'title': 'Channel 2:', 'name': 'channel_2', 'type': 'int', 'value': 2},
        {'title': 'Bin width (ms):', 'name': 'bin_width_ms', 'type': 'float', 'value': 10.0, 'min': 0.001},
        ]

    def ini_attributes(self):
        #  TODO declare the type of the wrapper (and assign it to self.controller) you're going to use for easy
        #  autocompletion
        self.controller = None
        self.counter = None
        #TODO declare here attributes you want/need to init with a default value
        pass

    def commit_settings(self, param: Parameter):
        if param.name() in ['channel_1', 'channel_2', 'bin_width_ms']:
        if self.counter is not None:
            self.counter.stop()
            self.counter = None

        channel_1 = self.settings['channel_1']
        channel_2 = self.settings['channel_2']
        bin_width_ms = self.settings['bin_width_ms']
        binwidth_ps = int(bin_width_ms * 1e9)

        self.counter = TimeTagger.Counter(self.controller, channels=[channel_1, channel_2], binwidth=binwidth_ps, n_values=1)
        self.counter.start()

    def ini_detector(self, controller=None):
         if controller is None:
            self.controller = TimeTagger.createTimeTagger()
         else:
            self.controller = controller

         channel_1 = self.settings['channel_1']
         channel_2 = self.settings['channel_2']
         bin_width_ms = self.settings['bin_width_ms']

         binwidth_ps = int(bin_width_ms * 1e9)

         self.counter = TimeTagger.Counter(
            self.controller,
            channels=[channel_1, channel_2],
            binwidth=binwidth_ps,
            n_values=1
         )

         self.counter.start()

         info = 'Swabian TimeTagger Counter initialized'
         initialized = True

        # TODO for your custom plugin (optional) initialize viewers panel with the future type of data


         return info, initialized

    def close(self):
         if self.counter is not None:
            self.counter.stop()
            self.counter = None
         if self.controller is not None:
             TimeTagger.freeTimeTagger(self.controller)
             self.controller = None
             
    def grab_data(self, Naverage=1, **kwargs):
        data = self.counter.getData()

        bin_width_ms = self.settings['bin_width_ms']
        bin_width_s = bin_width_ms * 1e-3

        counts_ch1 = data[0, -1]
        counts_ch2 = data[1, -1]

        cps_ch1 = counts_ch1 / bin_width_s
        cps_ch2 = counts_ch2 / bin_width_s

        self.dte_signal.emit(
            DataToExport(
                'TimeTagger Counter',
                data=[
                    DataFromPlugins(
                        name='PL Counter',
                        data=[
                            np.array([cps_ch1]),
                            np.array([cps_ch2])
                        ],
                        dim='Data0D',
                        labels=['Channel 1', 'Channel 2']
                    )
                ]
            )
        )


    def callback(self):
        """optional asynchrone method called when the detector has finished its acquisition of data"""
        data_tot = self.controller.your_method_to_get_data_from_buffer()
        self.dte_signal.emit(DataToExport(name='myplugin',
                                          data=[DataFromPlugins(name='Mock1', data=data_tot,
                                                                dim='Data0D', labels=['dat0', 'data1'])]))

    def stop(self):
        """Stop the current grab hardware wise if necessary"""
        ## TODO for your custom plugin
        if self.counter is not None:
            self.counter.stop()
        return ''


if __name__ == '__main__':
    main(__file__)
