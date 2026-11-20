from behave import then, when
from django.urls import reverse


@when('an anonymous visitor opens the time series project list')
def open_project_list(context):
    context.response = context.test.client.get(reverse('qpstimeseries-project-list'))


@then('they are redirected to the login page')
def check_login_redirect(context):
    assert context.response.status_code == 302
    assert '/login/' in context.response.headers['Location']
