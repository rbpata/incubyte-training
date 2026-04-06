


class Email:
    def __init__(self, sender, recipient, subject, body):
        self.sender = sender
        self.recipient = recipient
        self.subject = subject
        self.body = body

    def __repr__(self):
        return f"Email(from={self.sender}, to={self.recipient}, subject={self.subject})"


class User:
    def __init__(self, email_address):
        self.email_address = email_address
        self.inbox = []

    def send_email(self, email, recipient):
        """Send an email to a recipient."""
        email.sender = self.email_address
        email.recipient = recipient.email_address
        recipient.inbox.append(email)

    def clear_mailbox(self):
        """Clear all emails from inbox."""
        self.inbox.clear()


class MailAdminClient:
    def __init__(self):
        self.emails = []
        self.users = []

    def send_email(self, email):
        """Send an email"""
        self.emails.append(email)
        return True

    def get_emails(self, recipient=None):
        """Get emails, optionally filtered by recipient"""
        if recipient:
            return [e for e in self.emails if e.recipient == recipient]
        return self.emails

    def clear_emails(self):
        """Clear all emails"""
        self.emails.clear()

    def create_user(self):
        """Create a new user"""
        user = User(f"user_{len(self.users)}@mail.com")
        self.users.append(user)
        return user

    def delete_user(self, user):
        """Delete a user"""
        if user in self.users:
            self.users.remove(user)
