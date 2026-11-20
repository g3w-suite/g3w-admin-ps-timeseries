import datetime

from behave import given, then, when
from django.urls import reverse

from qps_timeseries.tests.base import create_timeseries_project, setup_timeseries_test_project


@given('a time-series test project')
def timeseries_test_project(context):
    setup_timeseries_test_project(context)


@when('an administrator checks the project configuration')
def check_project_configuration(context):
    assert context.test.client.login(
        username=context.test.test_user1.username,
        password=context.test.test_user1.username,
    )
    context.config_url = reverse(
        'group-map-config',
        args=[context.project.group.slug, 'qdjango', context.project.pk],
    )
    context.initial_config = context.test.client.get(context.config_url).json()
    create_timeseries_project(context)
    context.enabled_config = context.test.client.get(context.config_url).json()
    context.plugin_config = context.enabled_config['group']['plugins']['qps_timeseries']


@then('the time-series plugin is absent until enabled')
def check_plugin_activation(context):
    assert 'qps_timeseries' not in context.initial_config['group']['plugins']
    assert 'qps_timeseries' in context.enabled_config['group']['plugins']


@then('its configuration identifies the project and layer')
def check_plugin_configuration(context):
    assert context.plugin_config['gid'] == 'qdjango:{}'.format(context.project.pk)
    assert len(context.plugin_config['layers']) == 1


@when('an anonymous visitor requests layer information')
def request_layer_info_anonymously(context):
    layer = context.project.layer_set.all()[0]
    context.layer_info_url = reverse('qpstimeseries-api-layerinfo', kwargs={'pk': layer.pk})
    context.response = context.test.client.get(context.layer_info_url)


@then('the layer information request is forbidden')
def check_layer_info_forbidden(context):
    assert context.response.status_code == 403


@when('an administrator requests layer information')
def request_layer_info_as_admin(context):
    assert context.test.client.login(
        username=context.test.test_user1.username,
        password=context.test.test_user1.username,
    )
    context.response = context.test.client.get(context.layer_info_url)
    context.layer_info = context.response.json()


@then('the layer information includes the expected time series')
def check_layer_info(context):
    assert context.response.status_code == 200
    assert context.layer_info['result']
    assert len(context.layer_info['x']) == 357
    assert len(context.layer_info['y']) == 357
    assert context.layer_info['fields'] == [
        'pid', 'cluster_la', 'mp_type', 'latitude', 'longitude', 'easting',
        'northing', 'height', 'height_wgs', 'line', 'pixel', 'rmse',
        'temporal_c', 'amplitude_', 'incidence_', 'track_angl', 'los_east',
        'los_north', 'los_up', 'mean_veloc', 'mean_vel_1', 'accelerati',
        'accelera_1', 'seasonalit', 'seasonal_1',
    ]


def _request_plot_data(context):
    context.response = context.test.client.get(context.plot_url)
    if context.response.status_code == 200:
        context.plot_data = context.response.json()


@when('an anonymous visitor requests plot data')
def request_plot_data_anonymously(context):
    layer = context.project.layer_set.all()[0]
    context.plot_url = reverse(
        'qpstimeseries-api-plot-data',
        kwargs={
            'project_pk': context.project.pk,
            'layer_id': layer.qgs_layer_id,
            'feature_id': 1,
        },
    )
    _request_plot_data(context)


@when('an administrator requests plot data without an active time-series project')
def request_plot_data_without_project(context):
    assert context.test.client.login(
        username=context.test.test_user1.username,
        password=context.test.test_user1.username,
    )
    _request_plot_data(context)


@then('the plot data request is forbidden')
def check_plot_data_forbidden(context):
    assert context.response.status_code == 403


@given('an administrator enables the time-series project')
def enable_timeseries_project(context):
    context.timeseries_project, context.timeseries_layer = create_timeseries_project(context)


@when('plot data is requested')
def request_plot_data(context):
    _request_plot_data(context)


