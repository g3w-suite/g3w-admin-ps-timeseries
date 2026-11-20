from sitetree.utils import item
from core.utils.tree import G3Wtree

sitetrees = (

  G3Wtree(
        'qps_timeseries',
        title='PS TIMESERIES',
        module='qps_timeseries',
        items=[
            item(
                'Permanent scatters',
                'qpstimeseries-project-list',
                icon_css_class='fa fa-area-chart',
                url_as_pattern=True,
                children=[
                    item(
                        'Aggiungi progetto',
                        'qpstimeseries-project-add',
                        url_as_pattern=True,
                        in_menu=False,
                        access_by_perms=['qps_timeseries.add_qpstimeseriesproject'],
                    ),
                    item(
                        'Agg. progetto {{ object.project.title }}',
                        'qpstimeseries-project-update object.pk',
                        url_as_pattern=True,
                        in_menu=False,
                        alias='qpstimeseries-project-update',
                    ),
                ]
            ),
        ]
    ),

  G3Wtree(
        'qps_timeseries_en',
        title='PS TIMSERIES',
        module='qps_timeseries',
        items=[
            item(
                'Permanent scatters',
                'qpstimeseries-project-list',
                icon_css_class='fa fa-area-chart',
                children=[
                    item(
                        'Add project',
                        'qpstimeseries-project-add',
                        url_as_pattern=True,
                        in_menu=False,
                        access_by_perms=['qps_timeseries.add_qpstimeseriesproject']
                    ),
                    item(
                        'Update project {{ object.project.title }}',
                        'qpstimeseries-project-update object.pk',
                        url_as_pattern=True,
                        in_menu=False,
                        alias='qpstimeseries-project-update'
                    ),
                ]
            ),
        ]
    ),

)