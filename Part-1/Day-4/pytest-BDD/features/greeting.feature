Feature: Greeting users

  Scenario: Greeting a user
    Given a user named "Ram"
    When the greeting service greets the user
    Then the result should be "Hello, Ram!"