@then('the default plot data is returned')
def check_default_plot_data(context):
    data = context.plot_data
    assert context.response.status_code == 200
    assert data['result']
    assert len(data['data'][0]['x']) == 357
    assert len(data['data'][0]['y']) == 357
    assert len(data['data'][1]['y']) == 0
    assert len(data['data'][2]['y']) == 0
    assert 'error_y' not in data['data'][0]
    assert data['config'] == {
        'displayModeBar': True,
        'editable': False,
        'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'resetScale2d'],
        'responsive': True,
        'scrollZoom': True,
        'toImageButtonOptions': {'filename': 'qps-timeseries'},
    }


@when('the time range is restricted')
def restrict_time_range(context):
    context.timeseries_layer.min_date = datetime.date(2015, 2, 8)
    context.timeseries_layer.max_date = datetime.date(2015, 5, 27)
    context.timeseries_layer.save()
    _request_plot_data(context)


@then('the plot contains the restricted date range')
def check_restricted_time_range(context):
    assert context.response.status_code == 200
    assert len(context.plot_data['data'][0]['x']) == 10
    assert len(context.plot_data['data'][0]['y']) == 10
    assert len(context.plot_data['data'][1]['y']) == 0
    assert len(context.plot_data['data'][2]['y']) == 0


@when('upper and lower replicas are enabled')
def enable_replicas(context):
    context.timeseries_layer.replica_up = True
    context.timeseries_layer.replica_down = True
    context.timeseries_layer.replica_dist = 10
    context.timeseries_layer.save()
    _request_plot_data(context)


@then('the plot includes both replicas')
def check_replicas(context):
    data = context.plot_data['data']
    assert context.response.status_code == 200
    assert len(data[0]['x']) == 10
    assert len(data[0]['y']) == 10
    assert len(data[1]['y']) == 10
    assert len(data[2]['y']) == 10
    for index, value in enumerate(data[0]['y']):
        assert data[1]['y'][index] == value + 10


@when('trend lines and standard deviation are enabled')
def enable_trends(context):
    context.timeseries_layer.lin_trend = True
    context.timeseries_layer.poly_trend = True
    context.timeseries_layer.std = True
    context.timeseries_layer.save()
    _request_plot_data(context)


@then('the plot includes trends and standard deviation')
def check_trends(context):
    data = context.plot_data['data']
    assert context.response.status_code == 200
    assert len(data[0]['x']) == 10
    assert len(data[0]['y']) == 10
    assert len(data[1]['y']) == 10
    assert len(data[2]['y']) == 10
    for series in data[3:5]:
        assert len(series['x']) == 10
        assert len(series['y']) == 10
    assert data[0]['error_y']['type'] == 'data'
    assert data[0]['error_y']['symmetric'] is True
    assert len(data[0]['error_y']['array']) == 10


@when('plot layout options are configured')
def configure_plot_layout(context):
    context.timeseries_layer.h_grid = True
    context.timeseries_layer.v_grid = True
    context.timeseries_layer.lines = True
    context.timeseries_layer.labels = True
    context.timeseries_layer.x_axis_label = 'Label x'
    context.timeseries_layer.y_axis_label = 'Label y'
    context.timeseries_layer.title_part_1_field = 'pid'
    context.timeseries_layer.title_part_2_field = 'pid'
    context.timeseries_layer.title_part_3_field = 'pid'
    context.timeseries_layer.save()
    _request_plot_data(context)


@then('the configured plot labels and title are returned')
def check_plot_layout(context):
    layout = context.plot_data['layout']
    assert context.response.status_code == 200
    assert layout['xaxis']['title'] == 'Label x'
    assert layout['xaxis']['showgrid']
    assert layout['yaxis']['title'] == 'Label y'
    assert layout['yaxis']['showgrid']
    assert layout['title']['text'] == 'coher.: 1ODQB00afP vel.: 1ODQB00afP v_stdev.: 1ODQB00afP '
