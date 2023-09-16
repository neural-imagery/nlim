"""A standalone implementation of the scalp-coupling index."""
from warnings import warn

import mne
import numpy as np
import scipy.io
from mne.preprocessing.nirs import _validate_nirs_info

picks = np.array(
    [
        0,
        16,
        1,
        17,
        2,
        18,
        3,
        19,
        4,
        20,
        5,
        21,
        6,
        22,
        7,
        23,
        8,
        24,
        9,
        25,
        10,
        26,
        11,
        27,
        12,
        28,
        13,
        29,
        14,
        30,
        15,
        31,
    ]
)


def optical_density(_data, *, verbose=None):
    r"""Convert NIRS raw data to optical density.

    Parameters
    ----------
    raw : instance of Raw
        The raw data.
    %(verbose)s

    Returns
    -------
    raw : instance of Raw
        The modified raw instance.
    """
    # raw = raw.copy().load_data()
    # _validate_type(raw, BaseRaw, "raw")
    # picks = _validate_nirs_info(raw.info, fnirs="cw_amplitude")

    # The devices measure light intensity. Negative light intensities should
    # not occur. If they do it is likely due to hardware or movement issues.
    # Set all negative values to abs(x), this also has the benefit of ensuring
    # that the means are all greater than zero for the division below.
    if np.any(_data[picks] <= 0):
        warn("Negative intensities encountered. Setting to abs(x)")
        min_ = np.inf
        for pi in picks:
            np.abs(_data[pi], out=_data[pi])
            min_ = min(min_, _data[pi].min() or min_)
        # avoid == 0
        for pi in picks:
            np.maximum(_data[pi], min_, out=_data[pi])

    for pi in picks:
        data_mean = np.mean(_data[pi])
        _data[pi] /= data_mean
        np.log(_data[pi], out=_data[pi])
        _data[pi] *= -1
        # raw.info["chs"][pi]["coil_type"] = FIFF.FIFFV_COIL_FNIRS_OD

    return _data


def scalp_coupling_index(
    _data,
    l_freq=0.7,
    h_freq=1.5,
    l_trans_bandwidth=0.3,
    h_trans_bandwidth=0.3,
    verbose=False,
):
    r"""Calculate scalp coupling index.

    This function calculates the scalp coupling index
    :footcite:`pollonini2014auditory`. This is a measure of the quality of the
    connection between the optode and the scalp.

    Parameters
    ----------
    raw : instance of Raw
        The raw data.
    %(l_freq)s
    %(h_freq)s
    %(l_trans_bandwidth)s
    %(h_trans_bandwidth)s
    %(verbose)s

    Returns
    -------
    sci : array of float
        Array containing scalp coupling index for each channel.

    References
    ----------
    .. footbibliography::
    """
    # _validate_type(raw, BaseRaw, "raw")
    # picks = _validate_nirs_info(raw.info, fnirs="od", which="Scalp coupling index")
    picks = np.array(
        [
            0,
            16,
            1,
            17,
            2,
            18,
            3,
            19,
            4,
            20,
            5,
            21,
            6,
            22,
            7,
            23,
            8,
            24,
            9,
            25,
            10,
            26,
            11,
            27,
            12,
            28,
            13,
            29,
            14,
            30,
            15,
            31,
        ]
    )

    # raw = raw.copy().pick(picks).load_data()
    zero_mask = np.std(_data, axis=-1) == 0
    filtered_data = filter(
        _data,
        l_freq=l_freq,
        h_freq=h_freq,
        l_trans_bandwidth=l_trans_bandwidth,
        h_trans_bandwidth=h_trans_bandwidth,
    )
    # filtered_data = raw.filter(
    #     l_freq,
    #     h_freq,
    #     l_trans_bandwidth=l_trans_bandwidth,
    #     h_trans_bandwidth=h_trans_bandwidth,
    #     verbose=verbose,
    # ).get_data()

    sci = np.zeros(picks.shape)
    for ii in range(0, len(picks), 2):
        with np.errstate(invalid="ignore"):
            c = np.corrcoef(filtered_data[ii], filtered_data[ii + 1])[0][1]
        if not np.isfinite(c):  # someone had std=0
            c = 0
        sci[ii] = c
        sci[ii + 1] = c
    sci[zero_mask] = 0
    sci = sci[np.argsort(picks)]  # restore original order
    return sci


