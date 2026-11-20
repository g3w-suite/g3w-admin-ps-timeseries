# coding=utf-8
""""
    Base testing module
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2023-12-28'
__copyright__ = 'Copyright 2015 - 2023, Gis3w'
__license__ = 'MPL 2.0'

import datetime
import os

from django.core.management import call_command
from django.core.files import File
from core.models import G3WSpatialRefSys, Group as CoreGroup
from usersmanage.tests.utils import setup_testing_user
from qdjango.utils.data import QgisProject
from qps_timeseries.models import (
    QpsTimeseriesProject,
    QpsTimeseriesLayer
)

CURRENT_PATH = os.path.dirname(__file__)
TEST_BASE_PATH = 'data/'
DATASOURCE_PATH = '{}/{}project_data'.format(CURRENT_PATH, TEST_BASE_PATH)

QGS_PROJECT_FILE = 'projects/qps_timeseries.qgs'

FIXTURES = [
    'BaseLayer.json',
    'G3WMapControls.json',
    'G3WSpatialRefSys.json',
    'G3WGeneralDataSuite.json',
]


def setup_timeseries_test_project(context):
    call_command('loaddata', *FIXTURES, verbosity=0)
    setup_testing_user(context.test)

    group = CoreGroup.objects.create(
        name='QProcessing',
        title='QProcessing',
        header_logo_img='',
        srid=G3WSpatialRefSys.objects.get(auth_srid=4326),
    )
    project_path = os.path.join(CURRENT_PATH, TEST_BASE_PATH, QGS_PROJECT_FILE)
    with open(project_path, 'r') as project_file:
        project = QgisProject(File(project_file))
        project.title = 'Qps Timeseries Test Project'
        project.group = group
        project.save()
    context.project = project.instance


def create_timeseries_project(context):
    timeseries_project = QpsTimeseriesProject(project=context.project)
    timeseries_project.save()
    layer = QpsTimeseriesLayer(
        qps_timeseries_project=timeseries_project,
        layer=context.project.layer_set.all()[0],
        min_date=datetime.date(2015, 2, 8),
        max_date=datetime.date(2021, 12, 21),
    )
    layer.save()
    return timeseries_project, layer