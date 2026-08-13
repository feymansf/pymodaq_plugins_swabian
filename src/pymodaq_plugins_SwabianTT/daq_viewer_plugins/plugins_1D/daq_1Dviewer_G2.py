import numpy as np

from pymodaq_utils.utils import ThreadCommand
from pymodaq_data.data import DataToExport, Axis
from pymodaq_gui.parameter import Parameter

from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.data import DataFromPlugins

import TimeTagger


class DAQ_1DViewer_G2(DAQ_Viewer_base):

    params = comon_parameters + [
        {'title': 'Channel 1:', 'name': 'channel_1', 'type': 'int', 'value': 1},
        {'title': 'Channel 2:', 'name': 'channel_2', 'type': 'int', 'value': 2},
        {'title': 'Bin width (ps):', 'name': 'bin_width_ps', 'type': 'int', 'value': 100},
        {'title': 'Number of bins:', 'name': 'n_bins', 'type': 'int', 'value': 1000},
    ]

    def ini_attributes(self):
        self.controller = None
        self.correlation = None
        self.x_axis = None

    def commit_settings(self, param: Parameter):
        if param.name() in ['channel_1', 'channel_2', 'bin_width_ps', 'n_bins']:
            if self.correlation is not None:
                self.correlation.stop()
                self.correlation = None
                self.init_correlation()

    def init_correlation(self):
        channel_1 = self.settings['channel_1']
        channel_2 = self.settings['channel_2']
        bin_width_ps = self.settings['bin_width_ps']
        n_bins = self.settings['n_bins']

        self.correlation = TimeTagger.Correlation(self.controller, channel_1=channel_1, channel_2=channel_2, binwidth=bin_width_ps, n_bins=n_bins)

        self.correlation.start()

        tau = np.asarray(self.correlation.getIndex(), dtype=float)

        self.x_axis = Axis(data=tau, label='Delay', units='ps', index=0)

        self.dte_signal_temp.emit(DataToExport(name='TimeTagger G2', data=[
            DataFromPlugins(name='Correlation', data=[np.zeros_like(tau)], dim='Data1D', labels=['Correlation'], axes=[self.x_axis])
        ]))

    def ini_detector(self, controller=None):
        if self.is_master:
            self.controller = TimeTagger.createTimeTagger()
        else:
            self.controller = controller

        self.init_correlation()

        info = 'Swabian TimeTagger g2 initialized'
        initialized = True

        return info, initialized

    def close(self):
        if self.correlation is not None:
            self.correlation.stop()
            self.correlation = None

        if self.is_master and self.controller is not None:
            TimeTagger.freeTimeTagger(self.controller)
            self.controller = None

    def grab_data(self, Naverage=1, **kwargs):
        data = np.asarray(self.correlation.getData(), dtype=float)

        self.dte_signal.emit(DataToExport('TimeTagger G2', data=[
            DataFromPlugins(name='Correlation', data=[data], dim='Data1D', labels=['Correlation'], axes=[self.x_axis.copy()])
        ]))

    def stop(self):
        if self.correlation is not None:
            self.correlation.stop()

        self.emit_status(ThreadCommand('Update_Status', ['TimeTagger correlation stopped']))
        return ''


if __name__ == '__main__':
    main(__file__)