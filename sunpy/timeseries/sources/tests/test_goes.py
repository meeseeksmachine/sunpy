import matplotlib.pyplot as plt
import numpy as np
import pytest

from astropy import units as u

import sunpy.timeseries
from sunpy.data.test import get_test_filepath
from sunpy.tests.helpers import figure_test
from sunpy.util.exceptions import SunpyUserWarning

goes_fits_filepath_com = get_test_filepath('go1520120601.fits.gz')
goes13_filepath_nc = get_test_filepath('sci_gxrs-l2-irrad_g13_d20170901_truncated.nc')
goes15_filepath_nc = get_test_filepath('sci_gxrs-l2-irrad_g15_d20131028_truncated.nc')
goes17_filepath_nc = get_test_filepath('sci_xrsf-l2-flx1s_g17_d20201016_truncated.nc')
goes15_1m_avg_filepath = get_test_filepath('sci_xrsf-l2-avg1m_g15_d20190102_truncated.nc')
goes16_1m_avg_filepath = get_test_filepath('sci_xrsf-l2-avg1m_g16_d20210101_truncated.nc')
goes13_leap_second_filepath = get_test_filepath('goes_13_leap_second.nc')


@pytest.mark.parametrize("goes_nc_files",
                         [goes_fits_filepath_com,
                          goes13_filepath_nc,
                          goes15_filepath_nc,
                          goes17_filepath_nc,
                          goes15_1m_avg_filepath,
                          goes16_1m_avg_filepath])
def test_implicit_goes(goes_nc_files):
    # Test implicit for all files
    ts_goes = sunpy.timeseries.TimeSeries(goes_nc_files, source='XRS')
    assert isinstance(ts_goes, sunpy.timeseries.sources.goes.XRSTimeSeries)


@pytest.mark.parametrize("goes_nc_files, sat_no",
                         [(goes_fits_filepath_com, 'GOES-15'),
                          (goes13_filepath_nc, 'GOES-13'),
                          (goes15_filepath_nc, 'GOES-15'),
                          (goes17_filepath_nc, 'GOES-17'),
                          (goes15_1m_avg_filepath, 'GOES-15'),
                          (goes16_1m_avg_filepath, 'GOES-16')])
def test_implicit_goes_satno(goes_nc_files, sat_no):
    # Test that satellite number is correctly parsed from files
    ts_goes = sunpy.timeseries.TimeSeries(goes_nc_files, source='XRS')
    assert ts_goes.observatory == sat_no


def test_implicit_goes_satno_missing():
    # Test a GOES TimeSeries for a missing satellite number
    ts_goes = sunpy.timeseries.TimeSeries(goes17_filepath_nc)
    del ts_goes.meta.metas[0]['id']
    assert ts_goes.observatory is None


def test_columns_units():
    # Test that all columns have associated units
    ts_goes = sunpy.timeseries.TimeSeries(goes17_filepath_nc, source='XRS')
    assert np.all([isinstance(unit_val, u.UnitBase) for unit_val in ts_goes.units.values()])


def test_goes_netcdf_time_parsing15():
    # Testing to make sure the time is correctly parsed (to ignore leap seconds)
    # Tests for 13, 14, 15
    ts_goes = sunpy.timeseries.TimeSeries(goes15_filepath_nc, source="XRS")
    assert ts_goes.index[0].strftime("%Y-%m-%d %H:%M:%S.%f") == '2013-10-28 00:00:01.385000'


def test_goes_netcdf_time_parsing17():
    # Testing to make sure the time is correctly parsed (to ignore leap seconds)
    # Tests for GOES-R (16, 17)
    ts_goes = sunpy.timeseries.TimeSeries(goes17_filepath_nc, source="XRS")
    assert ts_goes.index[0].strftime("%Y-%m-%d %H:%M:%S.%f") == '2020-10-16 00:00:00.476771'


def test_goes_leap_seconds():
    # Test for case when leap second present
    with pytest.warns(SunpyUserWarning, match="There is one leap second timestamp present in: goes_13_leap_second"):
        ts = sunpy.timeseries.TimeSeries(goes13_leap_second_filepath)
    assert str(ts.index[-1]) == '2015-06-30 23:59:59.999000'


def test_goes_plot_column(goes_test_ts):
    ax = goes_test_ts.plot()
    assert len(ax.lines) == 2
    assert '0.5--4.0' == ax.lines[0].get_label().split()[0]


@pytest.mark.remote_data
def test_goes_remote():
    # Older format file
    goes = sunpy.timeseries.TimeSeries(
        'https://umbra.nascom.nasa.gov/goes/fits/1986/go06860129.fits')
    assert isinstance(goes, sunpy.timeseries.sources.goes.XRSTimeSeries)
    # Newer format
    goes = sunpy.timeseries.TimeSeries(
        'https://umbra.nascom.nasa.gov/goes/fits/2018/go1520180626.fits')
    assert isinstance(goes, sunpy.timeseries.sources.goes.XRSTimeSeries)
    # Testing NOAA served data
    goes = sunpy.timeseries.TimeSeries(
        'https://data.ngdc.noaa.gov/platforms/solar-space-observing-satellites/goes/goes16/l2/data/xrsf-l2-flx1s_science/2022/05/sci_xrsf-l2-flx1s_g16_d20220506_v2-2-0.nc')
    assert isinstance(goes, sunpy.timeseries.sources.goes.XRSTimeSeries)


@figure_test
def test_goes_peek(goes_test_ts):
    goes_test_ts.peek()


@figure_test
def test_goes_ylim(goes_test_ts):
    # Check that y-limits of the shared flare category axis are linked
    # to the LH side y-limits.
    fig, ax = plt.subplots()
    goes_test_ts.plot(ax)
    ax.set_ylim(1e-7, 1e-5)