def filter(
    # self,
    _data,
    l_freq,
    h_freq,
    picks=None,
    filter_length="auto",
    l_trans_bandwidth="auto",
    h_trans_bandwidth="auto",
    n_jobs=None,
    method="fir",
    iir_params=None,
    phase="zero",
    fir_window="hamming",
    fir_design="firwin",
    skip_by_annotation=("edge", "bad_acq_skip"),
    pad="edge",
    *,
    verbose=None,
):
    """Filter a subset of channels.

    Parameters
    ----------
    %(l_freq)s
    %(h_freq)s
    %(picks_all_data)s
    %(filter_length)s
    %(l_trans_bandwidth)s
    %(h_trans_bandwidth)s
    %(n_jobs_fir)s
    %(method_fir)s
    %(iir_params)s
    %(phase)s
    %(fir_window)s
    %(fir_design)s
    %(skip_by_annotation)s

        .. versionadded:: 0.16.
    %(pad_fir)s
    %(verbose)s

    Returns
    -------
    inst : instance of Epochs, Evoked, or Raw
        The filtered data.

    See Also
    --------
    mne.filter.create_filter
    mne.Evoked.savgol_filter
    mne.io.Raw.notch_filter
    mne.io.Raw.resample
    mne.filter.create_filter
    mne.filter.filter_data
    mne.filter.construct_iir_filter

    Notes
    -----
    Applies a zero-phase low-pass, high-pass, band-pass, or band-stop
    filter to the channels selected by ``picks``.
    The data are modified inplace.

    The object has to have the data loaded e.g. with ``preload=True``
    or ``self.load_data()``.

    ``l_freq`` and ``h_freq`` are the frequencies below which and above
    which, respectively, to filter out of the data. Thus the uses are:

        * ``l_freq < h_freq``: band-pass filter
        * ``l_freq > h_freq``: band-stop filter
        * ``l_freq is not None and h_freq is None``: high-pass filter
        * ``l_freq is None and h_freq is not None``: low-pass filter

    ``self.info['lowpass']`` and ``self.info['highpass']`` are only
    updated with picks=None.

    .. note:: If n_jobs > 1, more memory is required as
                ``len(picks) * n_times`` additional time points need to
                be temporarily stored in memory.

    For more information, see the tutorials
    :ref:`disc-filtering` and :ref:`tut-filter-resample` and
    :func:`mne.filter.create_filter`.

    .. versionadded:: 0.15
    """
    # from .io import BaseRaw
    from mne.annotations import _annotations_starts_stops

    # _check_preload(self, "inst.filter")
    if pad is None and method != "iir":
        pad = "edge"
    # update_info, picks = _filt_check_picks(self.info, picks, l_freq, h_freq)
    picks = np.array(
        [
            0,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
            27,
            28,
            29,
            30,
            31,
        ]
    )
    # print(f"custom {picks = }")
    # if isinstance(self, BaseRaw):
    #     # Deal with annotations
    #     onsets, ends = _annotations_starts_stops(
    #         self, skip_by_annotation, invert=True
    #     )
    #     logger.info(
    #         "Filtering raw data in %d contiguous segment%s"
    #         % (len(onsets), _pl(onsets))
    #     )
    # else:
    onsets, ends = np.array([0]), np.array([_data.shape[1]])
    # print(f"custom {onsets = }, {ends  = }")
    max_idx = (ends - onsets).argmax()
    for si, (start, stop) in enumerate(zip(onsets, ends)):
        # print(si)
        # Only output filter params once (for info level), and only warn
        # once about the length criterion (longest segment is too short)
        use_verbose = verbose if si == max_idx else "error"
        # print("custo start stop data = {}".format(_data[:, start:stop]))
        # print("custom all params", l_freq, h_freq, picks, filter_length, l_trans_bandwidth,  h_trans_bandwidth,
        #     n_jobs,
        #     method,
        #     iir_params,
        #     True,
        #     phase,
        #     fir_window,
        #     fir_design,
        #     pad,
        #     use_verbose,)
        filtered = mne.filter.filter_data(
            _data[:, start:stop],
            10.0,
            # self.info["sfreq"],
            l_freq,
            h_freq,
            picks,
            filter_length,
            l_trans_bandwidth,
            h_trans_bandwidth,
            n_jobs,
            method,
            iir_params,
            copy=True,
            phase=phase,
            fir_window=fir_window,
            fir_design=fir_design,
            pad="reflect_limited",
            verbose=use_verbose,
        )
        # print("custom filtered = {}".format(filtered))
        # break
    # update info if filter is applied to all data channels,
    # and it's not a band-stop filter
    # _filt_update_info(self.info, update_info, l_freq, h_freq)
    return filtered


if __name__ == "__main__":
    mar = mne.io.read_raw_snirf("./mar.snirf")
    mar_raw_od = mne.preprocessing.nirs.optical_density(mar)
    from mne.filter import _filt_check_picks

    l_freq = 0.7
    h_freq = 1.5
    l_trans_bandwidth = 0.3
    h_trans_bandwidth = 0.3
    verbose = False
    # picks=None
    # update_info, picks = _filt_check_picks(mar_raw_od.info, picks, l_freq, h_freq)
    # picks = _validate_nirs_info(mar_raw_od.info, fnirs="od", which="Scalp coupling index")
    # breakpoint()
    mar_sci = mne.preprocessing.nirs.scalp_coupling_index(mar_raw_od)
    fig, ax = plt.subplots()
    ax.hist(mar_sci)
    ax.set(xlabel="Scalp Coupling Index", ylabel="Count", xlim=[0, 1])
    data = scipy.io.loadmat("./mar.nirs")["d"].T
    assert np.allclose(data, mar.load_data()._data)
    raw_od = optical_density(data)
    assert np.allclose(mar_raw_od._data, raw_od)
    # sci = scalp_coupling_index()
    filtered = filter(
        raw_od,
        l_freq=l_freq,
        h_freq=h_freq,
        l_trans_bandwidth=l_trans_bandwidth,
        h_trans_bandwidth=h_trans_bandwidth,
        verbose=False,
    )
    # print(f'cusetom {filtered = }')
    picks = _validate_nirs_info(
        mar_raw_od.info, fnirs="od", which="Scalp coupling index"
    )
    # print(f"{picks = }")
    # breakpoint()
    raw = mar_raw_od.copy().pick(list(picks)).load_data()
    mar_filtered = raw.filter(
        l_freq=l_freq,
        h_freq=h_freq,
        l_trans_bandwidth=l_trans_bandwidth,
        h_trans_bandwidth=h_trans_bandwidth,
        verbose=verbose,
    ).get_data()

    sci = scalp_coupling_index(raw_od)
