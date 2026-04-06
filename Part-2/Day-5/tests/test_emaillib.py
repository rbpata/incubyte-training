import pytest
from emaillib import Email, MailAdminClient

""" There’s also a more serious issue,
which is that if any of those steps in the setup raise an exception, 
none of the teardown code will run.

One option might be to go with the addfinalizer method instead of yield fixtures,
but that might get pretty complex and difficult to maintain (and it wouldn’t be compact anymore). """


@pytest.fixture
def mail_admin():
    """Fixture to create a MailAdminClient instance"""
    return MailAdminClient()


@pytest.fixture
def sending_user(mail_admin):
    """Fixture to provide a sending user email address"""
    user = mail_admin.create_user()
    yield user
    mail_admin.delete_user(user)


@pytest.fixture
def receiving_user(mail_admin, request):
    """Fixture to provide a receiving user email address"""

    def delete_user():
        mail_admin.delete_user(receiving_user)

    request.addfinalizer(delete_user)
    return mail_admin.create_user()


@pytest.fixture
def email(sending_user, receiving_user, request):
    """Fixture to create a sample email"""
    _email = Email(
        sender=sending_user.email_address,
        recipient=receiving_user.email_address,
        subject="Test Email",
        body="This is a test email.",
    )
    sending_user.send_email(_email, receiving_user)

    def clear_mailbox():
        receiving_user.clear_mailbox()

    request.addfinalizer(clear_mailbox)
    return _email


def test_email_received(receiving_user, email):
    """Test that the email is received in the recipient's inbox"""
    assert email in receiving_user.inbox
