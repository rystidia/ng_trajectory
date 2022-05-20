#!/usr/bin/env python3.6
# main.py
"""Penalize the incorrect solution by distance to the segments.
"""
######################
# Imports & Globals
######################

import numpy

import ng_trajectory.plot as ngplot

from ng_trajectory.interpolators.utils import pointDistance, trajectoryClosest, trajectoryClosestIndex
from ng_trajectory.segmentators.utils import *

from typing import List


# Global variables
DEBUG = False
MAP = None
MAP_ORIGIN = None
MAP_GRID = None


# Parameters
from ng_trajectory.parameter import *
P = ParameterList()
P.createAdd("debug", False, bool, "Whether debug plot is ought to be shown.", "Init.")


######################
# Functions
######################

def init(start_points: numpy.ndarray, map: numpy.ndarray, map_origin: numpy.ndarray, map_grid: float, map_last: numpy.ndarray, **kwargs) -> None:
    """Initialize penalizer.

    Arguments:
    start_points -- initial line on the track, should be a centerline, nx2 numpy.ndarray
    """
    global DEBUG, MAP, MAP_ORIGIN, MAP_GRID, BORDERLINES

    # Save the grid map for later usage
    MAP = map_last.copy()
    MAP_ORIGIN = map_origin
    MAP_GRID = map_grid


    # Update parameters
    P.updateAll(kwargs)


    # Debug is used for showing extra content
    DEBUG = P.getValue("debug")


def penalize(points: numpy.ndarray, candidate: List[numpy.ndarray], valid_points: numpy.ndarray, grid: float, penalty: float = 100, **overflown) -> float:
    """Get a penalty for the candidate solution based on number of incorrectly placed points.

    Arguments:
    points -- points to be checked, nx(>=2) numpy.ndarray
    candidate -- raw candidate (non-interpolated points), m-list of 1x2 numpy.ndarray
    valid_points -- valid area of the track, px2 numpy.ndarray
    grid -- when set, use this value as a grid size, otherwise it is computed, float
    penalty -- constant used for increasing the penalty criterion, float, default 100
    **overflown -- arguments not caught by previous parts

    Returns:
    rpenalty -- value of the penalty, 0 means no penalty, float
    """

    # Use the grid or compute it
    _grid = grid if grid else gridCompute(points)

    _dists = []

    _invalid_ids = []

    # 1. Find invalid points
    for _ip, _p in enumerate(points):
        # Check whether the point is invalid (i.e., there is not a single valid point next to it).
        if not numpy.any(numpy.all(numpy.abs( numpy.subtract(valid_points, _p[:2]) ) < _grid, axis = 1)):
            _invalid_ids.append(_ip)

            _closest = trajectoryClosest(valid_points, _p)

            _dists.append(
                pointDistance(
                    _closest,
                    _p
                )
            )

            if DEBUG:
                ngplot.pointsPlot(numpy.vstack((_closest[:2], _p[:2])))


    # 2. Find edges of the track area
    _edge_pairs = []

    for invalid_id in _invalid_ids:
        for _i in [-1, 1]:
            if (invalid_id + _i) % len(points) not in _invalid_ids:
                _edge_pairs.append((invalid_id, (invalid_id + _i) % len(points)))


    # 3. Find closest valid point on each edge
    _edges = []
    _discovered = []

    for out, inside in _edge_pairs:
        # a. Compute center point on the edge
        _center_point = (points[out] + points[inside]) / 2

        # b. Find closest valid point
        _close_index = trajectoryClosestIndex(valid_points, _center_point)
        _close_point = valid_points[_close_index, :]


        # c. Find closest border
        while not borderCheck(pointToMap(_close_point)):

            _distances = numpy.subtract(valid_points[:, :2], _close_point[:2])

            _temp_close_point = None

            for _area_index in sorted(numpy.argwhere(
                numpy.hypot(_distances[:, 0], _distances[:, 1]) <= numpy.hypot(_grid[0], _grid[1])
            ), key = lambda x: pointDistance(valid_points[x[0], :2], points[out])):
                if _area_index[0] == _close_index:
                    continue

                _is_border_point = borderCheck(pointToMap(valid_points[_area_index[0], :2]))

                if _temp_close_point is None or (not _temp_close_point[0] and _is_border_point):
                    _temp_close_point = (_is_border_point, valid_points[_area_index[0], :2])

                _discovered.append((
                    valid_points[_area_index[0], :2],
                    _is_border_point
                ))


            _close_point = _temp_close_point[1]


        _edges.append(
            _close_point
        )


    if DEBUG:
        if len(_discovered) > 0:
            ngplot.pointsScatter(numpy.asarray([point for point, border in _discovered]), color=[ ("red" if border else "yellow") for point, border in _discovered ], marker="o")
        ngplot.pointsScatter(numpy.asarray(_edges), color="green", marker="o")

    return penalty * max([0] + _dists)
