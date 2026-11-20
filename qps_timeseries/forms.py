# coding=utf-8
""""
Forms module fo Qps_timeseries
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2023-12-04'
__copyright__ = 'Copyright 2015 - 2023, Gis3w'
__license__ = 'MPL 2.0'

from django.forms import ModelForm, CharField, Select, HiddenInput
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    Div,
    HTML,
    Row,
    Field,
    Hidden
)
from core.mixins.forms import (
    G3WRequestFormMixin,
    G3WFormMixin
)
from .models import (
    QpsTimeseriesProject,
    QpsTimeseriesLayer
)


class QpsTimeseriesProjectForm(G3WFormMixin, G3WRequestFormMixin, ModelForm):
    """
    Form for EleProProject model.
    """
    class Meta:
        model = QpsTimeseriesProject
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
                                Div(
                                    Div(
                                        Div(
                                            Div(
                                                HTML("<h3 class='box-title'><i class='fa fa-file'></i> {}</h3>".format(
                                                    _('Project'))),
                                                css_class='box-header with-border'
                                            ),
                                            Div(
                                                Field('project', css_class='select2'),
                                                Field('note', css_class='wys5'),
                                                css_class='box-body',
                                            ),
                                            css_class='box box-success'
                                        ),
                                        css_class='col-md-12'
                                    ),
                                    css_class='row'
                                ),
                            )


class QpsTimeseriesLayerForm(G3WFormMixin, G3WRequestFormMixin, ModelForm):

    title_part_1_field = CharField(widget=Select())
    title_part_2_field = CharField(widget=Select())
    title_part_3_field = CharField(widget=Select())
    qps_timeseries_project = CharField(widget=HiddenInput())

    def __init__(self, *args, **kwargs):

        self.qps_timeseries_project_instance = kwargs['qps_timeseries_project']
        del(kwargs['qps_timeseries_project'])

        super().__init__(*args, **kwargs)

        self.initial['qps_timeseries_project'] = self.qps_timeseries_project_instance.pk

        # Change layer queryset
        self.fields['layer'].queryset = self.qps_timeseries_project_instance.project.layer_set.all()

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
                                Div(

                                    Div(
                                        Div(
                                            Div(
                                                HTML(
                                                    "<h3 class='box-title'><i class='fa fa-file'></i> {}</h3>".format(
                                                        _('Layer'))),
                                                css_class='box-header with-border'
                                            ),
                                            Div(
                                                'qps_timeseries_project',
                                                Field('layer', css_class='select2'),
                                                Field('note', css_class='wys5'),
                                                css_class='box-body',
                                            ),
                                            css_class='box box-success'
                                        ),
                                        css_class='col-md-12'
                                    ),
                                css_class='row'
                                ),
                                Div(
                                    Div(
                                        Div(
                                            Div(
                                                HTML("<h3 class='box-title'><i class='fa fa-file'></i> {}</h3>".format(
                                                    _('Scale options'))),
                                                css_class='box-header with-border'
                                            ),
                                            Div(
                                                'min_date',
                                                'max_date',
                                                # Div(
                                                #     Div(
                                                #         'min_y', css_class='col-md-6'
                                                #         ),
                                                #         Div(
                                                #             'max_y', css_class='col-md-6'
                                                #         ),
                                                #     css_class='row'),
                                                css_class='box-body',
                                            ),
                                            css_class='box box-success'
                                        ),
                                        css_class='col-md-3'
                                    ),
                                    Div(
                                        Div(
                                            Div(
                                                HTML("<h3 class='box-title'><i class='fa fa-file'></i> {}</h3>".format(
                                                    _('Replica'))),
                                                css_class='box-header with-border'
                                            ),
                                            Div(
                                                Field('replica_up', css_class='checkbox'),
                                                'replica_dist',
                                                Field('replica_down', css_class='checkbox'),

                                                css_class='box-body',
                                            ),
                                            css_class='box box-success'
                                        ),
                                        css_class='col-md-3'
                                    ),
                                    Div(
                                        Div(
                                            Div(
                                                HTML("<h3 class='box-title'><i class='fa fa-file'></i> {}</h3>".format(
                                                    _('Chart options'))),
                                                css_class='box-header with-border'
                                            ),
                                            Div(
                                                Div(
                                                    Div(
                                                        Field('h_grid', css_class='checkbox'),
                                                            Field('v_grid', css_class='checkbox'),
                                                            Field('lines', css_class='checkbox'),
                                                            Field('labels', css_class='checkbox'),
                                                            css_class='col-md-6'
                                                        ),
                                                        Div(
                                                            Field('lin_trend', css_class='checkbox'),
                                                            Field('poly_trend', css_class='checkbox'),
                                                            Field('detrending', css_class='checkbox'),
                                                            Field('std', css_class='checkbox'),
                                                            css_class='col-md-6'
                                                        ),
                                                    css_class='row'
                                                ),

                                                css_class='box-body',
                                            ),
                                            css_class='box box-success'
                                        ),
                                        css_class='col-md-3'
                                    ),
                                    Div(
                                        Div(
                                            Div(
                                                HTML("<h3 class='box-title'><i class='fa fa-file'></i> {}</h3>".format(
                                                    _('Chart axislabels'))),
                                                css_class='box-header with-border'
                                            ),
                                            Div(
                                                'x_axis_label',
                                                'y_axis_label',
                                                css_class='box-body',
                                            ),
                                            css_class='box box-success'
                                        ),
                                        css_class='col-md-3'
                                    ),

                                    css_class='row'
                                ),
                                Div(
                                    Div(
                                        Div(
                                            Div(
                                                HTML("<h3 class='box-title'><i class='fa fa-file'></i> {}</h3>".format(
                                                    _('Chart title'))),
                                                css_class='box-header with-border'
                                            ),
                                            Div(
                                                Div(
                                                    Div(
                                                        'title_part_1',
                                                        'title_part_2',
                                                        'title_part_3',
                                                        css_class='col-md-6'
                                                    ),
                                                    Div(
                                                        'title_part_1_field',
                                                        'title_part_2_field',
                                                        'title_part_3_field',
                                                        css_class='col-md-6'
                                                    ),
                                                    css_class='row'
                                                ),
                                                css_class='box-body',
                                            ),
                                            css_class='box box-success'
                                        ),
                                        css_class='col-md-6'
                                    ),
                                    css_class='row'
                                )
                            )

    def clean_qps_timeseries_project(self):
        return self.qps_timeseries_project_instance

    class Meta:
        model = QpsTimeseriesLayer
        fields = '__all__'