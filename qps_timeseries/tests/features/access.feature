@backend
Feature: Time series administration access

  Scenario: Anonymous visitors must log in before managing time series projects
    When an anonymous visitor opens the time series project list
    Then they are redirected to the login page
