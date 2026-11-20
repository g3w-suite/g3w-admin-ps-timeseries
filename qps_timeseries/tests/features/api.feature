@backend
Feature: Time series API
  Background:
    Given a time-series test project

  Scenario: Advertise the time-series plugin only when it is configured
    When an administrator checks the project configuration
    Then the time-series plugin is absent until enabled
    And its configuration identifies the project and layer

  Scenario: Restrict layer information to authenticated users
    When an anonymous visitor requests layer information
    Then the layer information request is forbidden
    When an administrator requests layer information
    Then the layer information includes the expected time series

  Scenario: Build plot data with configured ranges, replicas, trends, and layout
    When an anonymous visitor requests plot data
    Then the plot data request is forbidden
    When an administrator requests plot data without an active time-series project
    Then the plot data request is forbidden
    Given an administrator enables the time-series project
    When plot data is requested
    Then the default plot data is returned
    When the time range is restricted
    Then the plot contains the restricted date range
    When upper and lower replicas are enabled
    Then the plot includes both replicas
    When trend lines and standard deviation are enabled
    Then the plot includes trends and standard deviation
    When plot layout options are configured
    Then the configured plot labels and title are returned
