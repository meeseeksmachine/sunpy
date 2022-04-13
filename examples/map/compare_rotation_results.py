"""
================================
Comparing Map Rotation Functions
================================

This example will compare between the current library implementations for `sunpy.map.GenericMap.rotate`.
"""
import numpy as np
import pylab as plt

import sunpy.data.sample
import sunpy.map

###############################################################################
# Rotating a map in sunpy has a choice between two libraries: `skimage' and `scipy`
# One can also create a custom rotation function and add it, see :ref:`map_rotate_custom`.
#
# Since all these options use different algorithms, we need a basis for comparison.
#
# The problem is, defining a acceptable margin of difference in the final, rotated data product
# is difficult. One option is to use the `Symmetric Mean Absolute Percentage Difference
# <https://en.wikipedia.org/wiki/Symmetric_mean_absolute_percentage_error>`__
#
# This is a bit rudimentary, since it looks at all of the pixels in the image
# (and not just the solar disk), but it works as a quick check.


def smape(arr1, arr2):
    """
    Symmetric Mean Absolute Percentage Error

    Parameters
    ----------
    arr1 : `numpy.ndarray`
        First array to compare.
    arr2 : `numpy.ndarray`
        Second array to compare.

    Returns
    -------
    `float`
        Between 0% - 100% of average error between ``arr1`` and ``arr2``
    """
    eps = np.finfo(np.float64).eps
    return np.nanmean(np.abs(arr1 - arr2) / (np.maximum(np.abs(arr1) + np.abs(arr2), eps))) * 100

###############################################################################
# Using an HMI sample data, we will do a rotation to align the image to the north.
# We will also fix the order (to 3) for each operation.


hmi_map = sunpy.map.Map(sunpy.data.sample.HMI_LOS_IMAGE)

skimage_map = hmi_map.rotate(order=3, recenter=True, method='skimage')
scipy_map = hmi_map.rotate(order=3, recenter=True, method='scipy')

###############################################################################
# Now we will calculate the Symmetric Mean Percentage Error.

print("HMI Example")
print(f"scikit-image vs scipy {smape(skimage_map.data, scipy_map.data):.2f}%")

###############################################################################
# This essentially means that the average difference between every pixel in the
# ``skimage`` and ``scipy`` images is about 15\%, in the final rotated image.

###############################################################################
# Now for a visual comparison, the raw differences, that should highlight the differences.

fig0, ax0 = plt.subplots()
img0 = ax0.imshow(skimage_map.data - scipy_map.data, vmin=-50, vmax=50, cmap=plt.cm.seismic)
fig0.colorbar(img0)
ax0.set_title("Raw Difference: scikit-image vs scipy")

plt.show()

###############################################################################
# We can repeat this but for AIA data, using a 171 sample image.
# Since there is no rotation in the FITS header, it will just apply the same rotation to the image.
# This rotation is to set the rotation matrix to unity.

aia_map = sunpy.map.Map(sunpy.data.sample.AIA_171_IMAGE)

skimage_map = aia_map.rotate(order=3, recenter=True, method='skimage')
scipy_map = aia_map.rotate(order=3, recenter=True, method='scipy')

###############################################################################
# Now we will calculate the Symmetric Mean Percentage Error.

print("AIA 171 Example")
print(f"scikit-image vs scipy {smape(skimage_map.data, scipy_map.data):.2f}%")

###############################################################################
# This essentially means that the average difference between every pixel in the
# ``skimage`` and ``scipy`` images is about 1.9\% average difference in the
# final rotated image.

###############################################################################
# Now for a visual comparison, the raw differences, that should highlight the differences.

fig0, ax0 = plt.subplots()
img0 = ax0.imshow(skimage_map.data - scipy_map.data, vmin=-75, vmax=75, cmap=plt.cm.seismic)
fig0.colorbar(img0)
ax0.set_title("Raw Difference: scikit-image vs scipy")

plt.show()
